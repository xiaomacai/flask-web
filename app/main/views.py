# coding: utf-8
from flask import render_template, session, redirect, url_for, current_app, abort, request, flash
from flask import make_response

from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role, Post

from flask_login import login_required, current_user

from ..decorators import admin_required, permission_required
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

    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<user_name>')
def user(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination  )


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


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTRATOR):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<user_name>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash(u'你已经关注了该用户')
        return redirect(url_for('.user', user_name=user_name))
    current_user.follow(user)
    return redirect(url_for('.user', user_name=user_name))


@main.route('/unfollow/<user_name>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash(u'你尚未关注该用户')
        return redirect(url_for('.user', user_name=user_name))
    current_user.unfollow(user)
    return redirect(url_for('.user', user_name=user_name))


@main.route('/followers/<user_name>')
def followers(user_name):
    """关注了"""
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<user_name>')
def followed_by(user_name):
    """关注者"""
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['BLOG_FOLLOWED_PER_PAGE'],
        error_out=False
    )
    followed = [{'user': item.followed, 'timestamp': item.timestamp}
                for item in pagination.items]
    return render_template('followed_by.html', user=user, title='Followed by',
                           endpoint='.followed_by', pagination=pagination,
                           followed=followed)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp
