"""Base exception classes for Stratis."""

from typing import Optional, Any


class StratisError(Exception):
    """Base exception for all Stratis errors."""
    
    def __init__(self, message: str, detail: Optional[Any] = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class DatabaseError(StratisError):
    pass


class NotFoundError(StratisError):
    pass


class ValidationError(StratisError):
    pass


class AIError(StratisError):
    pass


class ConfigurationError(StratisError):
    pass
