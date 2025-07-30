import os
from flask import (
    Blueprint, jsonify, request, send_from_directory,
    current_app, abort
)
from pydantic import ValidationError

# MODIFICA: Aggiornati i percorsi di import per la nuova struttura
from ..services.models import LessonRequest
from ..services.services import fetch_classroom_lessons, fetch_floor_lessons
from ..services.constants import BUILDING_FLOOR_MAP

api_bp = Blueprint('api', __name__)

# --- Rotte API ---
@api_bp.route('/lessons', methods=['POST'])
def get_lessons():
    req = LessonRequest(**request.get_json(force=True))
    lessons = fetch_classroom_lessons(req.classroom, req.building, req.date, req.period)
    return jsonify(lessons)

@api_bp.route('/floor/<string:building>/<string:floor>', methods=['GET'])
def get_floor_view(building: str, floor: str):
    floor_num = int(floor)
    building_key = building.upper()
    if building_key not in BUILDING_FLOOR_MAP or floor_num not in BUILDING_FLOOR_MAP.get(building_key, {}):
        return jsonify({"error": "Invalid building or floor number"}), 404
    date = request.args.get('date')
    lessons = fetch_floor_lessons(building_key, floor_num, date)
    return jsonify(lessons)

# --- Rotte per Servire i File dell'Interfaccia Utente ---
@api_bp.route('/classroom_view.html')
def serve_classroom_view():
    return send_from_directory(current_app.template_folder, 'classroom_view.html')

@api_bp.route('/floor_view.html')
def serve_floor_view():
    return send_from_directory(current_app.template_folder, 'floor_view.html')

@api_bp.route('/static/<path:path>')
def serve_static_files(path: str):
    return send_from_directory(os.path.join(current_app.static_folder, 'static'), path)

@api_bp.route('/assets/<path:path>')
def serve_assets(path: str):
    return send_from_directory(os.path.join(current_app.static_folder, 'assets'), path)

@api_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.static_folder, 'assets'), 'favicon.ico')