# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from MyBlog.forms import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from MyBlog.models import Admin
from MyBlog.utils import redirect_back
from MyBlog.extensions import db

from MyBlog.utils import generate_token,validate_token
from MyBlog.emails import send_confirm_email, send_reset_password_email
from MyBlog.settings import Operations

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(email=form.email.data.lower()).first()
        if admin:
            if admin.validate_password(password):
                login_user(admin, remember)
                flash('欢迎回来.', 'info')
                return redirect_back()
            flash('密码不正确.', 'warning')
        else:
            flash('无此用户.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功.', 'info')
    return redirect(url_for('blog.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = Admin(name=name, email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user=user, operation='confirm')
        send_confirm_email(user=user, token=token)
        login_user(user)
        flash('账户确认邮件已发送, 请注意检查邮箱！', 'info')
        return redirect(url_for('blog.index'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('blog.index'))

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('账户已确认！.', 'success')
        return redirect(url_for('blog.index'))
    else:
        flash('非法或过期凭证.', 'danger')
        return redirect(url_for('.resend_confirm_email'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('blog.index'))

    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('新邮件已发送.', 'info')
    return redirect(url_for('blog.index'))


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(user=user, token=token)
            flash('密码重置邮件已发送，请在邮箱查看.', 'info')
            return redirect(url_for('.login'))
        flash('邮箱不存在.', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect(url_for('blog.index'))
        if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD,
                          new_password=form.password.data):
            flash('密码已修改.', 'success')
            return redirect(url_for('.login'))
        else:
            flash('无效或过期的凭证.', 'danger')
            return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)
