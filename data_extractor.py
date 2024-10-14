from flask import Flask, jsonify, request
import requests
from datetime import datetime
import os
from pydantic import BaseModel, ValidationError, Field

app = Flask(__name__)

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
        response.raise_for_status()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
