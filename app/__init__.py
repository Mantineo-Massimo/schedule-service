import os
from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

def create_app():
    """Crea, configura e restituisce l'istanza dell'applicazione Flask."""
    
    app = Flask(
        __name__,
        static_folder='../ui',
        template_folder='../ui'
    )

    # Carica la configurazione
    from .config import Config
    app.config.from_object(Config)
    
    # Inizializza le estensioni di sicurezza
    Talisman(app, content_security_policy=None, force_https=False)
    CORS(app)

    # Registra il blueprint che contiene tutte le rotte
    from .api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app