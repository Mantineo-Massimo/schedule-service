from pydantic import BaseModel, Field
from datetime import datetime, timedelta

# Pydantic input validation model
class LessonRequest(BaseModel):
    aula: str = Field(..., max_length=35, pattern=r'^[a-zA-Z0-9]+$')
    edificio: str = Field(..., max_length=35, pattern=r'^[a-zA-Z0-9]+$')

# Pydantic output model
class LessonResponse(BaseModel):
    start_time: str
    end_time: str
    lesson_name: str
    instructor: str
    classroom_name: str

# In-memory cache
cache = {}

def get_from_cache(aula, edificio):
    cache_key = f"{aula}_{edificio}"
    cached_value = cache.get(cache_key)
    if cached_value:
        data, expiration_time = cached_value
        if expiration_time > datetime.now():
            print("Cache hit")
            return data
        else:
            print("Cache expired")
            del cache[cache_key]
    return None

def set_in_cache(aula, edificio, data, ttl_minutes=15):
    cache_key = f"{aula}_{edificio}"
    expiration_time = datetime.now() + timedelta(minutes=ttl_minutes)
    cache[cache_key] = (data, expiration_time)
