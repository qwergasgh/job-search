from flask import Blueprint, current_app, render_template, request, redirect, send_file, url_for
from flask_login.utils import login_required, current_user
from .utils import save_to_csv, get_jobs
from .models import Job, User, Favorite
from .forms import RegisterForm
from app import db
import os


blueprint_app = Blueprint('blueprint_app', 
                          __name__,
                          template_folder='templates', 
                          static_folder='static')


@blueprint_app.route('/')
@login_required
def home(): 
    return render_template('index.html', title='Job search')


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
        elif type == 'favorites':
            vacancies_favorites = Favorite.query.filter_by(id_user=current_user.id)
            id_list = [v.id_vacancy for v in vacancies_favorites]
            if len(id_list) == 0:
                return redirect(url_for('blueprint_vacancies.favorites'))
            vacancies = Job.query.filter(Job.id.in_(id_list)).all()
            name = 'favorites_vacancies'
        elif type == 'result':
            query_search = request.args.get('query_search')
            city=request.args.get('city')
            state=request.args.get('state')
            salary=request.args.get('salary')
            vacancies = get_jobs(dict(query=query_search,
                                        city=city,
                                        state=state,
                                        salary=salary)).all()
            name = 'result'
        else:
            raise Exception()
        if vacancies is None:
            raise Exception()
        file = os.path.join(current_app.config['TMP_DIR'], \
               f'{name}_for_{current_user.user_name}.csv')
        if save_to_csv(vacancies, file):
            return send_file(file)
        else:
            raise Exception()
    except:
        return redirect(url_for('blueprint_app.home'))

