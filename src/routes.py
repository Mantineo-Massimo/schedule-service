from flask import request, jsonify
from pydantic import ValidationError
from src.services import LessonLooper
from src.models import LessonRequest, LessonResponse

lesson_looper = None

def register_routes(app):
    # General exception handler for all routes
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception if necessary
        print(f"Unhandled exception: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

    @app.route('/lessons', methods=['GET'])
    def get_lessons():
        try:
            global lesson_looper
            aula = request.args.get('aula')
            edificio = request.args.get('edificio')

            # Validate inputs using Pydantic
            LessonRequest(aula=aula, edificio=edificio)

            # Initialize the lesson looper if it's not already started
            if lesson_looper is None:
                lesson_looper = LessonLooper(aula, edificio)
                lesson_looper.fetch_and_split()

            # Get current classes (morning/afternoon)
            current_classes = lesson_looper.get_current_classes()

            # Ensure current_classes is not None
            if not current_classes:
                return jsonify({"error": "No classes available"}), 404

            # Format and return the classes
            formatted_classes = [
                LessonResponse(
                    start_time=lesson.get("dataInizio", "N/A"),
                    end_time=lesson.get("dataFine", "N/A"),
                    lesson_name=lesson.get("evento", {}).get("dettagliDidattici", [{}])[0].get("nome", "N/A"),
                    instructor=f'{lesson.get("docenti", [{}])[0].get("nome", "N/A")} {lesson.get("docenti", [{}])[0].get("cognome", "N/A")}'
                ).model_dump()
                for lesson in current_classes
            ]

            return jsonify(formatted_classes)

        except ValidationError as e:
            return jsonify({"error": e.errors()}), 400

        except Exception as e:
            # Catch-all for any unexpected exceptions
            print(f"Error in /lessons route: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500
