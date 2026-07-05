"""
Configuration management for Stratis backend.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = field(default_factory=lambda: os.getenv("STRATIS_DB_PATH", "campaigns.db"))
    
    @property
    def absolute_path(self) -> Path:
        return Path(self.path).resolve()


@dataclass
class AIConfig:
    """AI/Ollama configuration."""
    url: str = field(default_factory=lambda: os.getenv("STRATIS_OLLAMA_URL", "http://localhost:11434/api/generate"))
    model: str = field(default_factory=lambda: os.getenv("STRATIS_OLLAMA_MODEL", "llama3.2"))
    timeout: int = field(default_factory=lambda: int(os.getenv("STRATIS_OLLAMA_TIMEOUT", "60")))
    enabled: bool = field(default_factory=lambda: os.getenv("STRATIS_AI_ENABLED", "true").lower() == "true")


@dataclass
class APIConfig:
    """API configuration."""
    prefix: str = field(default_factory=lambda: os.getenv("STRATIS_API_PREFIX", ""))
    environment: str = field(default_factory=lambda: os.getenv("STRATIS_ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("STRATIS_DEBUG", "false").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("STRATIS_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("STRATIS_PORT", "8000")))
    reload: bool = field(default_factory=lambda: os.getenv("STRATIS_RELOAD", "false").lower() == "true")


@dataclass
class CORSConfig:
    """CORS configuration."""
    origins: List[str] = field(default_factory=lambda: os.getenv("STRATIS_CORS_ORIGINS", "*").split(","))
    allow_credentials: bool = True
    allow_methods: List[str] = field(default_factory=lambda: ["*"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests: int = field(default_factory=lambda: int(os.getenv("STRATIS_RATE_LIMIT_REQUESTS", "100")))
    period: int = field(default_factory=lambda: int(os.getenv("STRATIS_RATE_LIMIT_PERIOD", "60")))


@dataclass
class AuthConfig:
    """Authentication configuration."""
    secret_key: str = field(default_factory=lambda: os.getenv("STRATIS_SECRET_KEY", "dev-secret-key-change-me"))
    algorithm: str = field(default_factory=lambda: os.getenv("STRATIS_JWT_ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(default_factory=lambda: int(os.getenv("STRATIS_ACCESS_TOKEN_EXPIRE_MINUTES", "30")))


@dataclass
class Config:
    """Main configuration container."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    api: APIConfig = field(default_factory=APIConfig)
    cors: CORSConfig = field(default_factory=CORSConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls()
    
    def ensure_directories(self) -> None:
        db_dir = self.database.absolute_path.parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)


config = Config.from_env()
