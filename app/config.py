"""
Configuration management for the application.
"""
import os
from dotenv import load_dotenv
from flask import Flask

def load_configuration(app: Flask):
    """Loads configuration from .env file and sets it on the app object."""
    load_dotenv()
    
    app.config['LESSON_API_BASE_URL'] = os.getenv(
        'LESSON_API_BASE_URL'
    )
    app.config['CACHE_TTL_MINUTES'] = int(os.getenv('CACHE_TTL_MINUTES', '15'))