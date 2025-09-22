# EN:
# This is the main entry point to run the Flask application.
# It imports the app factory `create_app` and creates an instance of the app.
# This setup is standard for Flask and allows for a clean separation
# of app creation and app running, which is good for testing and deployment.
#
# IT:
# Questo è il punto di ingresso principale per avviare l'applicazione Flask.
# Importa la "app factory" `create_app` e crea un'istanza dell'app.
# Questa configurazione è standard per Flask e permette una netta separazione
# tra la creazione dell'app e la sua esecuzione, il che è ottimo per test e deploy.

from app import create_app

# EN: Create the application instance using the factory.
# IT: Crea l'istanza dell'applicazione usando la factory.
application = create_app()

# EN: This block runs the app in development mode when the script is executed directly.
# IT: Questo blocco avvia l'app in modalità sviluppo quando lo script è eseguito direttamente.
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=True)