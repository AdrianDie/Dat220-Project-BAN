# funksjon som vil opprette og konfigurere Flask-applikasjonen.
from website import create_app

# Denne funksjonen returnerer en Flask-app, som vi tilordner til variabelen `app`.
app = create_app()

# Sjekk om skriptet kjøres som hovedprogrammet
if __name__ == '__main__':
    # Start Flask-webserveren i debug-modus.
    app.run(debug=True)
