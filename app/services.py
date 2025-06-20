"""
EN: Business logic for lesson data: fetching, caching, and grouping.
IT: Logica per la gestione delle lezioni: fetch, cache e aggregazione.
"""

import requests
from requests.exceptions import RequestException
from datetime import datetime, time
from app.config import BASE_URL
from app.models import get_from_cache, set_in_cache
from app.constants import FLOOR_CLASSROOMS

def _first_or_default(lst, default=None):
    # EN/IT: Returns the first element or default / Ritorna il primo elemento o default
    return lst[0] if isinstance(lst, list) and lst else (default or {})

class LessonLooper:
    """
    EN: Helper for fetching and splitting lesson data.
    IT: Helper per recuperare e suddividere le lezioni.
    """

    def __init__(self, classroom, building, date=None):
        self.classroom = classroom
        self.building = building
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.morning_classes = []
        self.afternoon_classes = []
        self.classroom_name = "N/A"

    def fetch_and_split(self):
        # EN/IT: Use cache if available / Usa cache se disponibile
        cached = get_from_cache(self.classroom, self.building, self.date)
        if cached:
            self.morning_classes, self.afternoon_classes = cached
            return

        data = self.fetch_lesson_data()
        if isinstance(data, dict) and data.get("error"):
            return

        first_aule = _first_or_default(data[0].get("aule", [])) if data else {}
        self.classroom_name = first_aule.get("descrizione", "N/A")

        self.morning_classes, self.afternoon_classes = self.split_classes(data)
        set_in_cache(self.classroom, self.building, self.date, (self.morning_classes, self.afternoon_classes))

    def fetch_lesson_data(self):
        # EN/IT: Queries the Cineca API to obtain commitments / Interroga l’API Cineca per ottenere gli impegni
        try:
            start = f"{self.date}T00:00:00%2B01:00"
            end   = f"{self.date}T23:59:59%2B01:00"
            url = f"{BASE_URL}/api/Impegni/getImpegniPublic?aula={self.classroom}&edificio={self.building}&dataInizio={start}&dataFine={end}"
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except RequestException:
            return {"error": "Unable to fetch lesson data"}

    def split_classes(self, data):
        # EN/IT: Divides lessons into morning and afternoon / Divide le lezioni in mattina e pomeriggio
        morning, afternoon = [], []
        for lesson in data or []:
            try:
                dt = datetime.strptime(lesson.get("dataInizio", ""), "%Y-%m-%dT%H:%M:%S.%fZ").time()
            except Exception:
                continue
            (morning if dt < time(12, 0) else afternoon).append(lesson)
        return morning, afternoon

def get_active_or_soon_lessons(floor_key, date=None):
    """
    EN: Return all lessons for a floor on a given date.
    IT: Restituisce tutte le lezioni di un piano per una data.
    """
    date = date or datetime.now().strftime('%Y-%m-%d')
    results = []

    for classroom, building in FLOOR_CLASSROOMS.get(floor_key, []):
        looper = LessonLooper(classroom, building, date)
        looper.fetch_and_split()

        for l in looper.morning_classes + looper.afternoon_classes:
            try:
                start = datetime.fromisoformat(l["dataInizio"].replace('Z', '+00:00'))
                end   = datetime.fromisoformat(l["dataFine"].replace('Z', '+00:00'))
            except Exception:
                continue

            evento = l.get("evento", {})
            dettagli = _first_or_default(evento.get("dettagliDidattici", []), {})
            lesson_name = dettagli.get("nome", "N/A")

            docente = _first_or_default(l.get("docenti", []), {})
            name = docente.get("nome", "").strip()
            surname = docente.get("cognome", "").strip()
            instructor = f"{name} {surname}".strip() or "N/A"

            aula_info = _first_or_default(l.get("aule", []), {})
            classroom_name = aula_info.get("descrizione", "N/A")

            results.append({
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "lesson_name": lesson_name,
                "instructor": instructor,
                "classroom_name": classroom_name
            })

    return results
