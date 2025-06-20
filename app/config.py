"""
EN: Configuration for external API endpoints.
IT: Configurazione per l'endpoint dell'API esterna.
"""

import os

BASE_URL = os.getenv(
    'LESSON_API_BASE_URL',
    'https://unime-public.prod.up.cineca.it'
)
