from api.app import db
from api.email import send_email
import secrets
from datetime import datetime, timedelta
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from time import time
import jwt
import requests


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


assignment = db.Table(
    'assignment',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('assigned_id', db.Integer, db.ForeignKey('user.id'))
)


follower = db.Table(
    'follower',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class Token(db.Model):
    """Token
    ----------------
    Attributes:
        id: int
        access_token: str
        access_expiration: datetime
        refresh_token: str
        refresh_expiration: datetime
        user_id: int
    ----------------
    Methods:
        generate: generate access and refresh tokens
        expire: expire access and refresh tokens
    """
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


class User(Updateable, db.Model):
    """User
    ----------------
    Attributes:
        id: int
        username: str
        email: str
        password_hash: str
        role: str
        confirmed: bool
        bitcoin_address: str
        name: str
        location: str
        member_since: datetime
        last_seen: datetime
        avatar: str
        tokens: relationship
        posts: relationship
        comments: relationship
        assigneed_tasks: relationship
        assigned_tasks: relationship
        following: relationship
        followers: relationship
    ----------------
    Methods:
        verify_password: check if password matches hashed password
        generate_auth_token: generate an auth token
        revoke_all: revoke all auth tokens
        generate_confirm_token: generate a confirm token
        generate_reset_token: generate a reset token
        ping: update last_seen
        follow: follow user
        unfollow: unfollow user
        is_following: check if user is following
        is_following_by: check if user is followed by
        add_notification: add notification
    ----------------
    Static Methods:
        verify_access_token: verify access token
        verufy_refresh_token: verify refresh token
        verify_confirm_token: verify a confirm token
        verify_reset_token: verify a reset token
    ----------------
    Properties:
        password: raise AttributeError
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(16), default='user')
    confirmed = db.Column(db.Boolean, default=False)
    bitcoin_address = db.Column(db.String(128), index=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar = db.Column(db.String(128))
    tokens = db.relationship('Token',
        backref='user',
        lazy='dynamic')
    posts = db.relationship('Post',
        backref='user',
        lazy='dynamic')
    comments = db.relationship('Comment',
        backref='user',
        lazy='dynamic')
    notifications = db.relationship('Notification',
        backref='user',
        lazy='dynamic')
    assigneed_tasks = db.relationship('Task',
        backref='user',
        lazy='dynamic')
    assigned_tasks = db.relationship('Task',
        secondary=assignment,
        primaryjoin=(assignment.c.assigned_id == id),
        lazy='dynamic')
    following = db.relationship('User',
        secondary=follower,
        primaryjoin=(follower.c.follower_id == id),
        secondaryjoin=(follower.c.followed_id == id),
        back_populates='followers',
        lazy='dynamic')
    followers = db.relationship('User',
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
        if self.email is not None and self.avatar is None:
            url = 'https://www.gravatar.com/avatar'
            avatar_hash = md5(self.email.lower().encode('utf-8'),
                              usedforsecurity=False).hexdigest()
            self.avatar = f'{url}/{avatar_hash}?d=identicon'
        send_email(to=kwargs['email'],
                   subject='Confirm Account',
                   template='confirm', user=self,
                   token=self.generate_confirm_token(),
                   url=f'/tokens/confirm?={self.generate_confirm_token()}')

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
            {'email': self.email},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_confirm_token(reset_token):
        try:
            email = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])['email']
        except jwt.PyJWTError:
            return None
        except KeyError:
            return None
        return db.session.scalar(User.query.filter_by(email=email))

    def generate_reset_token(self, expiration=3600):
        return jwt.encode(
            {'reset': self.id, 'exp': time() + expiration},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_token(reset_token):
        try:
            user_id = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])['reset']
        except jwt.PyJWTError:
            return
        return db.session.scalar(User.query.filter_by(id=user_id))

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

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
        return user in self.following or user == self
    
    def is_following_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower=user.id).first() is not None

    def add_notification(self, **kwargs):
        n = Notification(**kwargs)
        db.session.add(n)
        return n


class Post(db.Model):
    """Post
    ----------------
    Attributes:
        id: int
        body: str
        timestamp: datetime
        author_id: int fk
        comments: relationship
    ----------------
    Methods:
        update: update post body
    """
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
    """Comment
    ----------------
    Attributes:
        id: int
        body: str
        timestamp: datetime
        user_id: int fk
        post_id: int fk
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)


class Notification(db.Model):
    """Notification
    ----------------
    Attributes:
        id: int
        body: str
        read: bool
        user_id: int fk
        post_id: int fk
        comment_id: int fk
        timestamp: datetime
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Notification {}>'.format(self.body)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Task(Updateable, db.Model):
    """Task
    ----------------
    Attributes:
        id: int
        name: str
        value: int
        description: str
        completed: bool
        timestamp: datetime
        start_date: datetime
        due_date: datetime
        end_date: datetime
        last_updated_date: datetime
        url: str
        input_date: datetime
        txid: str
        assignee_id: int fk
        assignee: relationship
    ----------------
    Methods:
        start: start task
        ping: update last_updated_date
    ----------------
    Properties:
        transaction_status: get bitcoin transaction status
        transaction_amount: get bitcoin amount transaction
    """
    id = db.Column(db.Integer, primary_key=True, nullable=False)
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
    input_data = db.Column(db.String(512))
    txid = db.Column(db.String(128), db.CheckConstraint('txid IS NULL OR length(txid) = 64'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignee = db.relationship(
        'User',
        single_parent=True,
        overlaps='assigneed_tasks,user',
        foreign_keys=[assignee_id])

    def __repr__(self):
        return '<Task %r>' % (self.name)

    def start(self, user_id):
        db.session.execute(
            assignment.insert().values(
                task_id=self.id,
                assigned_id=user_id
            )
        )
        self.start_date = datetime.utcnow()
        self.last_update_date = datetime.utcnow()
        db.session.commit()

    def ping(self):
        self.last_update_date = datetime.utcnow()

    @property
    def transaction_status(self):
        if self.txid is None:
            return None
        res = requests.get('https://api.blockcypher.com/v1/btc/main/txs/' + self.txid).json()
        return res['confirmations'] or None

    @property
    def transaction_amount(self):
        if self.txid is None:
            return None
        res = requests.get('https://api.blockcypher.com/v1/btc/main/txs/' + self.txid).json()
        return float(res['total']) * 0.00000001 or None