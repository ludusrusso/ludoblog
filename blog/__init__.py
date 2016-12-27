from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav

bootstrap = Bootstrap()
nav = Nav()

def create_app():
    app = Flask(__name__)

    bootstrap.init_app(app)

    nav.init_app(app)

    from .main import main as main_bp
    app.register_blueprint(main_bp)
    return app

from .navbar import main_nav
