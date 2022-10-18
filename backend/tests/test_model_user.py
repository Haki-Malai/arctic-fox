import unittest
from time import sleep
from datetime import datetime
from api.app import create_app, db
from api.models import User, Role, AnonymousUser, Permission

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_setter(self):
        u = User(password='password')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='password')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='password')
        self.assertTrue(u.verify_password('password'))
        self.assertFalse(u.verify_password('false_password'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_user_role(self):
        u = User(email='foo@example.com', password='password')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_confirmation_and_jwt_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        self.assertTrue(u.confirmed)

    def test_confirmation_timeout(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        print('Sleeping for 1 second... ', end='', flush=True)
        sleep(2)
        self.assertFalse(u.confirm(token))
        self.assertFalse(u.confirmed)

    def test_reset_password(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'new_password'))
        self.assertTrue(u.verify_password('new_password'))

    def test_change_email(self):
        u = User(email='email')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('new_email')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'new_email')

    def test_follow(self):
        u1 = User(email='email1')
        u2 = User(email='email2')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u1))
        self.assertFalse(u1.is_following(u2))
        timestamp_before = datetime.utcnow()
        self.assertTrue(u1.follow(u2))
        self.assertTrue(u1.is_following(u2))
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.following.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.following.all()[-1]
        self.assertTrue(f.following == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        db.session.add(f)
        db.session.commit()
        self.assertTrue(u1.unfollow(u2))
        self.assertTrue(u1.following.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(u1.follow(u2))
        self.assertTrue(u1.following.count() == 2)
        db.session.add(u1)
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(u1.following.count() == 1)

