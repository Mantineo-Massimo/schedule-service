"""
EN:
Contains the core business logic of the application. This includes functions for
fetching data from the external API, parsing the raw data into a clean format,
and interacting with the cache to improve performance.

IT:
Contiene la logica di business principale dell'applicazione. Include funzioni per
recuperare dati dall'API esterna, effettuare il parsing dei dati grezzi in un formato pulito
e interagire con la cache per migliorare le performance.
"""
import requests
import json
from datetime import datetime, time
from typing import List, Dict, Any, Optional
from flask import current_app
from .models import get_from_cache, set_in_cache

def _make_api_request(url: str) -> List[Dict[str, Any]]:
    """
    EN: Helper function to perform a GET request to the external API with error handling.
    IT: Funzione di aiuto per eseguire una richiesta GET all'API esterna con gestione degli errori.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json() if "application/json" in response.headers.get("Content-Type", "") else []
    except (requests.RequestException, json.JSONDecodeError) as e:
        current_app.logger.error(f"API request to {url} failed: {e}")
        return []

def _parse_lesson(lesson_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    EN: Safely parses a raw lesson object from the API into a clean, standardized dictionary.
    IT: Effettua il parsing sicuro di un oggetto lezione grezzo dall'API in un dizionario pulito e standardizzato.
    """
    classroom_id_to_name = current_app.config.get('CLASSROOM_ID_TO_NAME', {})
    try:
        event = lesson_data.get("evento", {}) or {}
        details = (event.get("dettagliDidattici") or [{}])[0]
        instructors = lesson_data.get("docenti", []) or []
        instructor_info = instructors[0] if instructors else {}
        classrooms = lesson_data.get("aule", []) or []
        room_info = classrooms[0] if classrooms else {}
        classroom_id = room_info.get("id")
        return {
            "start_time": lesson_data["dataInizio"],
            "end_time": lesson_data["dataFine"],
            "lesson_name": details.get("nome", "N/A"),
            "instructor": f"{instructor_info.get('nome', '').strip()} {instructor_info.get('cognome', '').strip()}".strip() or "N/A",
            "classroom_name": room_info.get("descrizione") or classroom_id_to_name.get(classroom_id, "Unknown Room")
        }
    except (TypeError, IndexError, KeyError, AttributeError) as e:
        current_app.logger.warning(f"Skipping malformed lesson object. Error: {e}")
        return None

def fetch_classroom_lessons(classroom_id: str, building_id: str, date_str: Optional[str], period: str) -> List[Dict[str, Any]]:
    """
    EN: Fetches, caches, filters, and sorts lessons for a single classroom.
    IT: Recupera, mette in cache, filtra e ordina le lezioni per una singola aula.
    """
    date = date_str or datetime.now().strftime('%Y-%m-%d')
    cache_key = f"lessons_{classroom_id}_{date}"
    if (cached_data := get_from_cache(cache_key)) is not None:
        all_lessons = cached_data
    else:
        api_url = f"{current_app.config.get('LESSON_API_BASE_URL')}/api/Impegni/getImpegniPublic?aula={classroom_id}&edificio={building_id}&dataInizio={date}T00:00:00&dataFine={date}T23:59:59"
        all_lessons = [p for l in _make_api_request(api_url) if (p := _parse_lesson(l))]
        set_in_cache(cache_key, all_lessons)

    if not all_lessons:
        classroom_id_to_name = current_app.config.get('CLASSROOM_ID_TO_NAME', {})
        return [{"classroom_name": classroom_id_to_name.get(classroom_id, f"ID {classroom_id}"), "message": "No lessons available"}]

    def filter_by_period(lesson):
        start_time = datetime.fromisoformat(lesson['start_time'].replace('Z', '+00:00')).time()
        return (period == "morning" and start_time < time(13, 0)) or \
               (period == "afternoon" and start_time >= time(13, 0)) or \
               period == "all"

    return sorted([l for l in all_lessons if filter_by_period(l)], key=lambda x: x['start_time'])

def fetch_floor_lessons(building_key: str, floor: int, date_str: Optional[str]) -> List[Dict[str, Any]]:
    """
    EN: Fetches all lessons for every classroom on a specific floor.
    IT: Recupera tutte le lezioni per ogni aula di un piano specifico.
    """
    building_floor_map = current_app.config.get('BUILDING_FLOOR_MAP', {})
    classrooms = building_floor_map.get(building_key, {}).get(str(floor), [])
    all_lessons = []
    for classroom_id, building_id in classrooms:
        lessons = fetch_classroom_lessons(classroom_id, building_id, date_str, "all")
        if lessons and "message" not in lessons[0]:
            all_lessons.extend(lessons)
    return sorted(all_lessons, key=lambda x: (x['start_time'], x['classroom_name']))