# **Campus Lesson Kiosk API**

This is a Flask-based application that provides lesson schedule data in JSON format for campus information kiosks. It leverages **Pydantic** for input and output validation and implements caching to optimize API performance. The application is fully containerized using **Docker** for consistent deployment across different environments.

---

## **Features**
- Fetches lesson schedule data from the university API.
- Validates both input and output using **Pydantic**.
- Caches responses to reduce API load and improve performance.
- Returns lesson data in a clean and readable JSON format with human-readable date and time.
- Performs input validation on classroom (`aula`) and building (`edificio`) parameters.
- Dockerized for seamless and easy deployment.

---

## **API Endpoints**

### **GET /lessons**
Fetches and returns a list of lessons for the specified classroom and building.

#### **Query Parameters**:
- `aula` (required): The classroom ID.
- `edificio` (required): The building ID.

#### **Example Request**:
GET /lessons?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470


#### **Example Response**:
```json
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
```
## **Input Validation**

- **Classroom (`aula`)**: 
  - Must be an alphanumeric string.
  - Maximum length of 30 characters.
  
- **Building (`edificio`)**:
  - Must be an alphanumeric string.
  - Maximum length of 30 characters.

## **Output Format**

- **`start_time`**: The lesson’s start time in a human-readable format (e.g., `07 October 2024, 07:00 AM`).
- **`end_time`**: The lesson’s end time in a human-readable format.
- **`lesson_name`**: The name of the lesson.
- **`instructor`**: The name of the instructor.

## **Error Responses**

- **`400 Bad Request`**: Returned if the required parameters (aula and edificio) are missing or invalid.

```json
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
```
## **Docker Setup**

To run this application in a Docker container, follow these steps:

### 1. **Build the Docker image**:
First, build the Docker image for the Flask application using the following command:
```bash
docker build -t flask-app .
```
### 2. **Run the Docker container**:
After building the image, run the container with the following command:

```bash
docker run -p 5000:5000 flask-app
```
## **Testing**

The project includes unit tests to validate the API’s functionality using **unittest**. To run the tests, follow these steps:

### **Run the tests**:
To run the tests, use the following command:

```bash
python -m unittest testing_suit.py
```