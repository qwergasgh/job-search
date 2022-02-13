from flask_whooshalchemy3 import search_index
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask import Flask, current_app
from config import BaseConfig
from flask_mail import Mail
import os



def status_tmp():
    with app.app_context():
        if not os.path.isdir(current_app.config['TMP_DIR']):
            try:
                os.mkdir(current_app.config['TMP_DIR'])
            except:
                return


def create_blueprints():
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


def create_index():
    from .models import Job
    search_index(app, Job)


app = Flask(__name__)
app.config.from_object(BaseConfig)

csrf = CSRFProtect(app)

db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    db.create_all()

mail = Mail(app)

login = LoginManager(app)
login.session_protection = 'strong'

create_blueprints()
create_index()
status_tmp()

login.login_view = 'blueprint_user.login'


