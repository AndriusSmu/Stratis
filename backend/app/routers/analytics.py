"""Analytics routes."""

from fastapi import APIRouter, Depends

from ..database import get_db, DatabaseConnection, CampaignRepository
from ..services import AnalyticsService
from ..middleware.auth import require_auth
from ..models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(db: DatabaseConnection = Depends(get_db)) -> AnalyticsService:
    repository = CampaignRepository(db)
    return AnalyticsService(repository)


@router.get("/stats")
async def get_analytics(
    current_user: User = Depends(require_auth()),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_analytics(current_user.id)
