import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app_dir + '/app/db_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QSLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = 'my_secret_key'
    DEBUG = True
