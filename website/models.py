from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

# Importerer databasen 'db' fra det lokale miljøet

# Definerer User-klassen som representerer brukerne i databasen
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primærnøkkelen for brukertabellen
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    high_scores = db.relationship('HighScores', backref='user', lazy=True)  # Forhold til HighScore-tabellen
    user_role = db.Column(db.String(150))

# Definerer HighScore-klassen som representerer høye poengsummer i databasen
class HighScores(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    score = db.Column(db.Integer)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Fremmednøkkel som refererer til User-tabellen
    created_at = db.Column(db.DateTime(timezone=True), default=func.now()) 

# Definerer Note-klassen som representerer notatene i databasen
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    data = db.Column(db.Text, nullable=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Fremmednøkkel som refererer til User-tabellen
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())  


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Koble til bruker
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Lagre tidspunkt

    def __repr__(self):
        return f"<Files {self.filename}>"