# coding:utf8
from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    user_name = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.INTEGER, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}>'.format(self.user_name)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.INTEGER, unique=True)
    users = db.relationship('User', backref='roles')

    def __repr__(self):
        return '<Role {}>'.format(self.name)
