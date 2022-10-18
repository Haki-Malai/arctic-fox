import unittest
from datetime import datetime
from api.app import create_app, db
from api.models import User, Role, Post, Comment, Notification, AnonymousUser, Permission

class MediaModelTestCase(unittest.TestCase):
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
        
    def test_post(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        self.assertIsNone(u.posts.first())
        timestamp_before = datetime.utcnow()
        p = Post(body='test', user_id=u.id)
        db.session.add(p)
        db.session.commit()
        self.assertIsNotNone(u.posts.first())
        self.assertIsNotNone(Post.query.first())
        self.assertIsNotNone(p.timestamp)
        p.body = 'test2'
        db.session.add(p)
        db.session.commit()
        self.assertEqual(p.body, 'test2')
        timestamp_after = datetime.utcnow()
        self.assertTrue(timestamp_before <= p.timestamp <= timestamp_after)

    def test_comment(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        p = Post(body='test', user_id=u.id)
        timestamp_before = datetime.utcnow()
        db.session.add(p)
        db.session.commit()
        self.assertIsNone(p.comments.first())
        c = Comment(body='test', post_id=p.id, user_id=u.id)
        db.session.add(c)
        db.session.commit()
        self.assertIsNotNone(p.comments.first())
        self.assertIsNotNone(Comment.query.first())
        self.assertIsNotNone(c.timestamp)
        c.body = 'test2'
        db.session.add(c)
        db.session.commit()
        self.assertEqual(c.body, 'test2')
        timestamp_after = datetime.utcnow()
        self.assertTrue(timestamp_before <= c.timestamp <= timestamp_after)

    def test_notification(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        self.assertIsNone(u.notifications.first())
        n = Notification(name='test', user_id=u.id)
        db.session.add(n)
        db.session.commit()
        self.assertIsNotNone(u.notifications.first())
        
