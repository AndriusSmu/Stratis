"""Exception handling for Stratis backend."""

from .base import (
    StratisError,
    DatabaseError,
    NotFoundError,
    ValidationError,
    AIError,
    ConfigurationError,
)
from .handlers import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    ai_exception_handler,
)

__all__ = [
    "StratisError",
    "DatabaseError",
    "NotFoundError",
    "ValidationError",
    "AIError",
    "ConfigurationError",
    "validation_exception_handler",
    "http_exception_handler",
    "generic_exception_handler",
    "ai_exception_handler",
]
