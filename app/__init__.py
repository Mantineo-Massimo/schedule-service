"""
EN: Application factory for Info_Kiosk_Display.
IT: Factory per l'inizializzazione dell'app Flask Info_Kiosk_Display.
"""

import os
from flask import Flask
from flask_cors import CORS
from app.routes import register_routes

def create_app():
    """
    EN: Create and configure the Flask app.
    IT: Crea e configura l'app Flask.
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(basedir, '..', 'web')

    app = Flask(
        __name__,
        static_folder=static_dir,
        static_url_path='/static'
    )

    CORS(app)  # EN: Enable CORS globally / IT: Abilita CORS globalmente
    register_routes(app)  # EN/IT: Record all routes of the app / Registra tutte le rotte dell'app

    return app

# EN/IT: Entry point for Gunicorn (production WSGI server) / Punto di ingresso per Gunicorn (server WSGI di produzione)
app = create_app()
