from app import app, db
from app.models import Job, Favorites, User
from flask_script import Manager, Shell

# from flask_migrate import Migrate, migrate, upgrade, command


manager = Manager(app)


# migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Job=Job, User=User, Favorites=Favorites)


manager.add_command('shell', Shell(make_context=make_shell_context))
# manager.add_command('db', migrate)

if __name__ == '__main__':
    manager.run()
