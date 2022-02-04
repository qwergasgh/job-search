from flask import Blueprint, render_template, request, redirect, send_file, url_for
from flask_login.utils import login_required, current_user
from .forms import RegisterForm
from .models import Job, User, Favorite
from .utils import save_to_csv
from app import db
import os


ROWS_PAGINATOR = 20
blueprint_app = Blueprint('blueprint_app', 
                          __name__,
                          template_folder='templates', 
                          static_folder='static')


@blueprint_app.route('/')
@login_required
def home(): 
    return render_template('index.html', title='Job search')


@blueprint_app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, 
                    user_name=form.user_name.data,
                    first_name=form.first_name.data, 
                    last_name=form.last_name.data,
                    phonenumber=form.phonenumber.data, 
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('blueprint_user.login'))
    return render_template('register.html', title='Register', form=form)


@blueprint_app.route('/export')
@login_required
def export():
    try:
        type = request.args.get('vacancies')
        if type is None:
            raise Exception()
        if type == 'all':
            vacancies = Job.query.all()
            name = 'vacancies'
        if type == 'favorites':
            vacancies_favorites = Favorite.query.filter_by(id_user=current_user.id)
            id_list = []
            for v in vacancies_favorites:
                id_list.append(v.id_vacancy)
            if len(id_list) == 0:
                return redirect(url_for('blueprint_vacancies.favorites'))
            vacancies = Job.query.filter(Job.id.in_(id_list))
            name = 'favorites_vacancies'
        if vacancies is None:
            raise Exception()
        file = os.path.abspath(os.path.dirname(__file__)) + f'/tmp/{name}_for_{current_user.user_name}.csv'
        if save_to_csv(vacancies, file):
            return send_file(file)
        else:
            raise Exception()
    except:
        return redirect(url_for('blueprint_app.home'))
