"""
EN:
Defines all the web routes for the service. This includes:
1. API endpoints that return JSON data (e.g., /lessons, /floor).
2. Routes for serving the static front-end files (HTML, CSS, JS).
3. A health check endpoint for monitoring.

IT:
Definisce tutte le rotte web per il servizio. Include:
1. Endpoint API che restituiscono dati JSON (es. /lessons, /floor).
2. Rotte per servire i file statici del front-end (HTML, CSS, JS).
3. Un endpoint di health check per il monitoraggio.
"""
import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from pydantic import ValidationError
from ..services.models import LessonRequest
from ..services.services import fetch_classroom_lessons, fetch_floor_lessons

api_bp = Blueprint('api', __name__)

# --- API Endpoints ---
@api_bp.route('/lessons', methods=['POST'])
def get_lessons():
    """
    EN: Fetches lessons for a specific classroom based on a JSON payload.
    IT: Recupera le lezioni per un'aula specifica in base a un payload JSON.
    """
    try:
        req = LessonRequest(**request.get_json(force=True))
        lessons = fetch_classroom_lessons(req.classroom, req.building, req.date, req.period)
        return jsonify(lessons)
    except ValidationError as e:
        return jsonify({"error": "Invalid request data", "details": e.errors()}), 400

@api_bp.route('/floor/<string:building>/<string:floor>', methods=['GET'])
def get_floor_view(building: str, floor: str):
    """
    EN: Fetches all lessons for an entire floor of a building.
    IT: Recupera tutte le lezioni per un intero piano di un edificio.
    """
    building_floor_map = current_app.config.get('BUILDING_FLOOR_MAP', {})
    try:
        floor_str = str(int(floor))
        building_key = building.upper()
        if building_key not in building_floor_map or floor_str not in building_floor_map.get(building_key, {}):
            return jsonify({"error": "Invalid building or floor number"}), 404
        date = request.args.get('date')
        lessons = fetch_floor_lessons(building_key, int(floor_str), date)
        return jsonify(lessons)
    except ValueError:
        return jsonify({"error": "Floor must be an integer"}), 400

# --- UI Serving Routes ---
@api_bp.route('/classroom_view.html')
def serve_classroom_view():
    """EN: Serves the classroom view HTML page. / IT: Serve la pagina HTML della vista aula."""
    return send_from_directory(current_app.template_folder, 'classroom_view.html')

@api_bp.route('/floor_view.html')
def serve_floor_view():
    """EN: Serves the floor view HTML page. / IT: Serve la pagina HTML della vista piano."""
    return send_from_directory(current_app.template_folder, 'floor_view.html')

@api_bp.route('/static/<path:path>')
def serve_static_files(path: str):
    """EN: Serves static files (CSS, JS). / IT: Serve file statici (CSS, JS)."""
    return send_from_directory(os.path.join(current_app.static_folder, 'static'), path)

@api_bp.route('/assets/<path:path>')
def serve_assets(path: str):
    """EN: Serves asset files (images, fonts). / IT: Serve file di risorse (immagini, font)."""
    return send_from_directory(os.path.join(current_app.static_folder, 'assets'), path)

@api_bp.route('/favicon.ico')
def favicon():
    """EN: Serves the favicon. / IT: Serve la favicon."""
    return send_from_directory(os.path.join(current_app.static_folder, 'assets'), 'favicon.ico')

# --- Monitoring Endpoint ---
@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    EN: A simple endpoint to verify that the service is running and responsive.
    IT: Un endpoint semplice per verificare che il servizio sia in esecuzione e reattivo.
    """
    return jsonify({"status": "ok"}), 200