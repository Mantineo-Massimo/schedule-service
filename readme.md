Campus Lesson Kiosk API
This Flask application provides lesson schedule data in JSON format for use in campus information kiosks. It validates input using Pydantic and caches results to improve performance. The application is containerized using Docker for consistent deployment across environments.

Features
Fetches lesson schedule data from the university API.
Validates input and output using Pydantic.
Caches responses to reduce API calls and improve performance.
Returns lesson data in JSON format with readable date and time.
Input validation on the classroom (aula) and building (edificio) parameters.
Dockerized for easy deployment.
API Endpoint
GET /lessons
Fetches and returns a list of lessons for the specified classroom and building.

Query Parameters:
aula (required): The classroom ID.
edificio (required): The building ID.
Example Request:
bash
Copy code
GET /lessons?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470
Example Response:
json
Copy code
[
    {
        "start_time": "07 October 2024, 07:00 AM",
        "end_time": "07 October 2024, 09:00 AM",
        "lesson_name": "IGIENE ED IGIENE DEGLI ALIMENTI - IGIENE",
        "instructor": "Angela DI PIETRO"
    },
    {
        "start_time": "08 October 2024, 07:00 AM",
        "end_time": "08 October 2024, 09:00 AM",
        "lesson_name": "IGIENE ED IGIENE DEGLI ALIMENTI - IGIENE",
        "instructor": "Simona PERGOLIZZI"
    }
]
Input Validation
Classroom (aula): Must be an alphanumeric string with a maximum length of 30 characters.
Building (edificio): Must be an alphanumeric string with a maximum length of 30 characters.
Output Format:
start_time: The lesson’s start time in a human-readable format.
end_time: The lesson’s end time in a human-readable format.
lesson_name: The name of the lesson.
instructor: The name of the instructor.
Error Responses:
400 Bad Request: Returned if the required parameters are missing or invalid.
Example:

json
Copy code
{
    "error": [
        {
            "loc": ["aula"],
            "msg": "Input should be a valid string",
            "type": "string_type"
        },
        {
            "loc": ["edificio"],
            "msg": "Input should be a valid string",
            "type": "string_type"
        }
    ]
}
Docker Setup
To run this application using Docker, follow these steps:

Build the Docker image:

bash
Copy code
docker build -t flask-app .
Run the Docker container:

bash
Copy code
docker run -p 5000:5000 flask-app
The Flask application will be available at http://localhost:5000.

Installation (Without Docker)
If you prefer to run the application without Docker, follow these steps:

Clone the repository:

bash
Copy code
git clone <repository-url>
cd <project-directory>
Create a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the application:

bash
Copy code
flask run --host=0.0.0.0 --port=5000
Testing
The project includes unit tests that validate the API functionality using unittest. To run the tests:

Run the following command:
bash
Copy code
python -m unittest testing_suit.py
The tests ensure that:

Valid requests return the correct lesson data.
Invalid requests return appropriate error messages.
Input validation is enforced.
