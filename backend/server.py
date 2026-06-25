from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import sqlite3
import os
import csv
import io
from datetime import date, datetime

# ---------- CONFIG ----------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campaigns.db")

# ---------- APP SETUP ----------
app = FastAPI(title="Stratis Marketing Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CURRENCY CONVERSION (approximate, static) ----------
CONVERSION_TO_USD = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
}

# ---------- DATA MODELS ----------
class CampaignSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    budget: float = Field(..., gt=0, description="Budget must be greater than 0")
    spent: float = Field(0.0, ge=0, description="Amount already spent")
    currency: Literal["USD", "EUR", "GBP"] = "USD"
    start_date: str
    end_date: Optional[str] = None
    target_audience: Optional[str] = None
    status: Literal["Draft", "Active", "Paused", "Completed"] = "Draft"
    owner: Optional[str] = None
    tags: Optional[List[str]] = None
    assets: Optional[str] = None  # links / files description
    notes: Optional[str] = None

class CampaignResponse(CampaignSchema):
    id: int
    budget_usd: float
    is_expired: bool
    remaining: float
    progress_pct: float

class DashboardStats(BaseModel):
    active_budget_usd: float
    total_budget_usd: float
    total_spent_usd: float
    counts_by_status: dict
    expired_count: int

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        budget REAL NOT NULL,
        spent REAL DEFAULT 0,
        currency TEXT DEFAULT 'USD',
        start_date TEXT NOT NULL,
        end_date TEXT,
        target_audience TEXT,
        status TEXT DEFAULT 'Draft',
        owner TEXT,
        tags TEXT,
        assets TEXT,
        notes TEXT
    )''')

    c.execute("PRAGMA table_info(campaigns)")
    cols = [row[1] for row in c.fetchall()]

    def add_col(name, ddl):
        if name not in cols:
            c.execute(f"ALTER TABLE campaigns ADD COLUMN {ddl}")

    add_col("spent", "spent REAL DEFAULT 0")
    add_col("owner", "owner TEXT")
    add_col("tags", "tags TEXT")
    add_col("assets", "assets TEXT")
    add_col("notes", "notes TEXT")

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------- HELPERS ----------
def _parse_tags(raw: Optional[str]) -> Optional[List[str]]:
    if not raw:
        return None
    return [t.strip() for t in raw.split(",") if t.strip()]

def _serialize_tags(tags: Optional[List[str]]) -> Optional[str]:
    if not tags:
        return None
    return ", ".join(tags)

def enrich_campaign(row: dict) -> dict:
    rate = CONVERSION_TO_USD.get(row.get("currency", "USD"), 1.0)
    row["budget_usd"] = round(row["budget"] * rate, 2)

    end_date = row.get("end_date")
    if end_date:
        try:
            row["is_expired"] = datetime.strptime(end_date, "%Y-%m-%d").date() < date.today()
        except ValueError:
            row["is_expired"] = False
    else:
        row["is_expired"] = False

    spent = float(row.get("spent") or 0.0)
    remaining = max(row["budget"] - spent, 0.0)
    row["remaining"] = round(remaining, 2)
    row["progress_pct"] = round(min(spent / row["budget"] * 100, 100), 1) if row["budget"] > 0 else 0.0

    row["tags"] = _parse_tags(row.get("tags"))
    return row

def auto_update_expired_statuses(db: sqlite3.Connection):
    today = date.today().isoformat()
    c = db.cursor()
    c.execute(
        "UPDATE campaigns SET status = 'Completed' "
        "WHERE (status = 'Active' OR status = 'Paused') "
        "AND end_date IS NOT NULL AND end_date < ?",
        (today,)
    )
    db.commit()

# ---------- ROUTES ----------
@app.get("/", tags=["Root"])
def root():
    return {"message": "Stratis API Engine Operating Nominally."}

@app.get("/campaigns/stats", response_model=DashboardStats, tags=["Dashboard"])
def get_stats(db: sqlite3.Connection = Depends(get_db)):
    auto_update_expired_statuses(db)
    c = db.cursor()
    c.execute("SELECT * FROM campaigns")
    rows = [dict(r) for r in c.fetchall()]

    active_usd = 0.0
    total_usd = 0.0
    total_spent_usd = 0.0
    counts = {"Draft": 0, "Active": 0, "Paused": 0, "Completed": 0}
    expired_count = 0

    for row in rows:
        enriched = enrich_campaign(dict(row))
        total_usd += enriched["budget_usd"]
        total_spent_usd += enriched["spent"] * CONVERSION_TO_USD.get(enriched["currency"], 1.0)
        status = enriched["status"]
        if status in counts:
            counts[status] += 1
        if status == "Active":
            active_usd += enriched["budget_usd"]
        if enriched["is_expired"] and status != "Completed":
            expired_count += 1

    return DashboardStats(
        active_budget_usd=round(active_usd, 2),
        total_budget_usd=round(total_usd, 2),
        total_spent_usd=round(total_spent_usd, 2),
        counts_by_status=counts,
        expired_count=expired_count,
    )

@app.get("/campaigns/export", tags=["Export"])
def export_campaigns_csv(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM campaigns ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "name", "description", "budget", "spent", "currency",
        "start_date", "end_date", "target_audience", "status",
        "owner", "tags", "assets", "notes"
    ])
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in writer.fieldnames})

    output.seek(0)
    filename = f"stratis_campaigns_{date.today().isoformat()}.csv"

    def iter_csv():
        yield output.getvalue()

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/campaigns", response_model=List[CampaignResponse], tags=["Campaigns"])
def get_all_campaigns(db: sqlite3.Connection = Depends(get_db)):
    auto_update_expired_statuses(db)
    c = db.cursor()
    c.execute("SELECT * FROM campaigns ORDER BY start_date ASC, id DESC")
    rows = c.fetchall()
    return [enrich_campaign(dict(row)) for row in rows]

@app.get("/campaigns/{id}", response_model=CampaignResponse, tags=["Campaigns"])
def get_one_campaign(id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM campaigns WHERE id = ?", (id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return enrich_campaign(dict(row))

@app.post("/campaigns", response_model=CampaignResponse, status_code=201, tags=["Campaigns"])
def create_campaign(campaign: CampaignSchema, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    tags_str = _serialize_tags(campaign.tags)
    c.execute('''INSERT INTO campaigns
        (name, description, budget, spent, currency, start_date, end_date,
         target_audience, status, owner, tags, assets, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (campaign.name, campaign.description, campaign.budget, campaign.spent,
         campaign.currency, campaign.start_date, campaign.end_date,
         campaign.target_audience, campaign.status, campaign.owner,
         tags_str, campaign.assets, campaign.notes))
    db.commit()
    new_id = c.lastrowid
    c.execute("SELECT * FROM campaigns WHERE id = ?", (new_id,))
    return enrich_campaign(dict(c.fetchone()))

@app.post("/campaigns/{id}/duplicate", response_model=CampaignResponse, status_code=201, tags=["Campaigns"])
def duplicate_campaign(id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM campaigns WHERE id = ?", (id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    orig = dict(row)
    c.execute('''INSERT INTO campaigns
        (name, description, budget, spent, currency, start_date, end_date,
         target_audience, status, owner, tags, assets, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (f"{orig['name']} (Copy)", orig["description"], orig["budget"], 0.0,
         orig["currency"], orig["start_date"], orig["end_date"],
         orig["target_audience"], "Draft", orig.get("owner"),
         orig.get("tags"), orig.get("assets"), orig.get("notes")))
    db.commit()
    new_id = c.lastrowid
    c.execute("SELECT * FROM campaigns WHERE id = ?", (new_id,))
    return enrich_campaign(dict(c.fetchone()))

@app.put("/campaigns/{id}", response_model=CampaignResponse, tags=["Campaigns"])
def update_campaign(id: int, campaign: CampaignSchema, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM campaigns WHERE id = ?", (id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Campaign not found")
    tags_str = _serialize_tags(campaign.tags)
    c.execute('''UPDATE campaigns SET
        name=?, description=?, budget=?, spent=?, currency=?, start_date=?, end_date=?,
        target_audience=?, status=?, owner=?, tags=?, assets=?, notes=?
        WHERE id = ?''',
        (campaign.name, campaign.description, campaign.budget, campaign.spent,
         campaign.currency, campaign.start_date, campaign.end_date,
         campaign.target_audience, campaign.status, campaign.owner,
         tags_str, campaign.assets, campaign.notes, id))
    db.commit()
    c.execute("SELECT * FROM campaigns WHERE id = ?", (id,))
    return enrich_campaign(dict(c.fetchone()))

@app.delete("/campaigns/{id}", status_code=204, tags=["Campaigns"])
def delete_campaign(id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM campaigns WHERE id = ?", (id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Campaign not found")
    c.execute("DELETE FROM campaigns WHERE id = ?", (id,))
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
