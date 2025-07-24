import os
from flask import Flask
from flask_cors import CORS
from .routes import register_routes
from flask_talisman import Talisman
from dotenv import load_dotenv

def create_app():
    """Crea, configura e restituisce l'istanza dell'applicazione Flask."""
    
    app = Flask(
        __name__,
        template_folder='../ui',
        static_folder='../ui'
    )

    # Carica le variabili dal file .env nella configurazione di Flask
    load_dotenv()
    app.config['LESSON_API_BASE_URL'] = os.getenv('LESSON_API_BASE_URL')
    
    Talisman(app, content_security_policy=None, force_https=False)
    CORS(app)
    register_routes(app)
    
    return app