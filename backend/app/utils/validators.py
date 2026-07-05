"""Custom validation utilities."""

import re
from datetime import datetime
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    if not email:
        return True
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_date_range(
    start_date: str,
    end_date: Optional[str]
) -> Tuple[bool, Optional[str]]:
    if not end_date:
        return True, None
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        if end < start:
            return False, "End date must be after start date"
        return True, None
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"


def sanitize_string(text: str) -> str:
    if not text:
        return text
    return ''.join(char for char in text if ord(char) >= 32 or char == '\n')


def truncate_string(text: str, max_length: int) -> str:
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
