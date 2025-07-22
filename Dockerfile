# ==============================================================================
# EN: Dockerfile for lession-kiosk-display
#     Minimal and production-ready image with Python, Flask, and uWSGI.
#
# IT: Dockerfile per lession-kiosk-display
#     Immagine minimale pronta per la produzione con Python, Flask e uWSGI.
# ==============================================================================

FROM python:3.11-slim

# EN/IT: Set working directory / Imposta directory di lavoro
WORKDIR /app

# EN/IT: Copy file requirements and install dependencies / Copia file requirements e installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# EN/IT: Copy the application code / Copia il codice dell’applicazione
COPY . .

# EN/IT: Expose the port on which the server will be listening / Esponi la porta su cui il server sarà in ascolto
EXPOSE 8080

# EN/IT: Start command with production server / Comando di avvio con server di produzione
CMD ["gunicorn", "--worker-class", "gevent", "--bind", "0.0.0.0:8080", "--timeout", "360", "run:app"]