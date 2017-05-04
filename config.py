import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'stringa difficile da indovinare'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = 'True'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLOG_ADMIN_MAIL = os.environ.get('BLOG_ADMIN_MAIL') or 'admin@admin.com'
    BLOG_ADMIN_PASSWORD = os.environ.get('BLOG_ADMIN_PASSWORD') or 'admin'
    PAGE_ELEM_NUMBER = 5

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
