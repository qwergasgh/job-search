from werkzeug.security import generate_password_hash, check_password_hash
from whoosh.analysis import StemmingAnalyzer
from flask_login import UserMixin
from app import db, login, app
from datetime import datetime
import jwt



class TempJob(db.Model):
    __tablename__ = 'TempJob'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(80), nullable=False)
    source = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, index=True)

    def __init__(self, **kwargs):
        super(TempJob, self).__init__(**kwargs)
        if self.status is None:
            self.status = False


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id'), nullable=False)
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
    __tablename__ = 'Favorite'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('User.id'))
    id_vacancy = db.Column(db.Integer, db.ForeignKey('Job.id'))


class Role(db.Model):
    __tablename__ = 'Role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    privilege = db.Column(db.Boolean, index=True)


@login.user_loader
def user_loader(user_id):
    user = User.query.get(int(user_id))
    if user is None:
        return
    return user


class Job(db.Model):
    __tablename__ = 'Job'
    __searchable__ = ['title']
    __analyzer__ = StemmingAnalyzer()
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(80), nullable=False)
    source = db.Column(db.String(80), nullable=False)
