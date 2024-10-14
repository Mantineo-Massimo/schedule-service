from flask import Flask, jsonify, request
import requests
from datetime import datetime, time
from threading import Timer
import os
from pydantic import BaseModel, Field, ValidationError

app = Flask(__name__)

BASE_URL = os.getenv('LESSON_API_BASE_URL', 'https://unime-public.prod.up.cineca.it')

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

# Class to handle alternating between morning and afternoon classes
class LessonLooper:
    def __init__(self, aula, edificio):
        self.aula = aula
        self.edificio = edificio
        self.current_display = "morning"  # Start with morning classes
        self.morning_classes = []
        self.afternoon_classes = []
        self.toggle_time = datetime.now()  # Store the time of the toggle

    # Fetch the lesson data and split into morning and afternoon
    def fetch_and_split(self):
        json_data = fetch_lesson_data(self.aula, self.edificio)
        self.morning_classes, self.afternoon_classes = split_classes(json_data)
        print(f"Morning classes: {len(self.morning_classes)}")
        print(f"Afternoon classes: {len(self.afternoon_classes)}")

    # Toggle every 15 seconds based on time passed
    def toggle(self):
        now = datetime.now()
        elapsed_time = (now - self.toggle_time).total_seconds()

        # Toggle between morning and afternoon every 15 seconds
        if elapsed_time >= 15:
            self.toggle_time = now  # Reset the toggle time
            if self.current_display == "morning":
                self.current_display = "afternoon"
            else:
                self.current_display = "morning"

    def get_current_classes(self):
        # Toggle the display every 15 seconds
        self.toggle()

        if self.current_display == "morning":
            return self.morning_classes
        else:
            return self.afternoon_classes

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
