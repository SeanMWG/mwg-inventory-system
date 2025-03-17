from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Editor, Reader

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "Admin"

    def is_editor(self):
        return self.role == "Editor"

    def is_reader(self):
        return self.role == "Reader"

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False)
    room_number = db.Column(db.String(20), nullable=True)
    room_name = db.Column(db.String(100), nullable=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    category = db.Column(db.String(100))
    notes = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.String(100), nullable=True)
    date_assigned = db.Column(db.Date, nullable=True)
    date_decommissioned = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Inventory {self.asset_tag}>'

class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)  # ✅ Store username instead of user ID
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    inventory_item = db.relationship('Inventory', backref=db.backref('loan', lazy=True))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # Checked Out, Returned, etc.
    user = db.Column(db.String(100), nullable=False)  # Who performed the action
    item_name = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    change_description = db.Column(db.String(255), nullable=False)

    user = db.relationship('User', backref='changes')
    item = db.relationship('Inventory', backref='changes')


