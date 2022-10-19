from api.exceptions import ValidationError
from api.app import db
import secrets
from datetime import datetime, timedelta
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from time import time
import jwt
        
assignment = db.Table(
    'assignment',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('assignee_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('assigned_id', db.Integer, db.ForeignKey('user.id')),
)

follower = db.Table(
    'follower',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        return '<Token %r>' % self.id

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])

    def expire(self):
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @property
    def user(self):
        return User.query.get(self.user_id)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        Token.query.filter(Token.refresh_expiration < yesterday).delete()


class User(UserMixin, db.Model):
    """
    A class to represent a user.
    
    ...
    
    Attributes
    ----------
    id : int
        the user's id
    username : str
        the user's username 
    
    """
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(16), default='user')
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    tokens = db.relationship('Token', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    tasks = db.relationship(
        'Task',
        secondary=assignment,
        primaryjoin=(assignment.c.assignee_id == id),
        secondaryjoin=(assignment.c.assigned_id == id),
        lazy='dynamic')
    following = db.relationship(
        'User',
        cascade="all, delete-orphan",
        single_parent=True,
        secondary=follower,
        primaryjoin=(follower.c.follower_id == id),
        secondaryjoin=(follower.c.followed_id == id),
        back_populates='followers',
        lazy='dynamic')
    followers = db.relationship(
        'User',
        cascade="all, delete-orphan",
        single_parent=True,
        secondary=follower,
        primaryjoin=(follower.c.followed_id == id),
        secondaryjoin=(follower.c.follower_id == id),
        back_populates='following',
        lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email == current_app.config['ADMIN']:
            self.role = 'admin'
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        self.follow(self)

    def get_roles(self):
        return db.session.get(Role, self.role_id).name

    def update(self, data):
        if 'username' in data:
            self.username = data['username']
        if 'email' in data:
            self.email = data['email']
        if 'name' in data:
            self.name = data['name']

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token, refresh_token=None):
        token = Token.query.filter_by(
            access_token=access_token).first()
        if token:
            if token.access_expiration > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        token = Token.query.filter_by(
            refresh_token=refresh_token, access_token=access_token).first()
        if token:
            if token.refresh_expiration > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token

            # Someone tried to refresh with an expired token
            # Revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.add(token)
            db.session.commit()

    def revoke_all(self):
        for token in self.tokens:
            token.expire()

    def generate_confirm_token(self):
        return jwt.encode(
            {'confirm': self.id, 'exp': time() + expiration},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    def confirm(self, reset_token):
        try:
            email = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])['email']
        except jwt.PyJWTError:
            return
        self.confirmed = self.email == email
        return self.confirmed

    def generate_reset_token(self, expiration=3600):
        return jwt.encode(
            {'reset': self.id, 'exp': time() + expiration},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_token(reset_token):
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return db.session.scalar(User.select().filter_by(
            email=data['reset_email']))

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self):
        return md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://www.gravatar.com/avatar'
        hash = md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            db.session.execute(
                follower.insert().values(
                    follower_id=self.id,
                    followed_id=user.id)
            )

    def unfollow(self, user):
        if self.is_following(user):
            db.session.execute(
                follower.delete().where(
                follower.c.follower_id == self.id,
                follower.c.followed_id == user.id))

    def is_following(self, user):
        return user in self.following 
    
    def is_following_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower=user.id).first() is not None

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    @property
    def assigned_tasks(self):
        return self.tasks.filter_by(assigned_id=self.id)

    @property
    def assigneed_tasks(self):
        return self.tasks.filter_by(assignee_id=self.id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
 
    def update(self, data):
        self.body = data['body']       


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Notification {}>'.format(self.body)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True)
    value = db.Column(db.Float)
    description = db.Column(db.String(256))
    complete = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    start_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    last_update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    url = db.Column(db.String(128))
    input_data = db.Column(db.LargeBinary)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignee = db.relationship(
        'User',
        back_populates='tasks',
        foreign_keys=[assignee_id])
    assigned = db.relationship(
        'User',
        back_populates='tasks',
        foreign_keys=[assigned_id])

    def __repr__(self):
        return '<Task %r>' % (self.name)