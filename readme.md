# **Campus Lesson Kiosk API**

This Flask-based application provides lesson schedule data in JSON format for campus information kiosks. It fetches and alternates between morning and afternoon lessons every 15 seconds. It also uses **Pydantic** for input and output validation. The application is fully containerized using **Docker** for consistent deployment across different environments.

---

## **Features**
- Fetches lesson schedule data from the university API.
- Alternates between **morning** and **afternoon** classes every 15 seconds in a single API route.
- Validates both input and output using **Pydantic**.
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
## Running in Debug Mode

In production, debug mode is disabled by default. If you need to run the application in debug mode (for local development), set the `FLASK_DEBUG` environment variable to `1`:

```bash
export FLASK_DEBUG=1
```

### Testing & Running:

1. **Build the Docker image**:
   ```bash
   docker build -t flask-app .
   ```
2. **Running the Docker container**:
    ```bash
    docker run -p 5000:5000 flask-app
   
# Testing Guide

This guide explains how to set up, run, and write tests for the project.

## 1. Test Structure

The tests are organized to cover different aspects of the application, including:

### 1.1. **Validation Tests**
Tests that check whether the input parameters are valid. This includes ensuring the classroom (`aula`) and building (`edificio`) parameters are passed correctly.

- **Valid input test**: Ensures that valid `aula` and `edificio` values return a 200 status code.
- **Missing parameter tests**: Ensures that missing `aula` or `edificio` results in a 400 status code.
- **Invalid parameter length tests**: Ensures that an `aula` or `edificio` exceeding the allowed length (30 characters) returns a 400 status code.

### 1.2. **API Response Tests**
These tests validate that the API returns the correct data format when valid parameters are passed.

- **Valid response test**: Ensures that the API returns the expected JSON format for a valid request.

### 1.3. **Error Handling Tests**
Tests that validate how the application handles errors and exceptions.

- **General exception handling**: Ensures that unhandled exceptions return a proper error message and status code.

### 1.4. **Cache Tests**
Tests that validate if caching is working as expected to reduce the need for repeated API calls.

## 2. How to Run the Tests

Make sure that the project has the following Python libraries installed:

- `unittest`
- `requests`
- `pydantic`

### 2.1. Installing dependencies

If the dependencies are not installed, use:

```bash
pip install -r requirements.txt
```
### 2.2. Running the tests

To run the tests, use the following command:

```bash
pypthon -m unittest discover -s tests -p "*.py"

```
Please make sure to be in the main directory before


-----------

## Configuration

### Environment Variables

This application requires the following environment variable to be set:

#### `LESSON_API_BASE_URL`

- **Description**: This variable is used to specify the base URL for the lesson API. It is essential for the application to fetch the lesson schedule from the university's system.
- **Default**: If not set, the application defaults to: `https://unime-public.prod.up.cineca.it`
- **Usage**:
  - When running the app, set the environment variable `LESSON_API_BASE_URL` to the desired API base URL.
  - This URL will be used to fetch lesson schedule data for classrooms and buildings.

#### Example

You can set the environment variable in different ways depending on your operating system:

- **On Windows (Command Prompt)**:
    ```bash
    set LESSON_API_BASE_URL=https://your-api-url.com
    ```

- **On Linux/macOS**:
    ```bash
    export LESSON_API_BASE_URL=https://your-api-url.com
    ```

- **In Docker (via Dockerfile)**:
    You can set it in the Dockerfile like this:
    ```dockerfile
    ENV LESSON_API_BASE_URL=https://your-api-url.com
    ```

#### Example Usage with Docker

If you're using Docker, you can either set the environment variable in the Dockerfile or pass it in when running the container:

```bash
docker run -e LESSON_API_BASE_URL=https://your-api-url.com -p 5000:5000 your-docker-image
```
Make sure to replace https://your-api-url.com with the actual base URL you want to use for fetching lesson data.

## Project Overview

This project was developed as part of a **part-time** work assignment. The goal was to build a system that fetches and displays lesson schedule data for the University of Messina (UNIME) campus, making it suitable for deployment on campus information kiosks. The project includes input validation, caching mechanisms, and API calls to fetch the lesson data in real-time.

