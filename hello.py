# coding:utf8
from flask import Flask
from flask import render_template, redirect, url_for, session, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "SDF324SFW#*#fs4523sdfER@#5gfjj436.vm,65"
manager = Manager(app)
bootstrap = Bootstrap(app)


class NameForm(Form):
    name = StringField(u'输入你的姓名:', validators=[DataRequired()])
    submit = SubmitField(u'确认')


@app.route('/', methods=['POST', 'GET'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash(u'名字已修改!')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))


@app.route('/user/<username>')
def user(username):
    return render_template('user.html', name=username)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internet_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    manager.run()
