from flask import Blueprint, render_template, request, redirect, send_file, url_for, abort, jsonify
from flask_login.utils import login_required, login_user, logout_user, current_user
from .forms import LoginForm, RegisterForm, SearchForm, EditProfileForm, ParsingForm, JobForm, ResetPasswordForm, ResetPasswordForm_token
from .models import Job, User, Favorite, TempJob
from .utils import save_to_csv, clear_tmp, get_jobs, send_password_reset_email, Parsing
from app import db
import os
# from app import search



blueprint_app = Blueprint('blueprint_app', __name__,
                          template_folder='templates', 
                          static_folder='static')
ROWS_PAGINATOR = 20


@blueprint_app.route('/')
@login_required
def home(): 
    return render_template('index.html', title='Job search')


@blueprint_app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form_search = SearchForm()
    if request.form.get('submit_search') is not None:
        if form_search.validate_on_submit():
            return redirect(url_for('blueprint_app.report', 
                                    query_search=request.form.get('query_search'),
                                    headhunter=request.form.get('headhunter'),
                                    stackoverflow=request.form.get('stackoverflow'),
                                    city=request.form.get('city'),
                                    state=request.form.get('state'),
                                    salary=request.form.get('salary')))
    if current_user.is_administrator():
        form_parsing = ParsingForm()
        if form_parsing.validate_on_submit():
            p = Parsing(request.form.get('headhunter'), 
                        request.form.get('stackoverflow'), 
                        request.form.get('query_parsing'))
            p.parsing_vacancies()
    return render_template('search_form.html', 
                           title='Job search', 
                           form_search=form_search, 
                           form_parsing=form_parsing)


@blueprint_app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    query_search = request.args.get('query_search')
    # jobs_filter = get_jobs({'query': query_search,
    #                         'headhunter': request.args.get('headhunter'),
    #                         'stackoverflow': request.args.get('stackoverflow'),
    #                         'city': request.args.get('city'),
    #                         'state': request.args.get('state'),
    #                         'salary': request.args.get('salary')})
    
    count = Job.query.count()
    if count > ROWS_PAGINATOR:
        page = request.args.get('page', 1, type=int)
        jobs = Job.query.paginate(page=page, per_page=ROWS_PAGINATOR)
        title = f'Searching results {page} page'
        paginate = True
    else:
        jobs = Job.query.all()
        title = 'Searching results'
        paginate = False
    favorite_vacancies = {}
    if len(jobs) > 0:
        for job in jobs.items:
            id = job.id
            favorite_vacancy = Favorite.query.filter_by(id_user=current_user.id, 
                                                        id_vacancy=id).first()
            if favorite_vacancy is None:
                favorite_vacancies[id] = 'add'
            else:
                favorite_vacancies[id] = 'delete'
    parametrs = {'query_search': query_search,
                 'count': count, 
                 'paginate': paginate, 
                 'jobs': jobs, 
                 'favorite_vacancies': favorite_vacancies}
    return render_template('report.html', parametrs=parametrs, title=title)


@blueprint_app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, user_name=form.user_name.data,
                    first_name=form.first_name.data, last_name=form.last_name.data,
                    phonenumber=form.phonenumber.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('blueprint_app.login'))
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
                return redirect(url_for('blueprint_app.favorites'))
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


@blueprint_app.route('/report/set-status-vacancy', methods=['POST'])
@login_required
def set_status_vacancy():
    try:
        if request.method == 'POST':
            id_user = current_user.id
            id_vacancy = int(request.json['id'])
            param = request.json['param']
            if param == 'add':
                favorite_vacancy = Favorite(id_user=id_user, 
                                            id_vacancy=id_vacancy).first()
                db.session.add(favorite_vacancy)
            if param == 'delete':
                favorite_vacancy = Favorite.query.filter_by(id_user=id_user, 
                                                            id_vacancy=id_vacancy).first()
                db.session.delete(favorite_vacancy)
            db.session.commit()
            return jsonify({'valid': 'True'}), 200
    except:
        return jsonify({'valid': 'False'}), 400


@blueprint_app.route('/search/parsing')
def progress():
    percentage = Parsing.get_percentage()
    if percentage == 100:
        Parsing.update_percentage(0)
    return jsonify({'percentage': percentage}), 200

@blueprint_app.route('/search/stop-parsing', methods=['POST'])
def stop_parsing():
    Parsing.set_status_thread(False)
    Parsing.update_percentage(0)
    print('stop')
    return jsonify({'parsing': 'stop'}), 200


@blueprint_app.route('/parsing-result')
@login_required
def parsing_result():
    count = TempJob.query.count()
    if count > ROWS_PAGINATOR:
        page = request.args.get('page', 1, type=int)
        temp_jobs = TempJob.query.paginate(page=page, per_page=ROWS_PAGINATOR)
        title = f'Parsing results {page} page'
        paginate = True
    else:
        temp_jobs = TempJob.query.all()
        title = 'Parsing results'
        paginate = False
    parametrs = {'paginate': paginate, 
                 'jobs': temp_jobs,
                 'count': count}
    return render_template('parsing_result.html', title=title, parametrs=parametrs)


@blueprint_app.route('/parsing-result/set-status-vacancy', methods=['POST'])
@login_required
def set_status_parsing_vacancy():
    try:
        if request.method == 'POST':
            id_temp_vacancy = int(request.json['id'])
            param = request.json['param']
            temp_job = TempJob.query.filter_by(id=id_temp_vacancy).first()
            if param == 'y':
                temp_job.status = True
            if param == 'n':
                temp_job.status = False
            db.session.add(temp_job)
            db.session.commit()
            return jsonify({'valid': 'True'}), 200
    except:
        return jsonify({'valid': 'False'}), 400


@blueprint_app.route('/parsing-result/add-parsing-vacancies')
@login_required
def add_parsing_vacancies():
    try:
        param = request.args.get('param')
        if param is None:
            return redirect(url_for('blueprint_app.parsing_result'))
        if param == 'all':
            temp_jobs = TempJob.query.all()
        if param == 'favorites':
            temp_jobs = TempJob.query.filter_by(status=True)
        new_jobs = []
        for vacancy in temp_jobs:
            temp_job = Job(title=vacancy.title, 
                           company=vacancy.company, 
                           salary=vacancy.salary, 
                           location=vacancy.location, 
                           link=vacancy.link,
                           source=vacancy.source)
            new_jobs.append(temp_job)
        db.session.add(new_jobs)
        db.session.query(TempJob).delete()
        db.session.commit()
        return redirect(url_for('blueprint_app.vacancies'))
    except:
        return redirect(url_for('blueprint_app.parsing_result'))
