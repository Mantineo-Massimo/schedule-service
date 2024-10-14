<<<<<<< HEAD
from flask import Flask, jsonify, request
=======
from flask import Flask, jsonify
>>>>>>> 296877114146abd42e7aac284b813a9b4d1d32ba
import requests
from datetime import datetime
import os
from pydantic import BaseModel, ValidationError, Field

app = Flask(__name__)

<<<<<<< HEAD
# Load the base URL from the environment variable
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
=======
# Function to format date and time
def format_datetime(iso_datetime):
    try:
        dt = datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%d %B %Y, %I:%M %p")  # Format: 07 October 2024, 07:00 AM
    except ValueError:
        return iso_datetime  
>>>>>>> 296877114146abd42e7aac284b813a9b4d1d32ba

# Function to fetch and transform lesson data
def transform_lesson_data(aula: str, edificio: str):
    # Get today's date
    today_date = datetime.now().strftime("%Y-%m-%dT00:00:00%z")
    end_date = datetime.now().strftime("%Y-%m-%dT23:59:59%z")

    # Build the API URL using both aula and edificio
    url = f"{BASE_URL}/api/Impegni/getImpegniPublic?aula={aula}&edificio={edificio}&dataInizio={today_date}&dataFine={end_date}"

    # Request lesson data
    try:
        response = requests.get(url)
<<<<<<< HEAD
        response.raise_for_status()
=======
        response.raise_for_status() 
>>>>>>> 296877114146abd42e7aac284b813a9b4d1d32ba
        json_data = response.json()

        lesson_info_list = []
        for lesson in json_data:
            # Extract lesson details
            start_time = lesson.get("dataInizio", "N/A")
            end_time = lesson.get("dataFine", "N/A")
            lesson_name = lesson.get("evento", {}).get("dettagliDidattici", [{}])[0].get("nome", "N/A")
            instructor_info = lesson.get("docenti", [{}])[0]
            instructor_name = f"{instructor_info.get('nome', 'N/A')} {instructor_info.get('cognome', 'N/A')}"

            lesson_info = LessonResponse(
                start_time=start_time,
                end_time=end_time,
                lesson_name=lesson_name,
                instructor=instructor_name
            )

            # Validate the output data
            lesson_info_list.append(lesson_info.model_dump())  # Convert Pydantic model to dictionary

        return lesson_info_list
    except requests.exceptions.RequestException as e:
        return [{"error": "Unable to retrieve lesson data"}]

<<<<<<< HEAD
# Route to return JSON lesson data with classroom and building as query parameters
@app.route('/lessons', methods=['GET'])
def get_lessons():
    # Extract the 'aula' and 'edificio' query parameters
    aula = request.args.get('aula')
    edificio = request.args.get('edificio')

    # Input validation using Pydantic
    try:
        lesson_request = LessonRequest(aula=aula, edificio=edificio)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    # Call the function to fetch and transform the lesson data
    data = transform_lesson_data(lesson_request.aula, lesson_request.edificio)

    # Return the validated data as JSON
    return jsonify(data)
=======
# Flask route to return JSON data
@app.route('/lessons', methods=['GET'])
def get_lessons():
    data = transform_lesson_data()
    return jsonify(data)  # Return JSON data
>>>>>>> 296877114146abd42e7aac284b813a9b4d1d32ba

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
