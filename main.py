from website import create_app
from flask import request
from flask_socketio import SocketIO, emit
from website.queries import insert_chat, validate_session, get_user_by_id
from datetime import datetime

app = create_app()
socketio = SocketIO(app)

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)

@socketio.on('message')
def chat_handler(message):
    auth_token = request.cookies.get('auth_token')
    if auth_token:
        user_id = validate_session(auth_token)
        if user_id:
            user_data = get_user_by_id(user_id)
            message["username"] = user_data['username']
            message["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            emit("chat", message, broadcast=True)
            insert_chat(user_id, message["message"])