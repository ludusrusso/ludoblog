from . import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "<Role %r>"%self.name

    @staticmethod
    def insert_roles():
        for role_name in "admin publisher user".split():
            if Role.query.filter_by(name=role_name).first() is None:
                role = Role(name = role_name)
                db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(255))
    about = db.Column(db.Text())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return "<User %r>"%self.email

    @staticmethod
    def insert_admin():
        from flask import current_app
        if User.query.filter_by(email=current_app.config['BLOG_ADMIN_MAIL']).first() is None:
            user = User(
                email=current_app.config['BLOG_ADMIN_MAIL'],
                password=current_app.config['BLOG_ADMIN_PASSWORD'],
                active=True)
            user.roles.append(Role.query.filter_by(name='admin').first())
            db.session.add(user)
            db.session.commit()


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_edit = db.Column(db.DateTime, index=True, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
