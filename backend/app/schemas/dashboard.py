"""Dashboard Pydantic schemas."""

from typing import Dict
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    active_budget_usd: float = Field(..., description="Total active budget in USD")
    total_budget_usd: float = Field(..., description="Total budget across all campaigns in USD")
    total_spent_usd: float = Field(..., description="Total spent across all campaigns in USD")
    counts_by_status: Dict[str, int] = Field(..., description="Campaign counts by status")
    expired_count: int = Field(..., description="Number of expired campaigns")
    total_campaigns: int = Field(..., description="Total number of campaigns")
    
    class Config:
        json_schema_extra = {
            "example": {
                "active_budget_usd": 125000.00,
                "total_budget_usd": 250000.00,
                "total_spent_usd": 75000.00,
                "counts_by_status": {
                    "Draft": 2,
                    "Active": 3,
                    "Paused": 1,
                    "Completed": 4
                },
                "expired_count": 1,
                "total_campaigns": 10
            }
        }
