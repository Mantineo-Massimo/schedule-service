# app/services.py

"""
EN: Business logic for lesson data: fetching, caching, and grouping.
IT: Logica per la gestione delle lezioni: fetch, cache e aggregazione.
"""

import requests
from requests.exceptions import RequestException
from datetime import datetime, time

from app.config import BASE_URL
from app.models import get_from_cache, set_in_cache
from app.constants import FLOOR_CLASSROOMS, CLASSROOM_DESCRIPTIONS


def _first_or_default(lst, default=None):
    """
    EN: Returns the first element of a list or a default value.
    IT: Ritorna il primo elemento di una lista o un valore di default.
    """
    return lst[0] if isinstance(lst, list) and lst else (default or {})


class LessonLooper:
    """
    EN: Helper for fetching and splitting lesson data into morning/afternoon.
    IT: Helper per recuperare e suddividere le lezioni in mattina/pomeriggio.
    """

    def __init__(self, classroom: str, building: str, date: str = None):
        self.classroom         = classroom
        self.building          = building
        self.date              = date or datetime.now().strftime('%Y-%m-%d')
        self.morning_classes   = []
        self.afternoon_classes = []
        self.classroom_name    = "N/A"

    def fetch_and_split(self):
        """
        EN/IT: Use cache if available, otherwise fetch from API and split.
        """
        # 1) Try cache (which now includes classroom_name)
        cached = get_from_cache(self.classroom, self.building, self.date)
        if cached:
            mc, ac, cname = cached
            self.morning_classes   = mc
            self.afternoon_classes = ac
            self.classroom_name    = cname
            return

        # 2) Fetch raw data from external API
        data = self.fetch_lesson_data()

        # 3) Determine classroom_name: first from API, else fallback mapping
        first_room = _first_or_default(
            data[0].get("aule", [])
        ) if isinstance(data, list) and data else {}
        self.classroom_name = first_room.get("descrizione", "N/A")
        if self.classroom_name == "N/A":
            self.classroom_name = CLASSROOM_DESCRIPTIONS.get(
                self.classroom,
                f"Aula {self.classroom}"
            )

        # 4) If API returned an error, exit early (name is already set)
        if isinstance(data, dict) and data.get("error"):
            return

        # 5) Split into morning/afternoon
        self.morning_classes, self.afternoon_classes = self.split_classes(data)

        # 6) Cache both the class lists AND the classroom_name
        set_in_cache(
            self.classroom,
            self.building,
            self.date,
            (self.morning_classes, self.afternoon_classes, self.classroom_name)
        )

    def fetch_lesson_data(self):
        """
        EN/IT: Queries the Cineca API to obtain lessons (impegni).
        """
        try:
            start = f"{self.date}T00:00:00%2B01:00"
            end   = f"{self.date}T23:59:59%2B01:00"
            url = (
                f"{BASE_URL}/api/Impegni/getImpegniPublic"
                f"?aula={self.classroom}"
                f"&edificio={self.building}"
                f"&dataInizio={start}"
                f"&dataFine={end}"
            )
            resp = requests.get(url, timeout=6)
            resp.raise_for_status()
            return resp.json()
        except RequestException:
            return {"error": "Unable to fetch lesson data"}

    def split_classes(self, data):
        """
        EN/IT: Divide lessons into morning (<12:00) and afternoon (>=12:00).
        """
        morning, afternoon = [], []
        for lesson in data or []:
            try:
                dt = datetime.strptime(
                    lesson.get("dataInizio", ""),
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ).time()
            except Exception:
                continue
            (morning if dt < time(12, 0) else afternoon).append(lesson)
        return morning, afternoon


def get_active_or_soon_lessons(building_key: str, floor: int, date: str = None):
    """
    EN: Return all lessons for a specific floor within a building on a given date.
    IT: Restituisce tutte le lezioni di un piano specifico di un edificio per una data.
    """
    date = date or datetime.now().strftime('%Y-%m-%d')
    lessons = []

    floor_map = FLOOR_CLASSROOMS.get(building_key, {}).get(floor, [])
    for classroom_id, building_id in floor_map:
        looper = LessonLooper(classroom_id, building_id, date)
        looper.fetch_and_split()

        for raw in looper.morning_classes + looper.afternoon_classes:
            try:
                start = datetime.fromisoformat(
                    raw["dataInizio"].replace('Z', '+00:00')
                )
                end = datetime.fromisoformat(
                    raw["dataFine"].replace('Z', '+00:00')
                )
            except Exception:
                continue

            evento      = raw.get("evento", {})
            dettagli    = _first_or_default(evento.get("dettagliDidattici", []))
            lesson_name = dettagli.get("nome", "N/A")

            docente     = _first_or_default(raw.get("docenti", []))
            name        = docente.get("nome", "").strip()
            surname     = docente.get("cognome", "").strip()
            instructor  = f"{name} {surname}".strip() or "N/A"

            aula        = _first_or_default(raw.get("aule", []))
            classroom_name = aula.get("descrizione", "N/A")

            lessons.append({
                "start_time"     : start.isoformat(),
                "end_time"       : end.isoformat(),
                "lesson_name"    : lesson_name,
                "instructor"     : instructor,
                "classroom_name" : classroom_name
            })

    lessons.sort(key=lambda x: x["start_time"])
    return lessons
