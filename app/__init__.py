"""
Application factory for the Schedule Display Service.
"""
import os
from flask import Flask
from flask_cors import CORS
from .routes import register_routes
from .config import load_configuration

def create_app():
    """Creates, configures, and returns the Flask application instance."""
    app = Flask(
        __name__,
        static_folder='../ui',
        static_url_path='' # Serve static content from the root URL
    )

    # Load configuration from .env and other sources
    load_configuration(app)
    
    # Enable Cross-Origin Resource Sharing (CORS) for all routes
    CORS(app)

    # Register all API and view routes
    register_routes(app)

    return app