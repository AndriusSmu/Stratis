"""Campaign ORM model."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Dict, Any

from .enums import CampaignStatus, Currency


@dataclass
class Campaign:
    """Campaign domain model."""
    
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    budget: float = 0.0
    spent: float = 0.0
    currency: Currency = Currency.USD
    start_date: str = ""
    end_date: Optional[str] = None
    target_audience: Optional[str] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    owner: Optional[str] = None
    tags: Optional[List[str]] = None
    assets: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "budget": self.budget,
            "spent": self.spent,
            "currency": self.currency.value if self.currency else "USD",
            "start_date": self.start_date,
            "end_date": self.end_date,
            "target_audience": self.target_audience,
            "status": self.status.value if self.status else "Draft",
            "owner": self.owner,
            "tags": ",".join(self.tags) if self.tags else None,
            "assets": self.assets,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        tags = data.get("tags")
        if isinstance(tags, str) and tags:
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        elif not tags:
            tags = None
            
        status = data.get("status")
        if isinstance(status, str):
            status = CampaignStatus(status)
        
        currency = data.get("currency")
        if isinstance(currency, str):
            currency = Currency(currency)
        
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description"),
            budget=data.get("budget", 0.0),
            spent=data.get("spent", 0.0),
            currency=currency or Currency.USD,
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date"),
            target_audience=data.get("target_audience"),
            status=status or CampaignStatus.DRAFT,
            owner=data.get("owner"),
            tags=tags,
            assets=data.get("assets"),
            notes=data.get("notes"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @property
    def is_expired(self) -> bool:
        if not self.end_date:
            return False
        try:
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            return end < date.today() and self.status != CampaignStatus.COMPLETED
        except ValueError:
            return False
    
    @property
    def remaining(self) -> float:
        return max(self.budget - self.spent, 0.0)
    
    @property
    def progress_pct(self) -> float:
        if self.budget <= 0:
            return 0.0
        return min((self.spent / self.budget) * 100, 100.0)
