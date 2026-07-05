"""
Campaign CRUD routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from ..database import get_db, DatabaseConnection, CampaignRepository
from ..services import CampaignService
from ..schemas import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignFilters
from ..exceptions import NotFoundError, ValidationError
from ..middleware.auth import require_auth
from ..models import User

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


def get_campaign_service(
    db: DatabaseConnection = Depends(get_db)
) -> CampaignService:
    repository = CampaignRepository(db)
    return CampaignService(repository)


@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    current_user: User = Depends(require_auth()),
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "start_date",
    sort_order: str = "ASC",
    service: CampaignService = Depends(get_campaign_service),
):
    filters = CampaignFilters(
        status=status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    try:
        campaigns = service.get_all(current_user.id, filters)
        return [service.to_response(c) for c in campaigns]
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(require_auth()),
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        campaign = service.get_by_id(campaign_id, current_user.id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        return service.to_response(campaign)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(require_auth()),
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        created = service.create(current_user.id, campaign)
        return service.to_response(created)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign: CampaignUpdate,
    current_user: User = Depends(require_auth()),
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        updated = service.update(campaign_id, current_user.id, campaign)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        return service.to_response(updated)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(require_auth()),
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        deleted = service.delete(campaign_id, current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{campaign_id}/duplicate", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_campaign(
    campaign_id: int,
    current_user: User = Depends(require_auth()),
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        duplicated = service.duplicate(campaign_id, current_user.id)
        if not duplicated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        return service.to_response(duplicated)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
