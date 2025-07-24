"""
Business logic for fetching, processing, and caching lesson data.
"""
import json
import requests
from requests.exceptions import RequestException
from datetime import datetime, time
from typing import List, Dict, Any, Optional
from flask import current_app

from .models import get_from_cache, set_in_cache
from .constants import BUILDING_FLOOR_MAP, CLASSROOM_ID_TO_NAME

def _make_api_request(url: str) -> List[Dict[str, Any]]:
    """Helper function to perform a GET request to the external API."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Aggiunto controllo per risposte non JSON
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        current_app.logger.error(f"API response from {url} is not JSON.")
        return []
    except RequestException as e:
        current_app.logger.error(f"API request to {url} failed: {e}")
        return []
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Failed to decode JSON from {url}: {e}")
        return []


def _parse_lesson(lesson_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses a raw lesson object into a clean dictionary with robust error handling."""
    try:
        # Controlli più robusti sui dati ricevuti
        if not all(k in lesson_data for k in ["dataInizio", "dataFine"]):
            return None

        event = lesson_data.get("evento", {}) or {}
        details = (event.get("dettagliDidattici") or [{}])[0]
        lesson_name = details.get("nome", "N/A")
        
        instructors = lesson_data.get("docenti", []) or []
        instructor_info = instructors[0] if instructors else {}
        first_name = instructor_info.get("nome", "").strip()
        last_name = instructor_info.get("cognome", "").strip()
        instructor = f"{first_name} {last_name}".strip() or "N/A"

        classrooms = lesson_data.get("aule", []) or []
        room_info = classrooms[0] if classrooms else {}
        api_classroom_name = room_info.get("descrizione")
        classroom_id = room_info.get("id")
        classroom_name = api_classroom_name or CLASSROOM_ID_TO_NAME.get(classroom_id, "Unknown Room")

        return {
            "start_time": lesson_data["dataInizio"],
            "end_time": lesson_data["dataFine"],
            "lesson_name": lesson_name,
            "instructor": instructor,
            "classroom_name": classroom_name
        }
    except (TypeError, IndexError, KeyError, AttributeError) as e:
        current_app.logger.warning(f"Skipping malformed lesson object: {lesson_data}. Error: {e}")
        return None

def fetch_classroom_lessons(classroom_id: str, building_id: str, date_str: Optional[str], period: str) -> List[Dict[str, Any]]:
    """Fetches, caches, and filters lessons for a single classroom."""
    date = date_str or datetime.now().strftime('%Y-%m-%d')
    cache_key = f"lessons_{classroom_id}_{date}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data is not None:
        all_lessons = cached_data
    else:
        start_dt = f"{date}T00:00:00"
        end_dt = f"{date}T23:59:59"
        base_url = current_app.config.get('LESSON_API_BASE_URL')
        if not base_url:
            current_app.logger.error("LESSON_API_BASE_URL is not configured.")
            return []
            
        api_url = f"{base_url}/api/Impegni/getImpegniPublic?aula={classroom_id}&edificio={building_id}&dataInizio={start_dt}&dataFine={end_dt}"
        
        raw_lessons = _make_api_request(api_url)
        all_lessons = [parsed for lesson in raw_lessons if (parsed := _parse_lesson(lesson))]
        set_in_cache(cache_key, all_lessons)

    if not all_lessons:
        friendly_name = CLASSROOM_ID_TO_NAME.get(classroom_id, f"Room ID {classroom_id}")
        return [{"classroom_name": friendly_name, "message": "No lessons available"}]

    def filter_by_period(lesson):
        try:
            start_time = datetime.fromisoformat(lesson['start_time'].replace('Z', '+00:00')).time()
            if period == "morning":
                return start_time < time(13, 0)
            if period == "afternoon":
                return start_time >= time(13, 0)
            return True
        except (ValueError, KeyError):
            return False

    return sorted([lesson for lesson in all_lessons if filter_by_period(lesson)], key=lambda x: x['start_time'])


def fetch_floor_lessons(building_key: str, floor: int, date_str: Optional[str]) -> List[Dict[str, Any]]:
    # ... (funzione non modificata)
    classrooms_on_floor = BUILDING_FLOOR_MAP.get(building_key, {}).get(floor, [])
    all_lessons = []
    
    for classroom_id, building_id in classrooms_on_floor:
        lessons = fetch_classroom_lessons(classroom_id, building_id, date_str, "all")
        if lessons and "message" not in lessons[0]:
            all_lessons.extend(lessons)
            
    return sorted(all_lessons, key=lambda x: (x['start_time'], x['classroom_name']))