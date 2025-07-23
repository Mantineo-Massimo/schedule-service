"""
Data models for request/response validation and in-memory caching utilities.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple, Any
from datetime import datetime, timedelta
from flask import current_app

class LessonRequest(BaseModel):
    """Input schema for a lesson request."""
    classroom: str
    building: str
    date: Optional[str] = None
    period: Optional[str] = Field(default="all", pattern="^(morning|afternoon|all)$")

class LessonResponse(BaseModel):
    """Output schema for a single lesson."""
    start_time: str
    end_time: str
    lesson_name: str
    instructor: str
    classroom_name: str

# --- In-Memory Cache ---
_cache: dict[str, Tuple[Any, datetime]] = {}

def get_from_cache(key: str) -> Optional[Any]:
    """Returns data from the cache if it exists and has not expired."""
    item = _cache.get(key)
    if item:
        data, expiration = item
        if expiration > datetime.now():
            return data
        # Remove expired item
        del _cache[key]
    return None

def set_in_cache(key: str, data: Any):
    """Saves data to the cache with a configured Time-To-Live (TTL)."""
    ttl_minutes = current_app.config.get('CACHE_TTL_MINUTES', 15)
    expiration = datetime.now() + timedelta(minutes=ttl_minutes)
    _cache[key] = (data, expiration)