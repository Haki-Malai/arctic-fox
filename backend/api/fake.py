from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from api.models import User, Post, follower, Comment, Notification, Task, assignment
from flask import current_app


def fake_users(count=10):
    fake = Faker()
    u = User(
            username='username',
            password='password',
            email=current_app.config['MAIL_FOR_TEST_OR_DEBUG'] or 'test@test.gr',
            bitcoin_address=fake.md5(),
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            member_since=fake.past_date())
    db.session.add(u)
    print('Default admin: "useruser"')
    print('Generating fake users...')
    for i in range(count):
        u = User(
            username=fake.user_name(),
            email=fake.email(),
            bitcoin_address=fake.md5(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            
def fake_follows(count=100):
    fake = Faker()
    user_count = User.query.count()
    print('Generating fake follows...')
    for i in range(count):
        u1 = User.query.offset(randint(0, user_count - 1)).first()
        u2 = User.query.offset(randint(0, user_count - 1)).first()
        db.session.execute(follower.insert().values(
            follower_id=u1.id,
            followed_id=u2.id
        ))
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
    user_count = User.query.filter_by().count()
    print('Generating fake tasks...')
    for i in range(count):
        assigneed_from = User.query.offset(randint(0, user_count - 1)).first()
        assigned_to = User.query.offset(randint(0, user_count - 1)).first()
        t = Task(
            name=fake.bs(),
            description=fake.text(),
            value=float(fake.pricetag().replace('$', '').replace(',', '')),
            url=fake.url(),
            timestamp=fake.past_date(),
            due_date=fake.future_date(),
            assignee_id=assigneed_from.id,
        )
        db.session.add(t)
        db.session.commit()
        db.session.execute(assignment.insert().values(
            task_id=t.id,
            assigned_id=assigned_to.id,
        ))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()