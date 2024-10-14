from flask import Flask, jsonify, request
import requests
from datetime import datetime, time, timedelta
import os
from pydantic import BaseModel, Field

app = Flask(__name__)

# Base URL for the university API
BASE_URL = os.getenv('LESSON_API_BASE_URL', 'https://unime-public.prod.up.cineca.it')

# Cache structure to store responses temporarily
cache = {}

# Pydantic model for input validation
class LessonRequest(BaseModel):
    aula: str = Field(..., max_length=30, pattern=r'^[a-zA-Z0-9]+$')
    edificio: str = Field(..., max_length=30, pattern=r'^[a-zA-Z0-9]+$')

# Pydantic model for output validation
class LessonResponse(BaseModel):
    start_time: str
    end_time: str
    lesson_name: str
    instructor: str

# Function to fetch lesson data from the API based on aula and edificio
def fetch_lesson_data(aula, edificio):
    today_date = datetime.now().strftime("%Y-%m-%dT00:00:00%z")
    end_date = datetime.now().strftime("%Y-%m-%dT23:59:59%z")

    url = f"{BASE_URL}/api/Impegni/getImpegniPublic?aula={aula}&edificio={edificio}&dataInizio={today_date}&dataFine={end_date}"

    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Function to split the lesson data into morning and afternoon classes
def split_classes(json_data):
    morning_classes = []
    afternoon_classes = []

    for lesson in json_data:
        start_time_str = lesson.get("dataInizio", "N/A")
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").time()

        # Split into morning (before 12:00 PM) and afternoon (12:00 PM onwards)
        if start_time < time(12, 0):
            morning_classes.append(lesson)
        else:
            afternoon_classes.append(lesson)

    return morning_classes, afternoon_classes

# Cache helper functions
def get_from_cache(aula, edificio):
    cache_key = f"{aula}_{edificio}"
    cache_entry = cache.get(cache_key)

    if cache_entry:
        data, expiration_time = cache_entry
        if expiration_time > datetime.now():
            print("Cache hit")
            return data  # Valid cache entry
        else:
            print("Cache expired")
            del cache[cache_key]  # Remove expired cache entry

    print("Cache miss")
    return None

def set_in_cache(aula, edificio, data, ttl_minutes=15):
    cache_key = f"{aula}_{edificio}"
    expiration_time = datetime.now() + timedelta(minutes=ttl_minutes)
    cache[cache_key] = (data, expiration_time)
    print(f"Data cached for aula: {aula}, edificio: {edificio}")

# Class to handle alternating between morning and afternoon classes
class LessonLooper:
    def __init__(self, aula, edificio):
        self.aula = aula
        self.edificio = edificio
        self.current_display = "morning"
        self.morning_classes = []
        self.afternoon_classes = []
        self.toggle_time = datetime.now()

    # Fetch the lesson data and split into morning and afternoon
    def fetch_and_split(self):
        # Check if data is cached
        cached_data = get_from_cache(self.aula, self.edificio)
        if cached_data:
            self.morning_classes, self.afternoon_classes = cached_data
        else:
            # Fetch from API and cache the results
            json_data = fetch_lesson_data(self.aula, self.edificio)
            self.morning_classes, self.afternoon_classes = split_classes(json_data)
            set_in_cache(self.aula, self.edificio, (self.morning_classes, self.afternoon_classes))

    # Toggle between morning and afternoon classes every 15 seconds
    def toggle(self):
        now = datetime.now()
        elapsed_time = (now - self.toggle_time).total_seconds()

        if elapsed_time >= 15:
            self.toggle_time = now  # Reset the toggle time
            self.current_display = "afternoon" if self.current_display == "morning" else "morning"

    def get_current_classes(self):
        self.toggle()  # Toggle morning/afternoon every 15 seconds
        return self.morning_classes if self.current_display == "morning" else self.afternoon_classes

# Global variable to store the lesson looper instance
lesson_looper = None

# Route to start the loop and fetch the classes for the first time
@app.route('/lessons', methods=['GET'])
def get_lessons():
    global lesson_looper
    aula = request.args.get('aula')
    edificio = request.args.get('edificio')

    if not aula or not edificio:
        return jsonify({"error": "Missing 'aula' or 'edificio' parameter"}), 400

    # Initialize the lesson looper if it's not already started
    if lesson_looper is None:
        lesson_looper = LessonLooper(aula, edificio)
        lesson_looper.fetch_and_split()  # Fetch lessons once at the start

    # Get the current set of classes (morning or afternoon)
    current_classes = lesson_looper.get_current_classes()

    # Format the classes using Pydantic
    formatted_classes = [
        LessonResponse(
            start_time=lesson.get("dataInizio", "N/A"),
            end_time=lesson.get("dataFine", "N/A"),
            lesson_name=lesson.get("evento", {}).get("dettagliDidattici", [{}])[0].get("nome", "N/A"),
            instructor=f'{lesson.get("docenti", [{}])[0].get("nome", "N/A")} {lesson.get("docenti", [{}])[0].get("cognome", "N/A")}'
        ).dict()
        for lesson in current_classes
    ]

    return jsonify(formatted_classes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
