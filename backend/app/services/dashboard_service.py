"""
Dashboard service for campaign statistics.
"""

from ..database.repositories import CampaignRepository
from ..schemas import DashboardStats


class DashboardService:
    """Service for dashboard statistics."""
    
    def __init__(self, repository: CampaignRepository):
        self.repository = repository
    
    def get_stats(self, user_id: int) -> DashboardStats:
        stats = self.repository.get_stats(user_id)
        
        return DashboardStats(
            active_budget_usd=round(stats["active_budget_usd"], 2),
            total_budget_usd=round(stats["total_budget_usd"], 2),
            total_spent_usd=round(stats["total_spent_usd"], 2),
            counts_by_status=stats["by_status"],
            expired_count=stats["expired_count"],
            total_campaigns=stats["total"],
        )
