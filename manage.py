#!/usr/bin/env python

from blog import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app()
manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

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
