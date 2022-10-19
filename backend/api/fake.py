from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Follow, Comment, Notification, Task, Assignment
from flask import current_app


def fake_admins(count=2):
    fake = Faker()
    print('Generating fake admins...')
    for i in range(count):
        u = User(
            email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            member_since=fake.past_date(),
            role='admin'
        )
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_users(count=10):
    fake = Faker()
    print('Generating fake users...')
    for i in range(count):
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

            
def fake_follows(count=100):
    fake = Faker()
    user_count = User.query.count()
    print('Generating fake follows...')
    for i in range(count):
        u1 = User.query.offset(randint(0, user_count - 1)).first()
        u2 = User.query.offset(randint(0, user_count - 1)).first()
        f = Follow(
            follower=u1.id,
            followed=u2.id
        )
        db.session.add(f)
        try:
            db.session.commit()
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
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_notifications(count=50):
    fake = Faker()
    user_count = User.query.count()
    print('Generating fake notifications...')
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        n = Notificatin.query.offset(randint(0, post_count - 1)).first()
        db.session.add(n)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    
def fake_tasks(count=50):
    fake = Faker()
    user_count = User.query.filter_by(role='admin').count()
    print('Generating fake tasks...')
    for i in range(count):
        assignee = User.query.offset(randint(0, user_count - 1)).first()
        assigned = User.query.offset(randint(0, user_count - 1)).first()
        t = Task(
            name=fake.text(),
            timestamp=fake.past_date(),
            due_date=fake.future_date(),
        )
        a = Assignment(
            task=t.id,
            assignee=assignee.id,
            assigned=assigned.id,
        )
        db.session.add(a,t)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()