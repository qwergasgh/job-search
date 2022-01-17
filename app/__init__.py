from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import BaseConfig
from flask import Flask

app = Flask(__name__)
app.config.from_object(BaseConfig)

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
db.init_app(app)

login = LoginManager(app)
login.session_protection = 'strong'
login.login_view = 'blueprint_app.login'

from .views import blueprint_app

app.register_blueprint(blueprint_app)
