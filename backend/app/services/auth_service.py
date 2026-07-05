"""Authentication service."""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from ..config import config
from ..database.repositories import UserRepository
from ..exceptions import ValidationError
from ..models import User


class AuthService:
    """Service for authentication."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    
    def create_access_token(self, user_id: int, username: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=config.auth.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
        }
        return jwt.encode(payload, config.auth.secret_key, algorithm=config.auth.algorithm)
    
    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, config.auth.secret_key, algorithms=[config.auth.algorithm])
            return payload
        except JWTError:
            return None
    
    def register_user(self, email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
        if self.user_repository.get_by_username(username):
            raise ValidationError("Username already taken")
        
        if self.user_repository.get_by_email(email):
            raise ValidationError("Email already registered")
        
        password_hash = self.hash_password(password)
        
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
        )
        
        return self.user_repository.create(user)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def get_current_user(self, token: str) -> Optional[User]:
        payload = self.decode_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return self.user_repository.get_by_id(int(user_id))
