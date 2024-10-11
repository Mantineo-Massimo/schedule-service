from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Function to format date and time
def format_datetime(iso_datetime):
    try:
        dt = datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%d %B %Y, %I:%M %p")  # Format: 07 October 2024, 07:00 AM
    except ValueError:
        return iso_datetime  

# Function to fetch and transform lesson data
def transform_lesson_data():
    url = "https://unime-public.prod.up.cineca.it/api/Impegni/getImpegniPublic?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470&dataInizio=2024-10-07T00:00:00%2B02:00&dataFine=2024-10-14T00:00:00%2B02:00"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        json_data = response.json()
        lesson_info_list = []

        for lesson in json_data:
            start_time = format_datetime(lesson.get("dataInizio", "N/A"))
            end_time = format_datetime(lesson.get("dataFine", "N/A"))
            lesson_name = lesson.get("evento", {}).get("dettagliDidattici", [{}])[0].get("nome", "N/A")
            instructor_info = lesson.get("docenti", [{}])[0]
            instructor_name = f"{instructor_info.get('nome', 'N/A')} {instructor_info.get('cognome', 'N/A')}"

            lesson_info = {
                "start_time": start_time,
                "end_time": end_time,
                "lesson_name": lesson_name,
                "instructor": instructor_name
            }
            lesson_info_list.append(lesson_info)

        return lesson_info_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return [{"error": "Unable to retrieve lesson data at this time"}]

# Flask route to return JSON data
@app.route('/lessons', methods=['GET'])
def get_lessons():
    data = transform_lesson_data()
    return jsonify(data)  # Return JSON data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
