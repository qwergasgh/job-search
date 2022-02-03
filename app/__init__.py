from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import BaseConfig
from flask import Flask
from flask_mail import Mail
# from flask_msearch import Search


app = Flask(__name__)
app.config.from_object(BaseConfig)

csrf = CSRFProtect(app)

db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    db.create_all()

mail = Mail(app)
# search = Search(db=db)
# search.init_app(app)


login = LoginManager(app)
login.session_protection = 'strong'
login.login_view = 'blueprint_app.login'

from .views import blueprint_app
from .errors import blueprint_errors
from .vacancies import blueprint_vacancies
from .user import blueprint_user

app.register_blueprint(blueprint_app)
app.register_blueprint(blueprint_errors)
app.register_blueprint(blueprint_vacancies, url_prefix="/vacancies")
app.register_blueprint(blueprint_user, url_prefix="/user")




