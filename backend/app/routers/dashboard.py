"""Dashboard routes."""

from fastapi import APIRouter, Depends

from ..database import get_db, DatabaseConnection, CampaignRepository
from ..services import DashboardService
from ..schemas import DashboardStats
from ..middleware.auth import require_auth
from ..models import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(
    db: DatabaseConnection = Depends(get_db)
) -> DashboardService:
    repository = CampaignRepository(db)
    return DashboardService(repository)


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(require_auth()),
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.get_stats(current_user.id)
