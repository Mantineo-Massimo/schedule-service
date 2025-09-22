"""
EN:
Defines Pydantic models for data validation and the Redis cache helper functions.
These models ensure that data structures are consistent and type-safe.

IT:
Definisce i modelli Pydantic per la validazione dei dati e le funzioni di aiuto per la cache Redis.
Questi modelli assicurano che le strutture dati siano consistenti e con tipi sicuri.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
import json
from flask import current_app

class LessonRequest(BaseModel):
    """
    EN: Input schema for a lesson request, used to validate the JSON body.
    IT: Schema di input per una richiesta di lezioni, usato per validare il corpo JSON.
    """
    classroom: str
    building: str
    date: Optional[str] = None
    period: Optional[str] = Field(default="all", pattern="^(morning|afternoon|all)$")

def get_from_cache(key: str) -> Optional[Any]:
    """
    EN: Returns data from the Redis cache if it exists. Handles potential connection errors.
    IT: Restituisce i dati dalla cache Redis se esistono. Gestisce potenziali errori di connessione.
    """
    try:
        cached_value = current_app.redis.get(key)
        if cached_value:
            return json.loads(cached_value.decode('utf-8'))
        return None
    except Exception as e:
        current_app.logger.error(f"Redis GET failed for key '{key}': {e}")
        return None

def set_in_cache(key: str, data: Any):
    """
    EN: Saves data to the Redis cache with a configured TTL. Handles potential connection errors.
    IT: Salva i dati nella cache Redis con un TTL configurato. Gestisce potenziali errori di connessione.
    """
    try:
        ttl_seconds = current_app.config.get('CACHE_TTL_MINUTES', 15) * 60
        value_to_store = json.dumps(data)
        current_app.redis.setex(key, ttl_seconds, value_to_store)
    except Exception as e:
        current_app.logger.error(f"Redis SETEX failed for key '{key}': {e}")