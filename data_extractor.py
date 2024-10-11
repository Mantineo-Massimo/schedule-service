from flask import Flask, render_template_string
import requests

app = Flask(__name__)

def transform_lesson_data():
    url = "https://unime-public.prod.up.cineca.it/api/Impegni/getImpegniPublic?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470&dataInizio=2024-10-07T00:00:00%2B02:00&dataFine=2024-10-14T00:00:00%2B02:00"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        lesson_info_list = []





        for lesson in json_data:
            start_time = lesson.get("dataInizio", "N/A")
            end_time = lesson.get("dataFine", "N/A")
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
    else:
        return [{"error": "Failed to retrieve data"}]

# Flask route to render HTML table
@app.route('/lessons', methods=['GET'])
def get_lessons():
    data = transform_lesson_data()

    # the htlm part for displaying data in table 
    html_template = '''
    <html>
    <head>
        <title>Lesson Schedule</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 8px;
                text-align: left;
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
            <tr>
                <td>{{ lesson.start_time }}</td>
                <td>{{ lesson.end_time }}</td>
                <td>{{ lesson.lesson_name }}</td>
                <td>{{ lesson.instructor }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''

    return render_template_string(html_template, data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
