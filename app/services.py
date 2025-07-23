"""
Business logic for fetching, processing, and caching lesson data.
"""
import requests
from requests.exceptions import RequestException
from datetime import datetime, time
from typing import List, Dict, Any, Optional
from flask import current_app

from .models import get_from_cache, set_in_cache
from .constants import BUILDING_FLOOR_MAP, CLASSROOM_ID_TO_NAME # Assicurati che CLASSROOM_ID_TO_NAME sia importato

def _make_api_request(url: str) -> List[Dict[str, Any]]:
    # ... (funzione non modificata)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        current_app.logger.error(f"API request to {url} failed: {e}")
        return []

def _parse_lesson(lesson_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # ... (funzione non modificata)
    try:
        start_time_str = lesson_data.get("dataInizio", "")
        end_time_str = lesson_data.get("dataFine", "")
        
        event = lesson_data.get("evento", {})
        details = (event.get("dettagliDidattici") or [{}])[0]
        lesson_name = details.get("nome", "N/A")
        
        instructors = lesson_data.get("docenti", [])
        instructor_info = instructors[0] if instructors else {}
        first_name = instructor_info.get("nome", "").strip()
        last_name = instructor_info.get("cognome", "").strip()
        instructor = f"{first_name} {last_name}".strip() or "N/A"

        classrooms = lesson_data.get("aule", [])
        room_info = classrooms[0] if classrooms else {}
        # MODIFICA: Usa la mappa dei nomi come fallback se la descrizione API manca
        api_classroom_name = room_info.get("descrizione")
        classroom_id = room_info.get("id")
        classroom_name = api_classroom_name or CLASSROOM_ID_TO_NAME.get(classroom_id, "Unknown Room")

        return {
            "start_time": start_time_str,
            "end_time": end_time_str,
            "lesson_name": lesson_name,
            "instructor": instructor,
            "classroom_name": classroom_name
        }
    except (TypeError, IndexError, KeyError):
        return None

def fetch_classroom_lessons(classroom_id: str, building_id: str, date_str: Optional[str], period: str) -> List[Dict[str, Any]]:
    """Fetches, caches, and filters lessons for a single classroom."""
    date = date_str or datetime.now().strftime('%Y-%m-%d')
    cache_key = f"lessons_{classroom_id}_{date}"
    
    cached_data = get_from_cache(cache_key)
    if cached_data:
        all_lessons = cached_data
    else:
        start_dt = f"{date}T00:00:00"
        end_dt = f"{date}T23:59:59"
        api_url = (
            f"{current_app.config['LESSON_API_BASE_URL']}/api/Impegni/getImpegniPublic"
            f"?aula={classroom_id}&edificio={building_id}&dataInizio={start_dt}&dataFine={end_dt}"
        )
        raw_lessons = _make_api_request(api_url)
        all_lessons = [parsed for lesson in raw_lessons if (parsed := _parse_lesson(lesson))]
        set_in_cache(cache_key, all_lessons)

    # MODIFICA: Logica migliorata per il caso "nessuna lezione"
    if not all_lessons:
        # Cerca sempre il nome nella mappa, anche se non ci sono lezioni
        friendly_name = CLASSROOM_ID_TO_NAME.get(classroom_id, f"Room ID {classroom_id}")
        return [{"classroom_name": friendly_name, "message": "No lessons available"}]

    def filter_by_period(lesson):
        start_time = datetime.fromisoformat(lesson['start_time'].replace('Z', '+00:00')).time()
        if period == "morning":
            return start_time < time(13, 0)
        if period == "afternoon":
            return start_time >= time(13, 0)
        return True

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