# EN: Use an official lightweight Python runtime as a parent image.
# IT: Usa un'immagine Python ufficiale e leggera come immagine di base.
FROM python:3.11-slim

# EN: Set environment variables for optimized Python execution.
# IT: Imposta variabili d'ambiente per un'esecuzione Python ottimizzata.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# EN: Set the working directory inside the container.
# IT: Imposta la directory di lavoro all'interno del container.
WORKDIR /app

# EN: Copy the dependencies file and install them.
# IT: Copia il file delle dipendenze e le installa.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# EN: Copy all necessary application files into the container.
# IT: Copia tutti i file necessari dell'applicazione nel container.
COPY app ./app
COPY ui ./ui
COPY config ./config
COPY run.py .

# EN: Expose the port the app runs on.
# IT: Esponi la porta su cui l'applicazione è in esecuzione.
EXPOSE 8080

# EN: The command to run the application using Gunicorn WSGI server for production.
# IT: Il comando per avviare l'applicazione usando il server WSGI Gunicorn per la produzione.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:application"]