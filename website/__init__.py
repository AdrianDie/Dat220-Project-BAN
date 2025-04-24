from flask import Flask


def create_app():
    # Oppretter en instans av Flask-applikasjonen.
    app = Flask(__name__)
    
    # Setter en hemmelig nøkkel som brukes av Flask for sikkerhet av feks. sensitiv data
    app.config['SECRET_KEY'] = 'b43k5ljnjb2k9vd33b3vh5k57b87k9'
        

    # Importerer og registrerer blueprints.
    from .views import views_bp
    from .auth import auth_bp

    # Registrerer blueprints med Flask-applikasjonen.
    app.register_blueprint(views_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')
    
    return app

