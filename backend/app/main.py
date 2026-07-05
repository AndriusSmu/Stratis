print("=== LOADING MAIN.PY v5 (fix auth for CSV) ===")

import logging
import csv
import io
from datetime import date
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer

from .config import config
from .routers import auth, campaigns, ai, dashboard, analytics
from .exceptions.handlers import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    ai_exception_handler,
)
from .exceptions import AIError
from .database import get_db, DatabaseConnection, CampaignRepository
from .services import CampaignService, AuthService
from .models import User

# Import UserRepository for auth
from .database.repositories import UserRepository

logging.basicConfig(
    level=logging.INFO if not config.api.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Reuse the same OAuth2 scheme as auth router
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_campaign_service(
    db: DatabaseConnection = Depends(get_db)
) -> CampaignService:
    repository = CampaignRepository(db)
    return CampaignService(repository)

app = FastAPI(
    title="Stratis Marketing Engine",
    description="Marketing campaign management with AI capabilities",
    version="2.0.0",
    debug=config.api.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(AIError, ai_exception_handler)

api_prefix = config.api.prefix

app.include_router(auth.router, prefix=api_prefix)
app.include_router(campaigns.router, prefix=api_prefix)
app.include_router(ai.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)

# Test route
@app.get("/ping")
async def ping():
    return {"message": "pong"}

# CSV export with explicit auth (same as /auth/me)
@app.get("/export/csv", response_class=StreamingResponse)
async def export_csv(
    token: str = Depends(oauth2_scheme),
    service: CampaignService = Depends(get_campaign_service),
    db: DatabaseConnection = Depends(get_db),
):
    # Authenticate user manually (same as /auth/me)
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    current_user = auth_service.get_current_user(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    campaigns = service.get_all(current_user.id)
    output = io.StringIO()
    fieldnames = ["id", "name", "description", "budget", "spent", "currency",
                  "start_date", "end_date", "target_audience", "status",
                  "owner", "tags", "assets", "notes", "created_at", "updated_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for campaign in campaigns:
        row = campaign.to_dict()
        if row.get("tags"):
            row["tags"] = ", ".join(campaign.tags) if campaign.tags else ""
        writer.writerow(row)
    output.seek(0)
    filename = f"stratis_campaigns_{date.today().isoformat()}.csv"
    async def iter_csv():
        yield output.getvalue()
    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/")
async def root():
    return {
        "message": "Stratis API Engine Operating Nominally.",
        "version": "2.0.0",
        "environment": config.api.environment,
    }

print("=== Registered routes ===")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"  {route.path}")