from app import create_app

# Gunicorn cerca questa variabile 'application' di default
application = create_app()

if __name__ == '__main__':
    # Avvia il server di sviluppo solo se il file viene eseguito direttamente
    application.run(host='0.0.0.0', port=8080, debug=True)