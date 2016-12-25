from flask import Flask

def create_app():
    app = Flask(__name__)

    from .main import main as main_bp
    app.register_blueprint(main_bp)
    return app
