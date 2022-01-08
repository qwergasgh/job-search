from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

class Job(db.Model):
    __tablename__ = 'vacancies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(80), nullable=False)

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
            self.role_id = Role.query.filter_by(default=False).first()
        else:
            self.role_id = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_vacancy = db.Column(db.Integer, db.ForeignKey('vacancies.id'))

 class Role(db.Model):
     __tablename__ = 'roles'
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(80), nullable=False)
     users = db.relationship('User', backref='role')
     default = db.Column(db.Boolean, default=False, index=True)

     @staticmethod
     def insert_roles():
         roles = { 'User': False, 'Administrator': True }
         for r in roles:
             role = Role.query.filter_by(name=r).first()
             if role is None:
                 role = Role(name=r)
             role.default = roles[r][1]
             db.session.add(role)
         db.session.commit()

@login.user_loader
def user_loader(user_id):
    user = User.query.get(int(user_id))
    if user is None:
        return
    return user

#@login.unauthorized_handler
#def unauthorized_handler():
#    return 'unauthorized'