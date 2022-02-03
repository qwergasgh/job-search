from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login.utils import login_required, current_user
from app.forms import JobForm
from app.models import Job, Favorite
from app.views import ROWS_PAGINATOR
from app import db
import os

blueprint_vacancies = Blueprint('blueprint_vacancies', __name__,
                          template_folder='templates', 
                          static_folder='static')



@blueprint_vacancies.route('/')
@login_required
def vacancies():
    count = Job.query.count()
    if count > ROWS_PAGINATOR:
        page = request.args.get('page', 1, type=int)
        jobs = Job.query.paginate(page=page, per_page=ROWS_PAGINATOR)
        title = f'Vacancies {page} page'
        paginate = True
    else:
        jobs = Job.query.all()
        title = 'Vacancies'
        paginate = False
    parametrs = {'jobs': jobs, 
                 'count': count, 
                 'paginate': paginate}
    return render_template('vacancies.html', parametrs=parametrs, title=title)


@blueprint_vacancies.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    vacancies_favorites = Favorite.query.filter_by(id_user=current_user.id)
    id_list = []
    for v in vacancies_favorites:
        id_list.append(v.id_vacancy)
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
    parametrs = {'paginate': paginate, 'jobs': jobs}
    return render_template('favorites.html', parametrs=parametrs, title=title)


@blueprint_vacancies.route('/add-vacancy', methods=['GET', 'POST'])
@login_required
def add_vacancy():
    title = 'Add vacancy'
    formJob = JobForm()
    if formJob.validate_on_submit():
        title_vacancy= request.form.get('title')
        company = request.form.get('company')
        salary = request.form.get('salary')
        location = request.form.get('location')
        source = request.form.get('source')
        link = request.form.get('link')
        new_vacancy = Job(title=title_vacancy, 
                          company=company,
                          salary=salary,
                          location=location,
                          source=source,
                          link=link)
        db.session.add(new_vacancy)
        db.session.commit()
        # search.update_index(Job)
        return redirect(url_for('blueprint_vacancies.vacancies'))
    return render_template('add_vacancy.html', form=formJob, title=title)


@blueprint_vacancies.route('/delete-vacancy', methods=['POST'])
@login_required
def delete_vacancy():
    try:
        if request.method == 'POST':
            id_vacancy = request.json['id']
            if id_vacancy is None:
                return jsonify({'valid': 'False'}), 400
            vacancy = Job.query.filter_by(id=id_vacancy).first()
            f_vacancy = Favorite.query.fulter_by(id_vacancy=id_vacancy).first()
            db.session.delete(vacancy)
            db.session.delete(f_vacancy)
            db.session.commit()
            # search.update_index(Job)
            return jsonify({'valid': 'True'}), 200
    except:
        return jsonify({'valid': 'False'}), 400


@blueprint_vacancies.route('/delete-vacancies')
@login_required
def delete_vacancies():
    try:
        db.session.query(Job).delete()
        db.session.query(Favorite).delete()
        db.session.commit()
        # search.update_index(Job)
        return redirect(url_for('blueprint_vacancies.vacancies'))
    except:
        return jsonify({'valid': 'False'}), 400