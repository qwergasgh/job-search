from werkzeug.security import generate_password_hash, check_password_hash
from flask_msearch import Search
from flask_login import UserMixin
from datetime import datetime
from app import db, login, app
import jwt



class Job(db.Model):
    __tablename__ = 'vacancies'
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(80), nullable=False)
    source = db.Column(db.String(80), nullable=False)


class TempJob(db.Model):
    __tablename__ = 'temp_vacancies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(80), nullable=False)
    source = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, index=True)

    def __init__(self, **kwargs):
        super(TempJob, self).__init__(**kwargs)
        if self.status is None:
            self.status = False


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phonenumber = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            self.role_id = Role.query.filter_by(privilege=False).first().id
        # else:
        #     self.role_id = Role.query.filter_by(privilege=True).first().id

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        if self.role_id == Role.query.filter_by(privilege=True).first().id:
            return True
        else:
            return False

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

# many to many !!!
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_vacancy = db.Column(db.Integer, db.ForeignKey('vacancies.id'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    privilege = db.Column(db.Boolean, index=True)


@login.user_loader
def user_loader(user_id):
    user = User.query.get(int(user_id))
    if user is None:
        return
    return user

# @login.unauthorized_handler
# def unauthorized_handler():
#    return 'unauthorized'

# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
# admin = Admin(app)
# admin.add_view(ModelView(Job, db.session))
# admin.add_view(ModelView(TempJob, db.session))
# admin.add_view(ModelView(Favorite, db.session))
# admin.add_view(ModelView(Role, db.session))
# admin.add_view(ModelView(User, db.session))