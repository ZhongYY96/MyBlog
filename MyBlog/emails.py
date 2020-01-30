# -*- coding: utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

from MyBlog.extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, template="", html="", **kwargs):
    if html != "":
        message = Message(subject, recipients=[to], html=html)
    else:
        message = Message(subject, recipients=[to])
        message.body = render_template(template + '.txt', **kwargs)
        message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_confirm_email(user, token, to=None):
    send_mail(subject='账号确认', to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject='密码重置', to=user.email, template='emails/reset_password', user=user, token=token)


def send_change_email_email(user, token, to=None):
    send_mail(subject='修改邮箱', to=to or user.email, template='emails/change_email', user=user, token=token)
