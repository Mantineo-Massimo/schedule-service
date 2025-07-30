import os
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()

class Config:
    LESSON_API_BASE_URL = os.getenv('LESSON_API_BASE_URL', 'https://unime-public.prod.up.cineca.it')