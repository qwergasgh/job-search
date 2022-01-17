from wtforms import PasswordField, SubmitField, StringField, IntegerField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from flask_wtf import FlaskForm
from .models import User


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(),
                                            Length(1, 64),
                                            Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # first_name = StringField('First name', validators=[DataRequired()])
    # last_name = StringField('Last name', validators=[DataRequired()])
    # phonenumber = IntegerField('Phonenumber', validators=[DataRequired()])
    submit = SubmitField('Login')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        print(initial_validation)
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Unknown email')
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        return True


class RegisterForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired(), Length(min=3, max=64),
                                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                           "Usernames must have only letters, numbers, dots or "
                                                           "underscores")])
    email = EmailField('Email',
                       validators=[DataRequired(), Email(), Length(min=3, max=64)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('Verify password',
                            validators=[DataRequired(), EqualTo('password',
                                                                message='Passwords must match')])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=3, max=64)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=3, max=64)])
    phonenumber = StringField('Phonenumber', validators=[DataRequired(), Length(min=10, max=12),
                                                         Regexp('[0-9]', 0, "Phonenumber must have only numbers")])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(user_name=self.user_name.data).first()
        if user:
            self.user_name.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class SearchForm(FlaskForm):
    query_search = StringField('Query search', validators=[DataRequired(), Length(min=1, max=100)])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    salary = IntegerField('Salary', validators=[DataRequired()])
    headhunter = BooleanField('HeadHunter')
    stackoverflow = BooleanField('StackOverFlow')
    submit_search = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

    def validate(self):
        if self.query_search.data.strip() == "":
            return False
        if self.headhunter.data is False and self.stackoverflow.data is False:
            return False
        return True


class EditProfileForm(FlaskForm):
    user_name = StringField('Username',
                            validators=[DataRequired(), Length(min=3, max=64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                      "Usernames must have only "
                                                                                      "letters, numbers, "
                                                                                      "dots or underscores")])
    email = EmailField('Email',
                       validators=[DataRequired(), Email(), Length(min=3, max=64)])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=3, max=64)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=3, max=64)])
    phonenumber = StringField('Phonenumber', validators=[DataRequired(), Length(min=10, max=12),
                                                         Regexp('[0-9]', 0, "Phonenumber must have only numbers")])
    # password = PasswordField('Password',
    #         validators=[DataRequired(), Length(min=8, max=64)])
    # confirm = PasswordField('Verify password',
    #         validators=[DataRequired(), EqualTo('password',
    #         message='Passwords must match')])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
