from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login.utils import login_required, current_user
from .models import Job, Favorite
from .utils import get_jobs
from app import db


blueprint_report = Blueprint('blueprint_report', 
                             __name__,
                             template_folder='templates', 
                             static_folder='static')


@blueprint_report.route('/', methods=['GET', 'POST'])
@login_required
def report():
    query_search = request.args.get('query_search')
    city=request.args.get('city')
    state=request.args.get('state')
    salary=request.args.get('salary')
    jobs_filter = get_jobs(dict(query=query_search,
                                city=city,
                                state=state,
                                salary=salary))
    count = jobs_filter.count()
    favorite_vacancies = {}
    if count > current_app.config['ROWS_PAGINATOR']:
        page = request.args.get('page', 1, type=int)
        jobs = jobs_filter.paginate(page=page, per_page=current_app.config['ROWS_PAGINATOR'])
        title = f'Searching results {page} page'
        paginate = True
        if jobs is not None:
            for job in jobs.items:
                id = job.id
                favorite_vacancy = Favorite.query.filter_by(id_user=current_user.id,
                                                            id_vacancy=id).first()
                favorite_vacancies[id] = 'add' if favorite_vacancy is None else 'delete'
    else:
        jobs = jobs_filter
        title = 'Searching results'
        paginate = False
        if jobs is not None:
            for job in jobs:
                id = job.id
                favorite_vacancy = Favorite.query.filter_by(id_user=current_user.id,
                                                            id_vacancy=id).first()
                favorite_vacancies[id] = 'add' if favorite_vacancy is None else 'delete'
    parametrs = {'query_search': query_search,
                 'city': city,
                 'state': state,
                 'salary': salary,
                 'count': count, 
                 'paginate': paginate, 
                 'param': True,
                 'url': 'blueprint_report.report',
                 'jobs': jobs, 
                 'favorite_vacancies': favorite_vacancies}
    return render_template('report/report.html', parametrs=parametrs, title=title)



@blueprint_report.route('/set-status-vacancy', methods=['POST'])
@login_required
def set_status_vacancy():
    try:
        if request.method == 'POST':
            id_user = current_user.id
            id_vacancy = int(request.json['id'])
            param = request.json['param']
            if param == 'add':
                favorite_vacancy = Favorite(id_user=id_user, 
                                            id_vacancy=id_vacancy)
                db.session.add(favorite_vacancy)
            if param == 'delete':
                favorite_vacancy = Favorite.query.filter_by(id_user=id_user, 
                                                            id_vacancy=id_vacancy).first()
                db.session.delete(favorite_vacancy)
            db.session.commit()
            return jsonify({'valid': 'True'}), 200
    except:
        return jsonify({'valid': 'False'}), 400
