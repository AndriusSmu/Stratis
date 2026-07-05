"""
Campaign business logic service.
"""

from typing import List, Optional
from ..models import Campaign
from ..database.repositories import CampaignRepository
from ..schemas import CampaignCreate, CampaignUpdate, CampaignFilters
from ..exceptions import NotFoundError, ValidationError


class CampaignService:
    """Service for campaign business logic."""
    
    def __init__(self, repository: CampaignRepository):
        self.repository = repository
    
    def get_all(self, user_id: int, filters: Optional[CampaignFilters] = None) -> List[Campaign]:
        if filters:
            return self.repository.get_all(
                user_id=user_id,
                status=filters.status.value if filters.status else None,
                search=filters.search,
                sort_by=filters.sort_by,
                sort_order=filters.sort_order,
            )
        return self.repository.get_all(user_id=user_id)
    
    def get_by_id(self, campaign_id: int, user_id: int) -> Optional[Campaign]:
        return self.repository.get_by_id(campaign_id, user_id)
    
    def create(self, user_id: int, campaign_data: CampaignCreate) -> Campaign:
        if campaign_data.start_date and campaign_data.end_date:
            from datetime import datetime
            start = datetime.strptime(campaign_data.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(campaign_data.end_date, "%Y-%m-%d").date()
            if end < start:
                raise ValidationError("End date must be after start date")
        
        if campaign_data.spent > campaign_data.budget:
            raise ValidationError("Spent cannot exceed budget")
        
        campaign = Campaign(
            name=campaign_data.name,
            description=campaign_data.description,
            budget=campaign_data.budget,
            spent=campaign_data.spent,
            currency=campaign_data.currency,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            target_audience=campaign_data.target_audience,
            status=campaign_data.status,
            owner=campaign_data.owner,
            tags=campaign_data.tags,
            assets=campaign_data.assets,
            notes=campaign_data.notes,
        )
        
        return self.repository.create(campaign, user_id)
    
    def update(self, campaign_id: int, user_id: int, campaign_data: CampaignUpdate) -> Optional[Campaign]:
        existing = self.repository.get_by_id(campaign_id, user_id)
        if not existing:
            return None
        
        update_dict = {
            "name": campaign_data.name or existing.name,
            "description": campaign_data.description if campaign_data.description is not None else existing.description,
            "budget": campaign_data.budget or existing.budget,
            "spent": campaign_data.spent if campaign_data.spent is not None else existing.spent,
            "currency": campaign_data.currency or existing.currency,
            "start_date": campaign_data.start_date or existing.start_date,
            "end_date": campaign_data.end_date if campaign_data.end_date is not None else existing.end_date,
            "target_audience": campaign_data.target_audience if campaign_data.target_audience is not None else existing.target_audience,
            "status": campaign_data.status or existing.status,
            "owner": campaign_data.owner if campaign_data.owner is not None else existing.owner,
            "tags": campaign_data.tags if campaign_data.tags is not None else existing.tags,
            "assets": campaign_data.assets if campaign_data.assets is not None else existing.assets,
            "notes": campaign_data.notes if campaign_data.notes is not None else existing.notes,
        }
        
        if update_dict["start_date"] and update_dict["end_date"]:
            from datetime import datetime
            start = datetime.strptime(update_dict["start_date"], "%Y-%m-%d").date()
            end = datetime.strptime(update_dict["end_date"], "%Y-%m-%d").date()
            if end < start:
                raise ValidationError("End date must be after start date")
        
        if update_dict["spent"] > update_dict["budget"]:
            raise ValidationError("Spent cannot exceed budget")
        
        updated_campaign = Campaign(**update_dict)
        return self.repository.update(campaign_id, user_id, updated_campaign)
    
    def delete(self, campaign_id: int, user_id: int) -> bool:
        existing = self.repository.get_by_id(campaign_id, user_id)
        if not existing:
            return False
        return self.repository.delete(campaign_id, user_id)
    
    def duplicate(self, campaign_id: int, user_id: int) -> Optional[Campaign]:
        return self.repository.duplicate(campaign_id, user_id)
    
    def to_response(self, campaign: Campaign) -> dict:
        from .currency_service import CurrencyService
        
        currency_service = CurrencyService()
        
        return {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "budget": campaign.budget,
            "spent": campaign.spent,
            "currency": campaign.currency.value,
            "budget_usd": currency_service.to_usd(campaign.budget, campaign.currency),
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "target_audience": campaign.target_audience,
            "status": campaign.status.value,
            "owner": campaign.owner,
            "tags": campaign.tags,
            "assets": campaign.assets,
            "notes": campaign.notes,
            "is_expired": campaign.is_expired,
            "remaining": campaign.remaining,
            "progress_pct": campaign.progress_pct,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
        }
