from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Definerer User-klassen som representerer brukerne i databasen
class User(db.Model, UserMixin):
    __tablename__ = 'user' # Spesifiserer tabellnavn eksplisitt for klarhet
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # Matcher NOT NULL i create.py
    password = db.Column(db.String(150), nullable=False) # Matcher NOT NULL i create.py
    user_role = db.Column(db.String(150), nullable=False) # Matcher NOT NULL i create.py

    # Relasjoner (cascade delete håndteres i DB-skjema med ON DELETE CASCADE)
    high_scores = db.relationship('HighScores', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True) # Lagt til relasjon for notes
    files = db.relationship('Files', backref='user', lazy=True) # Lagt til relasjon for files
    comments = db.relationship('Comments', backref='user', lazy=True) # Relasjon for comments

# Definerer HighScore-klassen
class HighScores(db.Model):
    __tablename__ = 'high_scores' # Spesifiserer tabellnavn
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False) # Matcher NOT NULL i create.py
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False) # Matcher NOT NULL og FK
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now()) # Bruker server_default

# Definerer Note-klassen
class Note(db.Model):
    __tablename__ = 'note' # Spesifiserer tabellnavn
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False) # Matcher NOT NULL i create.py
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False) # Matcher NOT NULL og FK
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now()) # Bruker server_default

# Definerer Files-klassen
class Files(db.Model):
    __tablename__ = 'Files' # Spesifiserer tabellnavn (case-sensitive i koden, men bør matche create.py)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False) # Matcher NOT NULL og FK
    filename = db.Column(db.String(255), nullable=False) # Matcher NOT NULL i create.py
    uploaded_at = db.Column(db.DateTime, server_default=func.now()) # Bruker server_default

    def __repr__(self):
        return f"<Files {self.filename}>"

# ---------- VIKTIGE ENDRINGER HER ----------
# Fjernet den overflødige Comment-klassen:
# class Comment(db.Model):
#     ... (gammel kode her) ...

# Definerer Comments-klassen (den vi bruker) - Sjekk at den matcher databasen
class Comments(db.Model):
    __tablename__ = 'Comments' # Spesifiserer tabellnavn
    id = db.Column(db.Integer, primary_key=True)
    # Bruker 'user.id' som ForeignKey og legger til ondelete='CASCADE' for å matche DB-skjema
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    page = db.Column(db.String(100), nullable=False) # Kolonnen fra create.py
    content = db.Column(db.Text, nullable=False)     # Kolonnen fra create.py
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now()) # Bruker server_default

    # 'user' relasjonen er allerede definert i User-klassen via backref='comments'
    # så vi trenger ikke definere den på nytt her, men vi kan hvis vi vil for klarhet:
    # user = db.relationship('User', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        # Henter brukernavn via relasjonen hvis mulig (krever at user er lastet)
        username = self.user.username if self.user else f"UserID: {self.user_id}"
        return f"<Comment {self.id} by {username} on Page '{self.page}'>"
# ---------- SLUTT PÅ VIKTIGE ENDRINGER ----------