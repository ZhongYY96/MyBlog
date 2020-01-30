# -*- coding: utf-8 -*-
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from MyBlog import db
from MyBlog.models import Admin, Category, Post, Comment

fake = Faker()


def fake_admin(count=10):
    for i in range(count):
        user = Admin(
                    name=fake.name(),
                    username=fake.user_name(),
                    confirmed=True,
                    about=fake.sentence(),
                    email=fake.email()
        )
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    admin = Admin(
        name='helloworld',
        username='admin',
        confirmed=True,
        about='helloworld',
        email="123@qq.com"
    )
    admin.set_password('123')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):

    categorylist = ['生活', '科技', '教育', '旅游', '体育', '娱乐', '游戏']

    for i in categorylist:

        category = Category(name=i)
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            author=Admin.query.get(random.randint(1, Admin.query.count())),
            timestamp=fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        user = Admin.query.get(random.randint(1, Admin.query.count()))
        comment = Comment(
            author_name=user.username,
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count())),
            author=user
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        user = Admin.query.get(random.randint(1, Admin.query.count()))
        post = Post.query.get(random.randint(1, Post.query.count()))
        comment = Comment(
            author_name=user.username,
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            author=user,
            post_id_r=post.id
        )
        db.session.add(comment)

    db.session.commit()

    for i in range(salt):
        user = Admin.query.get(random.randint(1, Admin.query.count()))
        comment = Comment(
            author_name=user.username,
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count())),
            author=user
        )
        db.session.add(comment)
    db.session.commit()
