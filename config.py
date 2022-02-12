import os

app_dir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.join(app_dir + '/app/db_app.db')

class BaseConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app_dir + '/app/db_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    QSLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = 'my_secret_key'
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # ELASTICSEARCH_URL = {"hosts": ["127.0.0.1:9200"]}
    ADMINS = ['admin@mail.com']
    ROWS_PAGINATOR = 20
    WHOOSH_BASE = basedir
    WHOOSH_ANALYZER = 'StemmingAnalyzer'
    WHOOSH_INDEX_PATH = 'whooshSearch'
