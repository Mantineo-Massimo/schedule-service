"""
EN: API and frontend route definitions.
IT: Definizione delle rotte API e delle pagine frontend.
"""

import os
from flask import request, jsonify, send_file, send_from_directory
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.models    import LessonRequest, LessonResponse
from app.services  import LessonLooper, get_active_or_soon_lessons
from app.constants import FLOOR_CLASSROOMS

def register_routes(app):
    """
    EN: Register all routes for the application.
    IT: Registra tutte le rotte dell'applicazione.
    """

    @app.errorhandler(404)
    def handle_404(e):
        # EN/IT: Handler for route not found / Handler per route non trovate
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        # EN/IT: Handler for generic exceptions / Handler per eccezioni generiche
        if isinstance(e, HTTPException):
            return e
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/')
    def index():
        # EN/IT: Need the main page / Serve la pagina principale
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/lessons', methods=['POST'])
    def lessons():
        """
        EN: Return lessons for a classroom by date and period.
        IT: Restituisce le lezioni per un'aula, filtrate per data e fascia oraria.
        """
        try:
            payload = request.get_json(force=True)
            req = LessonRequest(**payload)

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
                    "message": "No classes available"
                }])

            result = []
            for l in classes:
                resp = LessonResponse(
                    start_time     = l.get("dataInizio", "N/A"),
                    end_time       = l.get("dataFine",   "N/A"),
                    lesson_name    = l.get("evento",{}).get("dettagliDidattici",[{}])[0].get("nome","N/A"),
                    instructor     = f'{l.get("docenti",[{}])[0].get("nome","")} {l.get("docenti",[{}])[0].get("cognome","")}',
                    classroom_name = l.get("aule",[{}])[0].get("descrizione","N/A")
                )
                result.append(resp.model_dump())

            return jsonify(result)

        except ValidationError as ve:
            return jsonify({"error": ve.errors()}), 400

    @app.route('/floor/<floor>', methods=['GET'])
    def floor_view(floor):
        """
        EN: Return all lessons for a floor.
        IT: Restituisce tutte le lezioni di un piano.
        """
        floor_key = floor.lower()
        if floor_key not in FLOOR_CLASSROOMS:
            return jsonify({"error": "Invalid floor"}), 400

        date = request.args.get("date")
        lessons = get_active_or_soon_lessons(floor_key, date)
        return jsonify(lessons)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        # EN/IT: Serve static files from poster resources / Serve file statici dalla cartella assets
        asset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web', 'assets'))
        file_path = os.path.join(asset_dir, filename)
        if not os.path.isfile(file_path):
            app.logger.error(f"Asset not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        return send_file(file_path)

    @app.route('/favicon.ico')
    def favicon():
        # EN/IT: Need favicon / Serve favicon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web/assets/favicon.ico'))
        return send_file(icon_path)
