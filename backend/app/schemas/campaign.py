"""Campaign Pydantic schemas for validation."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from ..models.enums import CampaignStatus, Currency


class CampaignBase(BaseModel):
    """Base campaign schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    budget: float = Field(..., gt=0)
    spent: float = Field(0.0, ge=0)
    currency: Currency = Currency.USD
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    target_audience: Optional[str] = Field(None, max_length=500)
    status: CampaignStatus = CampaignStatus.DRAFT
    owner: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, max_length=20)
    assets: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator("end_date")
    def validate_end_date(cls, v, values):
        if v and "start_date" in values:
            start = datetime.strptime(values["start_date"], "%Y-%m-%d").date()
            end = datetime.strptime(v, "%Y-%m-%d").date()
            if end < start:
                raise ValueError("End date must be after start date")
        return v
    
    @validator("budget")
    def validate_budget(cls, v):
        if v > 1_000_000_000:
            raise ValueError("Budget too large (max 1 billion)")
        return v
    
    @validator("spent")
    def validate_spent(cls, v, values):
        if "budget" in values and v > values["budget"]:
            raise ValueError("Spent cannot exceed budget")
        return v


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    budget: Optional[float] = Field(None, gt=0)
    spent: Optional[float] = Field(None, ge=0)
    currency: Optional[Currency] = None
    start_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    target_audience: Optional[str] = Field(None, max_length=500)
    status: Optional[CampaignStatus] = None
    owner: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, max_length=20)
    assets: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator("end_date")
    def validate_end_date(cls, v, values):
        if v and "start_date" in values and values["start_date"]:
            start = datetime.strptime(values["start_date"], "%Y-%m-%d").date()
            end = datetime.strptime(v, "%Y-%m-%d").date()
            if end < start:
                raise ValueError("End date must be after start date")
        return v


class CampaignResponse(CampaignBase):
    id: int
    budget_usd: float
    is_expired: bool
    remaining: float
    progress_pct: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class CampaignFilters(BaseModel):
    status: Optional[CampaignStatus] = None
    search: Optional[str] = Field(None, max_length=100)
    sort_by: str = "start_date"
    sort_order: str = "ASC"
    owner: Optional[str] = None
    start_date_from: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_date_to: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
