from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Oppretter en instans av SQLAlchemy-objektet. Dette vil bli brukt til å interagere med databasen.
db = SQLAlchemy()

# Definerer navnet på databasefilen.
DB_NAME = "database.db"

def create_app():
    # Oppretter en instans av Flask-applikasjonen.
    app = Flask(__name__)
    
    # Setter en hemmelig nøkkel som brukes av Flask for sikkerhet av feks. sensitiv data
    app.config['SECRET_KEY'] = 'b43k5ljnjb2k9vd33b3vh5k57b87k9'
    
    # Konfigurerer URI for SQLite-databasen.
    # Denne konfigurasjonen er nødvendig for at SQLAlchemy skal vite hvor databasen er og hvordan den skal koble til den når du bruker modeller og spørringer i Flask-applikasjonen din.
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Initialiserer databasen med Flask-applikasjonen.
    db.init_app(app)

    # Importerer og registrerer blueprints.
    from .views import views_bp
    from .auth import auth_bp

    # Registrerer blueprints med Flask-applikasjonen.
    app.register_blueprint(views_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')

    # Importerer User-modellen for å sikre at den er kjent for SQLAlchemy.
    from .models import User
    
    # Oppretter alle databasetabeller hvis de ikke allerede eksisterer.
    with app.app_context():
        db.create_all()

    # Setter opp Flask-Login.
    login_manager = LoginManager()
    
    # Definerer hvilken side brukerne skal omdirigeres til ved forsøk på å få tilgang til en beskyttet side uten å være innlogget.
    login_manager.login_view = 'auth_bp.login'
    
    # Initialiserer Flask-Login med applikasjonen.
    login_manager.init_app(app)

    # Definerer en callback for å laste inn en bruker fra databasen ved hjelp av bruker-ID.
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

