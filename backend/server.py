from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3

# Updated Application branding to Stratis
app = FastAPI(title="🎯 Stratis Marketing Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DATA VALIDATION (PYDANTIC) ----------
class CampaignSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    budget: float = Field(..., gt=0, description="Budget must be greater than 0")
    currency: str = "USD"
    start_date: str
    end_date: Optional[str] = None
    target_audience: Optional[str] = None
    status: str = "Draft"

class CampaignResponse(CampaignSchema):
    id: int

# ---------- DATABASE INITIALIZATION ----------
def init_db():
    conn = sqlite3.connect('campaigns.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        budget REAL NOT NULL,
        currency TEXT DEFAULT 'USD',
        start_date TEXT NOT NULL,
        end_date TEXT,
        target_audience TEXT,
        status TEXT DEFAULT 'Draft'
    )''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('campaigns.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ---------- API ROUTES ----------

@app.get("/", tags=["Root"])
def root():
    return {'message': 'Stratis API Engine Operating Nominally.'}

@app.get("/campaigns", response_model=List[CampaignResponse], tags=["Campaigns"])
def get_all_campaigns(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute('SELECT * FROM campaigns ORDER BY id DESC')
    rows = c.fetchall()
    return [dict(row) for row in rows]

@app.get("/campaigns/{id}", response_model=CampaignResponse, tags=["Campaigns"])
def get_one_campaign(id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute('SELECT * FROM campaigns WHERE id = ?', (id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return dict(row)

@app.post("/campaigns", response_model=CampaignResponse, status_code=201, tags=["Campaigns"])
def create_campaign(campaign: CampaignSchema, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute('''INSERT INTO campaigns 
        (name, description, budget, currency, start_date, end_date, target_audience, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (campaign.name, campaign.description, campaign.budget, campaign.currency,
         campaign.start_date, campaign.end_date, campaign.target_audience, campaign.status))
    db.commit()
    
    new_id = c.lastrowid
    c.execute('SELECT * FROM campaigns WHERE id = ?', (new_id,))
    return dict(c.fetchone())

@app.put("/campaigns/{id}", response_model=CampaignResponse, tags=["Campaigns"])
def update_campaign(id: int, campaign: CampaignSchema, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute('SELECT * FROM campaigns WHERE id = ?', (id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    c.execute('''UPDATE campaigns SET 
        name=?, description=?, budget=?, currency=?, start_date=?, end_date=?, target_audience=?, status=?
        WHERE id = ?''',
        (campaign.name, campaign.description, campaign.budget, campaign.currency,
         campaign.start_date, campaign.end_date, campaign.target_audience, campaign.status, id))
    db.commit()
    
    c.execute('SELECT * FROM campaigns WHERE id = ?', (id,))
    return dict(c.fetchone())

@app.delete("/campaigns/{id}", status_code=204, tags=["Campaigns"])
def delete_campaign(id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute('SELECT * FROM campaigns WHERE id = ?', (id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    c.execute('DELETE FROM campaigns WHERE id = ?', (id,))
    db.commit()
    return None

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)