import os

# app_dir = os.path.abspath(os.path.dirname(__file__))
# base_dir = os.path.join(app_dir, 'app/db_app.db')
# tmp = os.path.join(app_dir, 'app/tmp')

# add deploy config
class BaseConfig:
    # app
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    BASE_DIR = os.path.join(APP_DIR, 'app/db_app.db')
    TMP_DIR = os.path.join(APP_DIR, 'app/tmp')
    SECRET_KEY = 'my_secret_key'
    DEBUG = True
    # mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@mail.com']
    # pginate
    ROWS_PAGINATOR = 20
    # db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + BASE_DIR
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    QSLALCHEMY_COMMIT_ON_TEARDOWN = True
    # db whoosh
    WHOOSH_BASE = BASE_DIR
    WHOOSH_ANALYZER = 'StemmingAnalyzer'
    WHOOSH_INDEX_PATH = 'whooshSearch'
