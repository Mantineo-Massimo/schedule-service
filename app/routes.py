import os
from flask import (
    Blueprint, jsonify, request, send_from_directory,
    current_app
)
from .models import LessonRequest
from .services import fetch_classroom_lessons, fetch_floor_lessons
from .constants import BUILDING_FLOOR_MAP

bp = Blueprint('main', __name__)

# --- Rotte API (per recuperare i dati JSON) ---
@bp.route('/lessons', methods=['POST'])
def get_lessons():
    req = LessonRequest(**request.get_json(force=True))
    lessons = fetch_classroom_lessons(req.classroom, req.building, req.date, req.period)
    return jsonify(lessons)

@bp.route('/floor/<string:building>/<string:floor>', methods=['GET'])
def get_floor_view(building: str, floor: str):
    floor_num = int(floor)
    building_key = building.upper()
    if building_key not in BUILDING_FLOOR_MAP or floor_num not in BUILDING_FLOOR_MAP[building_key]:
        return jsonify({"error": "Invalid building or floor number"}), 404
    date = request.args.get('date')
    lessons = fetch_floor_lessons(building_key, floor_num, date)
    return jsonify(lessons)

# --- Rotte per Servire i File dell'Interfaccia Utente ---
@bp.route('/classroom_view.html')
def serve_classroom_view():
    return send_from_directory(current_app.template_folder, 'classroom_view.html')

@bp.route('/floor_view.html')
def serve_floor_view():
    return send_from_directory(current_app.template_folder, 'floor_view.html')

@bp.route('/static/<path:path>')
def serve_static_files(path: str):
    static_dir = os.path.join(current_app.static_folder, 'static')
    return send_from_directory(static_dir, path)

@bp.route('/assets/<path:path>')
def serve_assets(path: str):
    assets_dir = os.path.join(current_app.static_folder, 'assets')
    return send_from_directory(assets_dir, path)

def register_routes(app):
    app.register_blueprint(bp)