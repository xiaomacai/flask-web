# coding: utf8
from flask_mail import Message
from flask import render_template
from . import mail
from threading import Thread
from manage import app


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    msg = Message(subject=app.config['MAIL_SUBJECT_PREFIX']+subject, recipients=[to],
                  sender=app.config['BLOG_ADMIN'])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)

    thr = Thread(target=send_async_mail, args=(app, msg))
    thr.start()

    return thr
