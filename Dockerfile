# Dockerfile for schedule-display-service (production with Gunicorn)
FROM python:3.11-slim

# Set environment variables for optimized execution
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app ./app
COPY ui ./ui
COPY run.py .
COPY .env .

# Expose the port Gunicorn will run on
EXPOSE 8080

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:application"]