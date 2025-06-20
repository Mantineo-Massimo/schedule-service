from app import create_app  # EN/IT: Import your factory function / Importa la tua factory function

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)
