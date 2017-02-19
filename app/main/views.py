from flask import render_template, session, redirect, url_for, current_app, abort

from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..models import User

from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.name.data).first()
        if user is None:
            user = User(user_name=form.name.data)
            db.session.add(user)
            from ..email import send_mail
            send_mail(current_app.config['BLOG_ADMIN'], u'new user', 'mail/new_user', user=user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index'))
    return render_template('index.html', known=session.get('known'), name=session.get('name'),
                           form=form)


@main.route('/user/<user_name>')
def user(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


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


