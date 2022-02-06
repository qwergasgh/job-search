from flask import Blueprint, render_template, request, jsonify
from flask_login.utils import login_required, current_user
from .models import Job, Favorite
from app import db
from .views import ROWS_PAGINATOR


blueprint_report = Blueprint('blueprint_report', 
                             __name__,
                             template_folder='templates', 
                             static_folder='static')


@blueprint_report.route('/', methods=['GET', 'POST'])
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
    favorite_vacancies = {}
    if count > ROWS_PAGINATOR:
        page = request.args.get('page', 1, type=int)
        jobs = Job.query.paginate(page=page, per_page=ROWS_PAGINATOR)
        title = f'Searching results {page} page'
        paginate = True
        if jobs is not None:
            for job in jobs.items:
                id = job.id
                favorite_vacancy = Favorite.query.filter_by(id_user=current_user.id,
                                                            id_vacancy=id).first()
                if favorite_vacancy is None:
                    favorite_vacancies[id] = 'add'
                else:
                    favorite_vacancies[id] = 'delete'
    else:
        jobs = Job.query.all()
        title = 'Searching results'
        paginate = False
        if jobs is not None:
            for job in jobs:
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
