"""
EN:
Manages application configuration by loading environment variables from a .env file.
This approach separates configuration from code, which is a security and maintenance best practice.

IT:
Gestisce la configurazione dell'applicazione caricando variabili d'ambiente da un file .env.
Questo approccio separa la configurazione dal codice, una best practice di sicurezza e manutenzione.
"""
import os
from dotenv import load_dotenv

# EN: Load environment variables from the .env file.
# IT: Carica le variabili d'ambiente dal file .env.
load_dotenv()

class Config:
    """
    EN: A configuration class to hold all settings, with default fallbacks.
    IT: Una classe di configurazione per contenere tutte le impostazioni, con fallback predefiniti.
    """
    LESSON_API_BASE_URL = os.getenv('LESSON_API_BASE_URL', 'https://unime-public.prod.up.cineca.it')
    CACHE_TTL_MINUTES = int(os.getenv('CACHE_TTL_MINUTES', 15))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')