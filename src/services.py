import requests
from requests.exceptions import RequestException
from datetime import datetime, time
from src.config import BASE_URL
from src.models import cache, get_from_cache, set_in_cache

class LessonLooper:
    def __init__(self, aula, edificio):
        self.aula = aula
        self.edificio = edificio
        self.current_display = "morning"
        self.morning_classes = []
        self.afternoon_classes = []
        self.toggle_time = datetime.now()
        self.classroom_name="N/A"

    def fetch_and_split(self):
        try:
            cached_data = get_from_cache(self.aula, self.edificio)
            if cached_data:
                self.morning_classes, self.afternoon_classes = cached_data
            else:
                json_data = self.fetch_lesson_data()
                if 'error' not in json_data:
                    # Extract classroom name from the first lesson if available
                    if json_data and 'aule' in json_data[0]:
                        self.classroom_name = json_data[0].get("aule", [{}])[0].get("descrizione", "N/A")
                        print("Extracted classroom name:", self.classroom_name)  # Debugging line
                    else:
                        print("Classroom name not found in JSON structure.")
                    self.morning_classes, self.afternoon_classes = self.split_classes(json_data)
                    set_in_cache(self.aula, self.edificio, (self.morning_classes, self.afternoon_classes))
                else:
                    print("Error from API or cache failure")
        except Exception as e:
            print(f"Error accessing cache or fetching data: {e}")



    def fetch_lesson_data(self):
        try:
            today_date = datetime.now().strftime("%Y-%m-%dT00:00:00%z")
            end_date = datetime.now().strftime("%Y-%m-%dT23:59:59%z")
            url = f"{BASE_URL}/api/Impegni/getImpegniPublic?aula={self.aula}&edificio={self.edificio}&dataInizio={today_date}&dataFine={end_date}"
        
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses like the 400 , 500
            return response.json()
    
        except RequestException as e:
            print(f"Error fetching data from API: {e}")
            return {"error": "Unable to fetch lesson data"}


    def split_classes(self, json_data):
        morning_classes = []
        afternoon_classes = []

        for lesson in json_data:
            try:
                start_time_str = lesson.get("dataInizio", "N/A")
                start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").time()
            except KeyError as e:
                print(f"Missing key in lesson data: {e}")
                continue  # Skip to the next lesson

            # Split into morning and afternoon
            if start_time < time(12, 0):
                morning_classes.append(lesson)
            else:
                afternoon_classes.append(lesson)

        return morning_classes, afternoon_classes

    def toggle(self):
        now = datetime.now()
        elapsed_time = (now - self.toggle_time).total_seconds()

        if elapsed_time >= 15:
            self.toggle_time = now  # Reset the toggle time
            self.current_display = "afternoon" if self.current_display == "morning" else "morning"

    def get_current_classes(self):
        self.toggle()  # Toggle morning/afternoon every 15 seconds
        return self.morning_classes if self.current_display == "morning" else self.afternoon_classes