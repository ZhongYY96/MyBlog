# -*- coding: utf-8 -*-
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, \
    BooleanField, PasswordField
from flask_login import current_user

from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional, URL

from MyBlog.models import Category,Admin


class LoginForm(FlaskForm):
    email = StringField('电子邮件', validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegisterForm(FlaskForm):
    name = StringField('真实姓名', validators=[DataRequired(), Length(1, 30)])
    email = StringField('电子邮件', validators=[DataRequired(), Length(1, 254), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20),
                                                   Regexp('^[a-zA-Z0-9]*$',
                                                          message='用户名仅能包含 a-z, A-Z and 0-9.')])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(1, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if Admin.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该电子邮件已注册！')

    def validate_username(self, field):
        if Admin.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册！')


class SettingForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('博客标题', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('博客子标题', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('提交')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('类别', coerce=int, default=1)
    body = CKEditorField('内容', validators=[DataRequired()])
    submit = SubmitField('发布')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class AdminCommentForm(FlaskForm):
    body = TextAreaField('评论', validators=[DataRequired()])
    submit = SubmitField('提交')


class ForgetPasswordForm(FlaskForm):
    email = StringField('请输入注册邮件', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField('提交')


class ResetPasswordForm(FlaskForm):
    email = StringField('邮件', validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('密码确认', validators=[DataRequired()])
    submit = SubmitField('提交')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class DeleteAccountForm(FlaskForm):
    username = StringField('输入用户名', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('提交')

    def validate_username(self, field):
        if field.data != current_user.username:
            raise ValidationError('用户名不正确.')
