from tests.base_test_case import BaseTestCase
from api.app import db
from api.models import User, Post, Comment, Notification
from datetime import datetime
from time import sleep

class UserModelTestCase(BaseTestCase):
    def test_password(self):
        self.user.password = 'new_password'
        db.session.commit()
        self.assertTrue(self.user.verify_password('new_password'))
        self.assertFalse(self.user.verify_password(self.password))
        self.user.password = self.password
        db.session.commit()
        self.assertTrue(self.user.verify_password(self.password))

        with self.assertRaises(AttributeError):
            self.user.password

        u = User(password=self.password, email=self.email)
        u2 = User(password=self.password, email=self.email)
        self.assertTrue(u.password_hash != u2.password_hash)

        token = self.user.generate_confirm_token()
        self.assertIsNotNone(self.user.verify_confirm_token(token))
        
    def test_follow(self):
        u2 = User(email='email2')
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(self.user.is_following(self.user))
        self.assertFalse(self.user.is_following(u2))
        timestamp_before = datetime.utcnow()
        self.user.follow(u2)
        self.assertTrue(self.user.is_following(u2))
        self.assertTrue(self.user.is_following(u2))
        db.session.add(self.user)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(self.user.following.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(u2 in self.user.following)
        self.user.unfollow(u2)
        self.assertTrue(self.user.following.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.user.follow(u2)
        self.assertTrue(self.user.following.count() == 1)
        db.session.add(self.user)
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(self.user.following.count() == 0)

    def test_post(self):
        self.assertTrue(self.user.posts.count() == 0)
        timestamp_before = datetime.utcnow()
        post = Post(body='test_post', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(self.user.posts.count() == 1)
        self.assertTrue(post.user_id == self.user.id)
        self.assertTrue(self.user.posts.first().body == 'test_post')
        self.assertTrue(timestamp_after > self.user.posts.first().timestamp > timestamp_before)
        db.session.delete(post)
        self.assertTrue(self.user.posts.count() == 0)

    def test_comment(self):
        self.assertTrue(self.user.comments.count() == 0)
        timestamp_before = datetime.utcnow()
        post = Post(body='test_post', user_id=self.user.id)
        db.session.add(post)
        comment = Comment(body='test_comment', post_id=post.id, user_id=self.user.id)
        db.session.add(comment)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(self.user.comments.count() == 1)
        self.assertTrue(comment.user_id == self.user.id)
        self.assertTrue(self.user.comments.first().body == 'test_comment')
        self.assertTrue(timestamp_after > self.user.comments.first().timestamp > timestamp_before)
        db.session.delete(comment)
        self.assertTrue(self.user.comments.count() == 0)

    def test_notification(self):
        self.assertIsNone(self.user.notifications.first())
        n = Notification(body='test', user_id=self.user.id)
        db.session.add(n)
        db.session.commit()
        self.assertEquals(self.user.notifications.first(), n)