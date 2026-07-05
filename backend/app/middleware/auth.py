"""Authentication middleware."""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from ..database import get_db, DatabaseConnection
from ..database.repositories import UserRepository
from ..services.auth_service import AuthService
from ..models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(db: DatabaseConnection = Depends(get_db)) -> AuthService:
    user_repository = UserRepository(db)
    return AuthService(user_repository)


def require_auth():
    """Dependency for protected routes."""
    async def dependency(token: str = Depends(oauth2_scheme), db: DatabaseConnection = Depends(get_db)):
        user_repository = UserRepository(db)
        auth_service = AuthService(user_repository)
        user = auth_service.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    return dependency


async def get_current_user_from_request(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    
    token = auth_header.split(" ")[1]
    db = get_db()
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    return user
