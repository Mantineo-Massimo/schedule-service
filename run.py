"""
WSGI entrypoint for the Schedule Display Service.
Initializes the Flask application for production servers like Gunicorn.
"""
from app import create_app

# Gunicorn will look for this `application` variable by default.
application = create_app()

if __name__ == '__main__':
    # This block is for local development only.
    # It allows running the app directly with 'python run.py'.
    print("Starting Flask development server on http://localhost:8080")
    application.run(host='0.0.0.0', port=8080, debug=True)