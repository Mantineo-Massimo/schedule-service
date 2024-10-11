from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# Function to format date and time
def format_datetime(iso_datetime):
    try:
        dt = datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%d %B %Y, %I:%M %p")  # Format: 07 October 2024, 07:00 AM
    except ValueError:
        return iso_datetime  # If there's an error, return the original string

# Function to fetch and transform lesson data
def transform_lesson_data():
    url = "https://unime-public.prod.up.cineca.it/api/Impegni/getImpegniPublic?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470&dataInizio=2024-10-07T00:00:00%2B02:00&dataFine=2024-10-14T00:00:00%2B02:00"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses
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

# Flask route to render HTML table for kiosk display
@app.route('/lessons', methods=['GET'])
def get_lessons():
    data = transform_lesson_data()

    # the HTML part for displaying data in table
    html_template = '''
    <html>
    <head>
        <title>Lesson Schedule</title>
        <meta http-equiv="refresh" content="60">  <!-- Auto-refresh every 60 seconds -->
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;  /* Ensure vertical layout */
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            h1 {
                text-align: center;
                font-size: 28px;  /* Adjusted the font size */
                color: #333;
                margin-bottom: 20px;
                width: 100%;  /* Ensures it stays centered */
            }
            table {
                width: 80%;  /* Reduce width to fit better */
                border-collapse: collapse;
                font-size: 16px;  /* Reduced font size */
            }
            table, th, td {
                border: 1px solid #333;
            }
            th, td {
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #333;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            /* Responsive design for smaller screens */
            @media screen and (max-width: 768px) {
                table {
                    width: 100%;
                    font-size: 14px;
                }
                h1 {
                    font-size: 24px;
                }
            }
        </style>
    </head>
    <body>
        <h1>Lesson Schedule</h1>
        <table>
            <tr>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Lesson Name</th>
                <th>Instructor</th>
            </tr>
            {% for lesson in data %}
            {% if lesson.error %}
            <tr>
                <td colspan="4">{{ lesson.error }}</td>
            </tr>
            {% else %}
            <tr>
                <td>{{ lesson.start_time }}</td>
                <td>{{ lesson.end_time }}</td>
                <td>{{ lesson.lesson_name }}</td>
                <td>{{ lesson.instructor }}</td>
            </tr>
            {% endif %}
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    return render_template_string(html_template, data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
