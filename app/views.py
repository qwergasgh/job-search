import os
from flask import Blueprint, render_template, request, redirect, send_file, url_for, abort, jsonify
from flask_login.utils import login_required, login_user, logout_user, current_user
from .forms import LoginForm, RegisterForm, SearchForm, EditProfileForm
from .models import Job, User, Favorite
from .utils import parsing_vacancies, save_to_csv
from app import db
import os

blueprint_app = Blueprint('blueprint_app', __name__,
                          template_folder='templates', static_folder='static')
ROWS_PAGINATOR = 20


@blueprint_app.route('/')
@login_required
def home():
    # print(request.headers)
    # print('\n\n\n ip =', request.remote_addr) 
    return render_template('index.html', title='Job search')


@blueprint_app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('blueprint_app.report', form=form))
    return render_template('search_form.html', title='Job search', form=form)

# edit count, jobs <-- query db
@blueprint_app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    query = request.form.get('query_search')
    headhunter = request.form.get('headhunter')
    stackoverflow = request.form.get('stackoverflow')
    city = request.form.get('city')
    state = request.form.get('state')
    salary = request.form.get('salary')
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
    # parsing
    # parsing_vacancies(parametrs)
    #####
    id_jobs = []
    favorite_vacancies = {}
    for job in jobs.items:
        id = job.id
        id_jobs.append(id)
        favorite_vacancy = Favorite.query.filter_by(id_user=current_user.id, 
                                                    id_vacancy=id).first()
        if favorite_vacancy is None:
            favorite_vacancies[job.id] = 'add'
        else:
            favorite_vacancies[job.id] = 'delete'
    parametrs = {'query': query,
                 'headhunter': headhunter, 
                 'stackoverflow': stackoverflow, 
                 'city': city, 
                 'state': state, 
                 'salary': salary, 
                 'id_jobs': id_jobs, 
                 'count': count, 
                 'paginate': paginate, 
                 'title': title,
                 'jobs': jobs, 
                 'favorite_vacancies': favorite_vacancies}
    
    return render_template('report.html', parametrs=parametrs)


@blueprint_app.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    vacancies_favorites = Favorite.query.filter_by(id_user=current_user.id)
    id_list = []
    for v in vacancies_favorites:
        id_list.append(v.id_vacancy)
    if len(id_list) == 0:
        return redirect(url_for('blueprint_app.report'))
    jobs_filter = Job.query.filter(Job.id.in_(id_list))
    if len(id_list) > ROWS_PAGINATOR:
        page = request.args.get('page', 1, type=int)
        jobs = jobs_filter.paginate(page=page, per_page=ROWS_PAGINATOR)
        title = f'Favorites vacancies {page} page'
        paginate = True
    else:
        jobs = jobs_filter
        title = 'Favorites vacancies'
        paginate = False
    parametrs = {'title': title, 'paginate': paginate, 'jobs': jobs}
    return render_template('favorites.html', parametrs=parametrs)


@blueprint_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.password.data)
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form.get('email')).first()
        print(form.password.data)
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('blueprint_app.home'))
    return render_template('login.html', title='Login', form=form)


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


@blueprint_app.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('blueprint_app.home'))


@blueprint_app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(user_name=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@blueprint_app.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    name = current_user.user_name
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.user_name = form.user_name.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phonenumber = form.phonenumber.data
        # current_user.password = form.password.data
        # user = User.query.filter_by(user_name=name).first()
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('blueprint_app.edit_profile'))
    form.user_name.data = current_user.user_name
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phonenumber.data = current_user.phonenumber
    # form.password.data = current_user.password
    return render_template('edit_profile.html', title="Edit profile", form=form, name=name)


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
                favorite_vacancy = Favorite(id_user=id_user, id_vacancy=id_vacancy)
                db.session.add(favorite_vacancy)
            if param == 'delete':
                favorite_vacancy = Favorite.query.filter_by(id_user=id_user, id_vacancy=id_vacancy).first()
                db.session.delete(favorite_vacancy)
            db.session.commit()
            return jsonify({'valid': 'True'}), 200
    except:
        return jsonify({'valid': 'False'}), 400


@blueprint_app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="404 Not Found"), 404


@blueprint_app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title="500 Server Error"), 500


@blueprint_app.errorhandler(400)
def bad_request(e):
    return render_template('400.html', title="400 Bad Request"), 400
