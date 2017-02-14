# coding: utf8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Email(), Length(1,64)])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'保持登陆')
    submit = SubmitField(u'登陆')

