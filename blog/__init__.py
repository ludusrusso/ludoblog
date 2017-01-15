from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_superadmin import Admin
from flask_misaka import Misaka

bootstrap = Bootstrap()
nav = Nav()
markdown = Misaka()

db = SQLAlchemy()
security = Security()
from .adminviews import ModelAdmin, AdminIndexView
admin=Admin(index_view=AdminIndexView())


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    nav.init_app(app)
    db.init_app(app)
    markdown.init_app()
    admin.init_app(app)

    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    admin.register(User, admin_class=ModelAdmin, session=db.session)
    admin.register(Role, admin_class=ModelAdmin, session=db.session)

    from .main import main as main_bp
    app.register_blueprint(main_bp)
    return app

from .navbar import main_nav
