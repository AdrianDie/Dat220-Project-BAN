# funksjon som vil opprette og konfigurere Flask-applikasjonen.
from website import create_app
from flask_socketio import SocketIO, emit
from flask_login import current_user
from website.queries import insert_chat 

# Denne funksjonen returnerer en Flask-app, som vi tilordner til variabelen `app`.
app = create_app()
socketio = SocketIO(app)

# Sjekk om skriptet kjøres som hovedprogrammet
if __name__ == '__main__':
    # Start Flask-webserveren i debug-modus.
    app.run(debug=True)
    socketio.run(app)

@socketio.on('message')
def chat_handler(message):
    message["username"] = current_user.username
    emit("chat", message, broadcast=True)
    insert_chat(current_user.id, message["message"])
