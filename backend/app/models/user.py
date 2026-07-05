"""User model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User domain model."""
    
    id: Optional[int] = None
    email: str = ""
    username: str = ""
    password_hash: str = ""
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
