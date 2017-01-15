#!/usr/bin/env python

from blog import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from blog.models import *

app = create_app()
manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from blog.models import Role, User

    print 'INFO  [deploy command] migrate database to latest revision'
    upgrade()

    print 'INFO  [deploy command] create user roles'
    Role.insert_roles()

    print 'INFO  [deploy command] create admin user'
    User.insert_admin()


if __name__ == '__main__':
    manager.run()
