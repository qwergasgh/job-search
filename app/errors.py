from flask import Blueprint, render_template

blueprint_errors = Blueprint('blueprint_errors', __name__,
                          template_folder='templates', 
                          static_folder='static')


@blueprint_errors.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', title="404 Not Found"), 404


@blueprint_errors.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', title="500 Server Error"), 500


@blueprint_errors.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html', title="400 Bad Request"), 400