# app/routes.py

import os
from flask import request, jsonify, send_file, current_app as app
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.models    import LessonRequest, LessonResponse
from app.services  import LessonLooper, get_active_or_soon_lessons
from app.constants import FLOOR_CLASSROOMS

def register_routes(app):
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/')
    def index():
        return send_file(os.path.join(app.static_folder, 'index.html'))

    @app.route('/lessons', methods=['POST'])
    def lessons():
        try:
            payload = request.get_json(force=True)
            req     = LessonRequest(**payload)

            loop = LessonLooper(req.classroom, req.building, req.date)
            loop.fetch_and_split()

            if req.period == "morning":
                classes = loop.morning_classes
            elif req.period == "afternoon":
                classes = loop.afternoon_classes
            else:
                classes = loop.morning_classes + loop.afternoon_classes

            if not classes:
                return jsonify([{
                    "classroom_name": loop.classroom_name,
                    "message":        "No classes available"
                }])

            result = []
            for l in classes:
                # EN/IT: Safe extraction of first docente (instructor)
                docenti_list = l.get("docenti") or []
                docente = docenti_list[0] if docenti_list else {}
                nome    = docente.get("nome", "").strip()
                cognome = docente.get("cognome", "").strip()
                instructor = f"{nome} {cognome}".strip() or "N/A"

                # EN/IT: Safe extraction of first aula (classroom)
                aule_list      = l.get("aule") or []
                aula_info      = aule_list[0] if aule_list else {}
                classroom_name = aula_info.get("descrizione", "N/A")

                resp = LessonResponse(
                    start_time     = l.get("dataInizio", "N/A"),
                    end_time       = l.get("dataFine",   "N/A"),
                    lesson_name    = l.get("evento",{}) \
                                       .get("dettagliDidattici",[{}])[0] \
                                       .get("nome","N/A"),
                    instructor     = instructor,
                    classroom_name = classroom_name
                )
                result.append(resp.model_dump())

            return jsonify(result)

        except ValidationError as ve:
            return jsonify({"error": ve.errors()}), 400

    @app.route('/floor/<floor>', methods=['GET'])
    def floor_view(floor):
        floor_key = floor.lower()
        if floor_key not in FLOOR_CLASSROOMS:
            return jsonify({"error": "Invalid floor"}), 400

        date    = request.args.get("date")
        lessons = get_active_or_soon_lessons(floor_key, date)
        return jsonify(lessons)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        asset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'assets'))
        file_path = os.path.join(asset_dir, filename)

        if not os.path.isfile(file_path):
            app.logger.error(f"Asset not found: {file_path}")
            return jsonify({"error": "File not found"}), 404

        return send_file(file_path)

    @app.route('/favicon.ico')
    def favicon():
        return '', 204
