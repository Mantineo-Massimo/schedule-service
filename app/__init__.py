"""
EN:
Application factory for the Flask web service.
This file is responsible for creating and configuring the Flask app instance.
It initializes all necessary extensions like CORS, Talisman for security,
the Redis connection, and loads all external configurations and registers the API blueprints.

IT:
"Application factory" per il servizio web Flask.
Questo file è responsabile della creazione e configurazione dell'istanza dell'app Flask.
Inizializza tutte le estensioni necessarie come CORS, Talisman per la sicurezza,
la connessione a Redis, carica le configurazioni esterne e registra i blueprint.
"""
import os
import json
import redis
from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

def load_classroom_data(app):
    """
    EN: Loads classroom and building data from a JSON file into the app config.
    IT: Carica i dati di aule e edifici da un file JSON nella configurazione dell'app.
    """
    file_path = os.path.join(app.root_path, '..', 'config', 'classroom_data.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            app.config['BUILDING_FLOOR_MAP'] = data['BUILDING_FLOOR_MAP']
            app.config['CLASSROOM_ID_TO_NAME'] = data['CLASSROOM_ID_TO_NAME']
    except Exception as e:
        app.logger.error(f"FATAL: Could not load classroom data from {file_path}. Error: {e}")

def create_app():
    """
    EN: Creates, configures, and returns the Flask application instance.
    IT: Crea, configura e restituisce l'istanza dell'applicazione Flask.
    """
    app = Flask(__name__, static_folder='../ui', template_folder='../ui')

    from .config import Config
    app.config.from_object(Config)

    # EN: Create a Redis connection pool and attach it to the app instance.
    # IT: Crea un pool di connessioni Redis e lo collega all'istanza dell'app.
    app.redis = redis.from_url(app.config['REDIS_URL'])

    # EN: Load the classroom data from the external JSON file.
    # IT: Carica i dati delle aule dal file JSON esterno.
    load_classroom_data(app)

    # EN: Initialize security extensions.
    # IT: Inizializza le estensioni di sicurezza.
    Talisman(app, content_security_policy=None, force_https=False)
    CORS(app)

    # EN: Register the blueprint containing all the routes.
    # IT: Registra il blueprint che contiene tutte le rotte.
    from .api.routes import api_bp
    app.register_blueprint(api_bp)

    return app