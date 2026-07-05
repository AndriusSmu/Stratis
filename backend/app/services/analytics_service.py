"""Analytics service."""

from typing import Dict, Any
from ..database.repositories import CampaignRepository
from ..services.currency_service import CurrencyService


class AnalyticsService:
    """Service for campaign analytics."""
    
    def __init__(self, repository: CampaignRepository):
        self.repository = repository
        self.currency_service = CurrencyService()
    
    def get_analytics(self, user_id: int) -> Dict[str, Any]:
        campaigns = self.repository.get_all(user_id=user_id)
        
        total_budget = 0.0
        active_budget = 0.0
        completed_budget = 0.0
        total_spent = 0.0
        total_remaining = 0.0
        status_counts = {"Draft": 0, "Active": 0, "Paused": 0, "Completed": 0}
        
        for campaign in campaigns:
            budget_usd = self.currency_service.to_usd(campaign.budget, campaign.currency)
            spent_usd = self.currency_service.to_usd(campaign.spent, campaign.currency)
            
            total_budget += budget_usd
            total_spent += spent_usd
            total_remaining += campaign.remaining
            
            if campaign.status.value == "Active":
                active_budget += budget_usd
            elif campaign.status.value == "Completed":
                completed_budget += budget_usd
            
            status_counts[campaign.status.value] = status_counts.get(campaign.status.value, 0) + 1
        
        avg_budget = total_budget / len(campaigns) if campaigns else 0
        utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        budget_by_status = {}
        for campaign in campaigns:
            status = campaign.status.value
            budget_usd = self.currency_service.to_usd(campaign.budget, campaign.currency)
            budget_by_status[status] = budget_by_status.get(status, 0) + budget_usd
        
        return {
            "total_budget_usd": round(total_budget, 2),
            "active_budget_usd": round(active_budget, 2),
            "completed_budget_usd": round(completed_budget, 2),
            "total_spent_usd": round(total_spent, 2),
            "total_remaining_usd": round(total_remaining, 2),
            "average_budget_usd": round(avg_budget, 2),
            "budget_utilization_pct": round(utilization, 1),
            "campaign_count": len(campaigns),
            "status_counts": status_counts,
            "budget_by_status": {k: round(v, 2) for k, v in budget_by_status.items()},
        }
