# coding:utf8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    user_name = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.INTEGER, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError(u'password属性禁止访问')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.user_name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.INTEGER, unique=True)
    users = db.relationship('User', backref='roles')

    def __repr__(self):
        return '<Role {}>'.format(self.name)
