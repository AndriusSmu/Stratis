"""
Repository pattern for campaign data access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date

from .connection import DatabaseConnection
from ..models import Campaign, CampaignStatus, User


class CampaignRepository:
    """Repository for campaign CRUD operations."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def _row_to_campaign(self, row: Dict[str, Any]) -> Campaign:
        return Campaign.from_dict(dict(row))
    
    def get_all(
        self, 
        user_id: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "start_date",
        sort_order: str = "ASC"
    ) -> List[Campaign]:
        query = "SELECT * FROM campaigns WHERE user_id = ?"
        params = [user_id]
        
        self._auto_complete_expired(user_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if search:
            query += """ AND (name LIKE ? OR description LIKE ? OR target_audience LIKE ? OR notes LIKE ? OR owner LIKE ? OR tags LIKE ?)"""
            search_pattern = f"%{search}%"
            params.extend([search_pattern] * 6)
        
        valid_sort_columns = {"id", "name", "budget", "spent", "start_date", "end_date", "status", "owner", "created_at", "updated_at"}
        if sort_by not in valid_sort_columns:
            sort_by = "start_date"
        
        sort_order = "ASC" if sort_order.upper() == "ASC" else "DESC"
        query += f" ORDER BY {sort_by} {sort_order}, id DESC"
        
        cursor = self.db.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [self._row_to_campaign(dict(row)) for row in rows]
    
    def get_by_id(self, campaign_id: int, user_id: int) -> Optional[Campaign]:
        cursor = self.db.execute(
            "SELECT * FROM campaigns WHERE id = ? AND user_id = ?",
            (campaign_id, user_id)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_campaign(dict(row))
    
    def create(self, campaign: Campaign, user_id: int) -> Campaign:
        now = datetime.now().isoformat()
        data = campaign.to_dict()
        data["user_id"] = user_id
        data["created_at"] = now
        data["updated_at"] = now
        
        cursor = self.db.execute("""
            INSERT INTO campaigns (
                user_id, name, description, budget, spent, currency, start_date,
                end_date, target_audience, status, owner, tags, assets,
                notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data["name"], data["description"], data["budget"],
            data["spent"], data["currency"], data["start_date"],
            data["end_date"], data["target_audience"], data["status"],
            data["owner"], data["tags"], data["assets"],
            data["notes"], data["created_at"], data["updated_at"]
        ))
        
        campaign.id = cursor.lastrowid
        campaign.created_at = now
        campaign.updated_at = now
        return campaign
    
    def update(self, campaign_id: int, user_id: int, campaign: Campaign) -> Optional[Campaign]:
        existing = self.get_by_id(campaign_id, user_id)
        if not existing:
            return None
        
        now = datetime.now().isoformat()
        data = campaign.to_dict()
        data["updated_at"] = now
        
        self.db.execute("""
            UPDATE campaigns SET
                name = ?, description = ?, budget = ?, spent = ?,
                currency = ?, start_date = ?, end_date = ?,
                target_audience = ?, status = ?, owner = ?,
                tags = ?, assets = ?, notes = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (
            data["name"], data["description"], data["budget"],
            data["spent"], data["currency"], data["start_date"],
            data["end_date"], data["target_audience"], data["status"],
            data["owner"], data["tags"], data["assets"],
            data["notes"], data["updated_at"], campaign_id, user_id
        ))
        
        campaign.id = campaign_id
        campaign.updated_at = now
        campaign.created_at = existing.created_at
        return campaign
    
    def delete(self, campaign_id: int, user_id: int) -> bool:
        cursor = self.db.execute(
            "DELETE FROM campaigns WHERE id = ? AND user_id = ?",
            (campaign_id, user_id)
        )
        return cursor.rowcount > 0
    
    def duplicate(self, campaign_id: int, user_id: int) -> Optional[Campaign]:
        existing = self.get_by_id(campaign_id, user_id)
        if not existing:
            return None
        
        new_campaign = Campaign(
            name=f"{existing.name} (Copy)",
            description=existing.description,
            budget=existing.budget,
            spent=0.0,
            currency=existing.currency,
            start_date=existing.start_date,
            end_date=existing.end_date,
            target_audience=existing.target_audience,
            status=CampaignStatus.DRAFT,
            owner=existing.owner,
            tags=existing.tags,
            assets=existing.assets,
            notes=existing.notes,
        )
        
        return self.create(new_campaign, user_id)
    
    def _auto_complete_expired(self, user_id: int) -> None:
        today = date.today().isoformat()
        self.db.execute(
            """
            UPDATE campaigns SET status = 'Completed', updated_at = ?
            WHERE user_id = ? AND (status = 'Active' OR status = 'Paused')
            AND end_date IS NOT NULL AND end_date < ?
            """,
            (datetime.now().isoformat(), user_id, today)
        )
    
    def get_stats(self, user_id: int) -> Dict[str, Any]:
        campaigns = self.get_all(user_id=user_id)
        
        stats = {
            "total": len(campaigns),
            "by_status": {s.value: 0 for s in CampaignStatus},
            "total_budget_usd": 0.0,
            "total_spent_usd": 0.0,
            "active_budget_usd": 0.0,
            "expired_count": 0,
        }
        
        from ..services.currency_service import CurrencyService
        currency_service = CurrencyService()
        
        for campaign in campaigns:
            stats["by_status"][campaign.status.value] =                 stats["by_status"].get(campaign.status.value, 0) + 1
            
            budget_usd = currency_service.to_usd(campaign.budget, campaign.currency)
            spent_usd = currency_service.to_usd(campaign.spent, campaign.currency)
            
            stats["total_budget_usd"] += budget_usd
            stats["total_spent_usd"] += spent_usd
            
            if campaign.status == CampaignStatus.ACTIVE:
                stats["active_budget_usd"] += budget_usd
            
            if campaign.is_expired and campaign.status != CampaignStatus.COMPLETED:
                stats["expired_count"] += 1
        
        return stats


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, user: User) -> User:
        now = datetime.now().isoformat()
        cursor = self.db.execute("""
            INSERT INTO users (email, username, password_hash, full_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user.email, user.username, user.password_hash, user.full_name, now, now))
        
        user.id = cursor.lastrowid
        user.created_at = now
        user.updated_at = now
        return user
    
    def get_by_username(self, username: str) -> Optional[User]:
        cursor = self.db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_user(row)
    
    def get_by_email(self, email: str) -> Optional[User]:
        cursor = self.db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_user(row)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        cursor = self.db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_user(row)
    
    def _row_to_user(self, row) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            username=row["username"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
