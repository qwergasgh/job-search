from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from flask_login.utils import login_required
from .models import Job, TempJob
from app import db


blueprint_parsing_result = Blueprint('blueprint_parsing_result', 
                                     __name__,
                                     template_folder='templates', 
                                     static_folder='static')


@blueprint_parsing_result.route('/')
@login_required
def parsing_result():
    count = TempJob.query.count()
    if count > current_app.config['ROWS_PAGINATOR']:
        page = request.args.get('page', 1, type=int)
        temp_jobs = TempJob.query.paginate(page=page, per_page=current_app.config['ROWS_PAGINATOR'])
        title = f'Parsing results {page} page'
        paginate = True
    else:
        temp_jobs = TempJob.query.all()
        title = 'Parsing results'
        paginate = False
    parametrs = {'paginate': paginate, 
                 'jobs': temp_jobs,
                 'count': count}
    return render_template('parsing_result/parsing_result.html', title=title, parametrs=parametrs)


@blueprint_parsing_result.route('/set-status-vacancy', methods=['POST'])
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


@blueprint_parsing_result.route('/delete-vacancy', methods=['POST'])
@login_required
def delete_vacancy():
    try:
        if request.method == 'POST':
            id_temp_vacancy = int(request.json['id'])
            temp_job = TempJob.query.filter_by(id=id_temp_vacancy).first()
            db.session.delete(temp_job)
            db.session.commit()
            return jsonify({'valid': 'True'}), 200
    except:
        return jsonify({'valid': 'False'}), 400


@blueprint_parsing_result.route('/add-parsing-vacancies')
@login_required
def add_parsing_vacancies():
    try:
        param = request.args.get('param')
        if param is None:
            return redirect(url_for('blueprint_parsing_result.parsing_result'))
        if param == 'all':
            temp_jobs = TempJob.query.all()
        if param == 'favorites':
            temp_jobs = TempJob.query.filter_by(status=True)
        for vacancy in temp_jobs:
            temp_job = Job(title=vacancy.title, 
                           company=vacancy.company, 
                           salary=vacancy.salary, 
                           # location=vacancy.location, 
                           city=vacancy.city, 
                           state=vacancy.state, 
                           link=vacancy.link,
                           source=vacancy.source)
            db.session.add(temp_job)
            db.session.delete(vacancy)
        db.session.commit()
        return redirect(url_for('blueprint_vacancies.vacancies'))
    except:
        return redirect(url_for('blueprint_parsing_result.parsing_result'))


@blueprint_parsing_result.route('/delete-vacancies')
@login_required
def delete_vacancies():
    try:
        db.session.query(TempJob).delete()
        db.session.commit()
        return redirect(url_for('blueprint_parsing_result.parsing_result'))
    except:
        return jsonify({'valid': 'False'}), 400