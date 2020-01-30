# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint
from flask_login import current_user, login_required
from flask import Markup
from MyBlog.extensions import db
from MyBlog.forms import AdminCommentForm
from MyBlog.models import Post, Category, Comment
from MyBlog.utils import confirm_required

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['MYBLOG_POST_PER_PAGE']
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
        posts = pagination.items
        return render_template('blog/index.html', pagination=pagination, posts=posts)
    else:
        return redirect(url_for('auth.login'))


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        reviewed = False
        if current_user == post.author:
            reviewed = True

    if form.validate_on_submit():
        if current_user.confirmed:
            author = current_user._get_current_object()
            author_name = author.username
            body = form.body.data
            if post.author == current_user:
                comment = Comment(
                    author=author, author_name=author_name, body=body,
                    post=post, reviewed=reviewed)
            else:
                comment = Comment(
                    author=author, author_name=author_name, body=body,
                    post_id_r=post.id, reviewed=reviewed)

            replied_id = request.args.get('reply')
            if replied_id:
                replied_comment = Comment.query.get_or_404(replied_id)
                comment.replied = replied_comment
            db.session.add(comment)
            db.session.commit()
            if post.author == current_user:
                flash('评论发布成功.', 'success')
            else:
                flash('你的评论将在作者审阅后发布.', 'info')
            return redirect(url_for('.show_post', post_id=post_id))
        else:
            message = Markup(
                '请先在邮箱中确认您的账号.'
                '没收到邮件?'
                '<a class="alert-link" href="%s">重新发送确认邮件</a>' %
                url_for('auth.resend_confirm_email'))
            flash(message, 'warning')
            return redirect(url_for('.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
@login_required
@confirm_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('评论已关闭.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author_name) + '#comment-form')


