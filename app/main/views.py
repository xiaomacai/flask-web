from flask import render_template, session, redirect, url_for, current_app, abort

from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role, Post

from flask_login import login_required, current_user

from ..decorators import admin_required
from ..models import Permission


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        if current_user.can(Permission.WRITE_ARTICLES) and \
                form.validate_on_submit():
            post = Post(body=form.body.data, author=current_user._get_current_object())
            db.session.add(post)
            return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)


@main.route('/user/<user_name>')
def user(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        return redirect(url_for('main.user', user_name=current_user.user_name))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.user_name = form.user_name.data
        return redirect(url_for('main.user', user_name=user.user_name))
    form.email.data = user.email
    form.about_me.data = user.about_me
    form.confirmed.data = user.confirmed
    form.location.data = user.location
    form.name.data = user.name
    form.role.data = user.role_id

    return render_template('edit_profile.html', form=form, user=user)

