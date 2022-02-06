from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import BaseConfig
from flask import Flask
from flask_mail import Mail
from elasticsearch import Elasticsearch


app = Flask(__name__)
app.config.from_object(BaseConfig)

csrf = CSRFProtect(app)

db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    db.create_all()

mail = Mail(app)

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])

login = LoginManager(app)
login.session_protection = 'strong'

from .views import blueprint_app
from .errors import blueprint_errors
from .vacancies import blueprint_vacancies
from .user import blueprint_user
from .parsing_result import blueprint_parsing_result
from .search import blueprint_search
from .report import blueprint_report

app.register_blueprint(blueprint_app)
app.register_blueprint(blueprint_errors)
app.register_blueprint(blueprint_vacancies, url_prefix="/vacancies")
app.register_blueprint(blueprint_user, url_prefix="/user")
app.register_blueprint(blueprint_parsing_result, url_prefix="/parsing-result")
app.register_blueprint(blueprint_search, url_prefix="/search")
app.register_blueprint(blueprint_report, url_prefix="/report")

login.login_view = 'blueprint_user.login'


