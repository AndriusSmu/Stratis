"""AI-related Pydantic schemas."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BriefRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_audience: Optional[str] = Field(None, max_length=500)
    budget: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field("USD", pattern=r"^(USD|EUR|GBP)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Q4 Product Launch",
                "target_audience": "Tech-savvy professionals aged 25-40",
                "budget": 50000,
                "currency": "USD"
            }
        }


class BriefResponse(BaseModel):
    description: str
    tags: List[str]
    notes: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Q4 Product Launch campaign targeting tech-savvy professionals.",
                "tags": ["product-launch", "q4-2024", "professional"],
                "notes": "Key metrics: 25% increase in brand awareness, 15% conversion rate."
            }
        }


class InsightsRequest(BaseModel):
    campaigns: List[Dict[str, Any]] = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaigns": [
                    {
                        "name": "Q4 Product Launch",
                        "status": "Active",
                        "budget": 50000,
                        "spent": 25000,
                        "progress_pct": 50.0,
                        "is_expired": False
                    }
                ]
            }
        }


class InsightsResponse(BaseModel):
    insights: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "insights": "Portfolio is healthy with 3 active campaigns. One campaign is approaching 90% spend. Recommend reallocating budget from underperforming channels."
            }
        }
