# Campus Lesson Kiosk API

This Flask application provides lesson schedule data in JSON format for use in campus information kiosks.

## Features
- Fetches lesson schedule data from the university API.
- Converts raw data into a more user-friendly format with readable date and time.
- Returns the data as JSON via a REST API endpoint.

## API Endpoint
- **GET /lessons**: Returns a list of lessons with `start_time`, `end_time`, `lesson_name`, and `instructor`.

### Example Response
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
