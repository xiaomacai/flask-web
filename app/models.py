# coding:utf8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
import bleach
from markdown import markdown


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    user_name = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.TEXT)
    member_since = db.Column(db.DATETIME(), default=datetime.utcnow)
    last_seen = db.Column(db.DATETIME(), default=datetime.utcnow)
    role_id = db.Column(db.INTEGER, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.BOOLEAN, default=False)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BLOG_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

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


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.INTEGER, unique=True)
    default = db.Column(db.BOOLEAN, default=False, index=True)
    permissions = db.Column(db.INTEGER)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMIT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMIT | Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.default = roles[r][1]
            role.permissions = roles[r][0]
            db.session.add(role)
        db.session.commit()


class Permission:
    FOLLOW = 0X01
    COMMIT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTRATOR = 0X80


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.INTEGER, primary_key=True)
    body = db.Column(db.TEXT)
    body_html = db.Column(db.TEXT)
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    author_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i'\
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
