# -*- coding: utf-8 -*-
import os

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from flask_login import login_required, current_user, fresh_login_required
from flask_ckeditor import upload_success, upload_fail

from MyBlog.extensions import db
from MyBlog.forms import SettingForm, PostForm, ChangePasswordForm, DeleteAccountForm
from MyBlog.models import Post, Category, Comment
from MyBlog.utils import redirect_back, allowed_file
from MyBlog.utils import confirm_required
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        db.session.commit()
        flash('设置已更新.', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/post/manage')
@login_required
@confirm_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.author == current_user).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['MYBLOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@confirm_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('博文已创建.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@confirm_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('博文已更新.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
@confirm_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('博文已删除.', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
@confirm_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('已关闭评论.', 'success')
    else:
        post.can_comment = True
        flash('已打开评论.', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/manage')
@login_required
@confirm_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        user_id = current_user.id
        filtered_comments = Comment.query.join(Post, Post.id == Comment.post_id_r).filter(Post.author_id == user_id)
        filtered_comments = filtered_comments.filter(Comment.reviewed== False)
    else:
        user_id=current_user.id
        filtered_comments = Comment.query.join(Post, Post.id == Comment.post_id).filter(Post.author_id == user_id)
    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
@confirm_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.filter_by(id=comment.post_id_r).first()
    comment.reviewed = True
    comment.post = post
    db.session.commit()
    flash('评论已通过.', 'success')
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@confirm_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除.', 'success')
    return redirect_back()


@admin_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['MYBLOG_UPLOAD_PATH'], filename)


@admin_bp.route('/upload', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('仅图片!')
    f.save(os.path.join(current_app.config['MYBLOG_UPLOAD_PATH'], f.filename))
    url = url_for('.get_image', filename=f.filename)
    return upload_success(url, f.filename)


@admin_bp.route('/settings/account/delete', methods=['GET', 'POST'])
@fresh_login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        flash('账号已删除', 'success')
        return redirect(url_for('blog.index'))
    return render_template('admin/delete_account.html', form=form)


@admin_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('新密码已设置.', 'success')
            return redirect(url_for('blog.index'))
        else:
            flash('旧密码不正确.', 'warning')
    return render_template('admin/change_password.html', form=form)
