"""
Defines all HTTP routes for the Schedule Display Service.
"""
import os
from flask import request, jsonify, send_from_directory, current_app, Blueprint
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from .models import LessonRequest
from .services import fetch_classroom_lessons, fetch_floor_lessons
from .constants import BUILDING_FLOOR_MAP

bp = Blueprint('main', __name__)

@bp.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Resource not found"}), 404

@bp.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    current_app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "An internal server error occurred"}), 500

@bp.route('/')
def index():
    return jsonify({"message": "Welcome to the Schedule Display API"})

@bp.route('/lessons', methods=['POST'])
def get_lessons():
    """Endpoint to get lessons for a single classroom."""
    try:
        req = LessonRequest(**request.get_json(force=True))
        lessons = fetch_classroom_lessons(req.classroom, req.building, req.date, req.period)
        return jsonify(lessons)
    except ValidationError as ve:
        return jsonify({"error": "Invalid request payload", "details": ve.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Error in /lessons endpoint: {e}")
        return jsonify({"error": "Failed to fetch lessons"}), 500

@bp.route('/floor/<string:building>/<string:floor>', methods=['GET'])
def get_floor_view(building: str, floor: str):
    """Endpoint to get all lessons for an entire floor."""
    try:
        floor_num = int(floor)
    except ValueError:
        return jsonify({"error": "Floor must be an integer"}), 400

    if building not in BUILDING_FLOOR_MAP or floor_num not in BUILDING_FLOOR_MAP[building]:
        return jsonify({"error": "Invalid building or floor number"}), 404

    date = request.args.get('date')
    lessons = fetch_floor_lessons(building, floor_num, date)
    return jsonify(lessons)

# --- Routes to Serve UI Files ---

@bp.route('/views/<path:filename>')
def serve_views(filename: str):
    """Serves the main HTML view files (classroom_view.html, floor_view.html)."""
    return send_from_directory(current_app.static_folder, filename)

@bp.route('/static/<path:path>')
def serve_static_files(path: str):
    """Serves static assets like CSS and JS files."""
    return send_from_directory(os.path.join(current_app.static_folder, 'static'), path)

@bp.route('/assets/<path:path>')
def serve_asset_files(path: str):
    """Serves assets like images and icons."""
    return send_from_directory(os.path.join(current_app.static_folder, 'assets'), path)

def register_routes(app):
    app.register_blueprint(bp)