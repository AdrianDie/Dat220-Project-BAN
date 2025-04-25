from flask import Flask


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'b43k5ljnjb2k9vd33b3vh5k57b87k9'

    from .views import views_bp
    from .auth import auth_bp
    
    app.register_blueprint(views_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')
    
    return app

