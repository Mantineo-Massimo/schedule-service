"""
EN: Data models and caching utilities.
IT: Modelli dati e funzioni di cache.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

class LessonRequest(BaseModel):
    """
    EN: Input schema for lesson requests.
    IT: Schema input per richieste lezione.
    """
    classroom: str
    building: str
    date: Optional[str] = None
    period: Optional[str] = "all"

class LessonResponse(BaseModel):
    """
    EN: Output schema for a single lesson.
    IT: Schema output per una lezione.
    """
    start_time: str
    end_time: str
    lesson_name: str
    instructor: str
    classroom_name: str

# EN/IT: In-memory cache dictionary / Dizionario della cache in memoria
_cache = {}

def get_from_cache(classroom: str, building: str, date: str):
    """
    EN: Return cached data if still valid.
    IT: Ritorna dati dalla cache se validi.
    """
    key = f"{classroom}_{building}_{date}"
    item = _cache.get(key)
    if item:
        data, expire = item
        if expire > datetime.now():
            return data
        del _cache[key]
    return None

def set_in_cache(classroom: str, building: str, date: str, data, ttl: int = 15):
    """
    EN: Save data to cache with expiration.
    IT: Salva dati in cache con scadenza.
    """
    key = f"{classroom}_{building}_{date}"
    expire = datetime.now() + timedelta(minutes=ttl)
    _cache[key] = (data, expire)
