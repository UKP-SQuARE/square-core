from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from squareapi.app import create_app
from squareapi.models import db, User, Skill

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

@manager.shell
def shell_ctx():
    return dict(app=app, db=db, User=User, Skill=Skill)

if __name__ == "__main__":
    manager.run()