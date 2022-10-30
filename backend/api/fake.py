from . import db
from sqlalchemy.exc import IntegrityError
from api.models import User, Post, follower, Comment, Notification, Task, assignment
from faker import Faker
from flask import current_app
from secrets import randbelow


def fake_users(count=10):  # nosec
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
    print('Default user-admin: "useruser"')
    for i in range(count):
        print('Generating fake user %d' % i, end="\r")
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


def fake_follows(count=100):  # nosec
    user_count = User.query.count()
    for i in range(count):
        print('Generating fake follow %d' % i, end="\r")
        u1 = User.query.offset(randbelow(user_count)).first()
        u2 = User.query.offset(randbelow(user_count)).first()
        db.session.execute(follower.insert().values(
            follower_id=u1.id,
            followed_id=u2.id
        ))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=20):  # nosec
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        print('Generating fake post %d' % i, end="\r")
        u = User.query.offset(randbelow(user_count)).first()
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


def fake_comments(count=50):  # nosec
    fake = Faker()
    user_count = User.query.count()
    post_count = Post.query.count()
    for i in range(count):
        print('Generating fake comments %d' % i, end="\r")
        u = User.query.offset(randbelow(user_count)).first()
        p = Post.query.offset(randbelow(post_count)).first()
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


def fake_notifications(count=50):  # nosec
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        print('Generating fake notifications %d' % i, end="\r")
        u = User.query.offset(randbelow(user_count)).first()
        n = Notification(user_id=u.id, body=fake.text(),\
            timestamp=fake.past_date())
        db.session.add(n)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    
def fake_tasks(count=50):  # nosec
    fake = Faker()
    user_count = User.query.filter_by().count()
    for i in range(count):
        print('Generating fake task %d' % i, end="\r")
        assigneed_from = User.query.offset(randbelow(user_count)).first()
        assigned_to = User.query.offset(randbelow(user_count)).first()
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