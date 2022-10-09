from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(512))
    email = db.Column(db.String(50), unique=True)
    avatar = db.Column(db.LargeBinary)
    bitcoin_address = db.Column(db.String(40))
    confirmed_email = db.Column(db.Boolean, default=False)
    creation_date = db.Column(db.Date)
    last_seen_date = db.Column(db.DateTime)
    level = db.Column(db.Integer, default=1)
    invitation_code = db.Column(db.String(10), unique=True)
    inviter_code = db.Column(db.String(10))
    invitation_commission = db.Column(db.Float(10), default=0)
    task_profit = db.Column(db.Float(10), default=0)
    balance = db.Column(db.Float, default=0)

    tasks = db.relationship('Task', backref='user')
    payments = db.relationship('Payment', backref='user')

    def __init__(self, username, email, password, invitation_code, inviter_code):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.creation_date = datetime.now()
        self.last_seen_date = datetime.now()
        self.invitation_code = invitation_code
        self.inviter_code = inviter_code

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    theme = db.Column(db.String(64))
    status = db.Column(db.Integer, default=0)
    image_proof = db.Column(db.LargeBinary)
    creation_date = db.Column(db.DateTime)
    assign_date = db.Column(db.DateTime)
    deadline_date = db.Column(db.DateTime)
    target_url = db.Column(db.String(64))
    info = db.Column(db.String(1024))
    submited = db.Column(db.DateTime)

    def __init__(self, admin_id, theme, url, days, info):
        self.admin_id = admin_id
        self.theme = theme
        self.creation_date = datetime.now()
        self.days = days
        self.url = url
        self.info = info

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(512))
    email = db.Column(db.String(25))
    creation_date = db.Column(db.Date)
    last_seen_date = db.Column(db.DateTime)
    
    tasks = db.relationship('Task', backref='admin')
    payments = db.relationship('Payment', backref='admin')

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.creation_date = datetime.now()
        self.last_seen_date = datetime.now()

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    amount = db.Column(db.Float(64))
    requested_date = db.Column(db.DateTime)
    tx_id = db.Column(db.String(64))
    on_hold = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)

    def __init__(self, user_id, amount):
        self.user_id = user_id
        self.amount = amount
        self.requested_date = datetime.now()

