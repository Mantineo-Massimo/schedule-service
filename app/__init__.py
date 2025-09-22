"""
EN:
Application factory for the Flask web service.
This file is responsible for creating and configuring the Flask app instance.
It initializes all necessary extensions like CORS, Talisman for security,
the Redis connection, and the Limiter for rate-limiting. It also loads
all external configurations and registers the API blueprints.

IT:
"Application factory" per il servizio web Flask.
Questo file è responsabile della creazione e configurazione dell'istanza dell'app Flask.
Inizializza tutte le estensioni necessarie come CORS, Talisman per la sicurezza,
la connessione a Redis e il Limiter per il rate-limiting. Carica inoltre
tutte le configurazioni esterne e registra i blueprint delle API.
"""
import os
import json
import redis
from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

    # EN: Create a Redis connection pool and attach it to the app.
    # IT: Crea un pool di connessioni Redis e lo collega all'app.
    app.redis = redis.from_url(app.config['REDIS_URL'])

    # EN: Load the classroom data from the external JSON file.
    # IT: Carica i dati delle aule dal file JSON esterno.
    load_classroom_data(app)

    # EN: Initialize the Limiter to use Redis as its storage backend.
    # IT: Inizializza il Limiter affinché usi Redis come memoria.
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config["REDIS_URL"]
    )

    # EN: Initialize security extensions.
    # IT: Inizializza le estensioni di sicurezza.
    Talisman(app, content_security_policy=None, force_https=False)
    CORS(app)

    # EN: Register the blueprint containing all the routes.
    # IT: Registra il blueprint che contiene tutte le rotte.
    from .api.routes import api_bp
    app.register_blueprint(api_bp)

    # EN: Apply a more specific rate limit to all routes in the blueprint.
    # IT: Applica un limite di richieste più specifico a tutte le rotte nel blueprint.
    limiter.limit("10 per minute")(api_bp)

    return app