from flask_login import UserMixin
from datetime import datetime
from extensions import db

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_projects = db.Column(db.Integer, nullable=False)
    max_engineers = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))
    subscription = db.relationship('Subscription', backref='users')
    card_token = db.Column(db.String(100))  # Store Viva Wallet card token
    projects = db.relationship('Project', backref='manager', lazy=True)
    assigned_projects = db.relationship('ProjectAssignment', backref='engineer', lazy=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(30)) 