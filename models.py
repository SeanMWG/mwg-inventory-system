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

    # Define relationships correctly with explicit foreign keys
    checkouts = db.relationship("Checkout", foreign_keys="Checkout.user_id", back_populates="user")

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
    is_loaner = db.Column(db.Boolean, default=False)
    
    # Updated relationships with explicit foreign keys to avoid ambiguity
    loans = db.relationship('Loan', foreign_keys="Loan.item_id", backref='inventory_item', lazy=True)
    checkouts = db.relationship("Checkout", foreign_keys="Checkout.item_id", backref="inventory_item", lazy=True)
    changes = db.relationship('ChangeLog', foreign_keys="ChangeLog.item_id", backref='item', lazy=True)

    def __repr__(self):
        return f'<Inventory {self.asset_tag}>'

class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    change_description = db.Column(db.String(255), nullable=False)

    user = db.relationship('User', backref='changes')

class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Match the existing database columns
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    
    # Remove inventory_id for now since it doesn't exist in the database yet
    # inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id', name="fk_checkout_inventory_id"), nullable=True)

    # Define relationship with explicit foreign key to avoid ambiguity
    user = db.relationship("User", foreign_keys=[user_id], back_populates="checkouts")
