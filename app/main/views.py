from flask import render_template, session, redirect, url_for, current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import User


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
