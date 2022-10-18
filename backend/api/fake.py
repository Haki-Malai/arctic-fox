from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment
from flask import current_app


def fake_users(count=10):
    fake = Faker()
    i = 0
    print('Generating fake users...')
    while i < count:
        u = User(
            email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            member_since=fake.past_date()
        )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def fake_posts(count=20):
    fake = Faker()
    user_count = User.query.count()
    print('Generating fake posts...')
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(
            body=fake.text(),
            timestamp=fake.past_date(),
            user_id=u.id
        )
        db.session.add(p)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def fake_comments(count=50):
    fake = Faker()
    user_count = User.query.count()
    post_count = Post.query.count()
    print('Generating fake comments...')
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post.query.offset(randint(0, post_count - 1)).first()
        c = Comment(
            body=fake.text(),
            timestamp=fake.past_date(),
            user_id=u.id,
            post_id=p.id
        )
        db.session.add(c)
    db.session.commit()