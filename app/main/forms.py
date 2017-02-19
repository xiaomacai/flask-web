# coding: utf8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField(u'姓名', validators=[DataRequired()])
    submit = SubmitField(u'确定')


class EditProfileForm(FlaskForm):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'确定')


class EditProfileAdminForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Email(), Length(1, 64)])
    user_name = StringField(u'用户名', validators=[DataRequired(), Length(1, 64)])
    confirmed = BooleanField(u'确认')
    role = SelectField(u'角色', coerce=int)
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for \
                             role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经存在')

    def validate_user_name(self, field):
        if field.data != self.user.user_name and \
                User.query.filter_by(user_name=field.data).first():
            raise ValidationError(u'用户名已经存在')
