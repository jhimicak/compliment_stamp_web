from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    stamps_received = db.relationship('Stamp', foreign_keys='Stamp.user_id', backref='receiver', lazy=True)
    coupons_received = db.relationship('Coupon', foreign_keys='Coupon.user_id', backref='owner', lazy=True)

class Stamp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.String(500), nullable=True) # Optional compliment message

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Null if auto-granted
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(200), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)

class EventConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stamps_required_for_coupon = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
