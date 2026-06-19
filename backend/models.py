"""
ZINARA ZOSS — backend/models.py
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db     = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), default='citizen')   # citizen | admin | super_admin
    id_number     = db.Column(db.String(50), unique=True, nullable=True)
    phone         = db.Column(db.String(20), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    vehicles     = db.relationship('Vehicle',     backref='owner',   lazy=True)
    applications = db.relationship('Application', backref='user',    lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'email':      self.email,
            'role':       self.role,
            'id_number':  self.id_number,
            'phone':      self.phone,
            'created_at': self.created_at.isoformat(),
            'is_active':  self.is_active,
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration    = db.Column(db.String(20), unique=True, nullable=False)
    make            = db.Column(db.String(50))
    model           = db.Column(db.String(50))
    year            = db.Column(db.Integer)
    color           = db.Column(db.String(30))
    engine_number   = db.Column(db.String(50))
    chassis_number  = db.Column(db.String(50))
    license_expiry  = db.Column(db.Date, nullable=True)
    status          = db.Column(db.String(20), default='active')   # active | expired
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'registration':   self.registration,
            'make':           self.make,
            'model':          self.model,
            'year':           self.year,
            'color':          self.color,
            'engine_number':  self.engine_number,
            'chassis_number': self.chassis_number,
            'license_expiry': self.license_expiry.isoformat() if self.license_expiry else None,
            'status':         self.status,
        }


class Application(db.Model):
    __tablename__ = 'applications'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id   = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    type         = db.Column(db.String(20), nullable=False)   # vehicle | radio | both
    amount       = db.Column(db.Float, default=0.0)
    status       = db.Column(db.String(20), default='pending')
    # pending → verified → paid → completed | rejected
    notes        = db.Column(db.Text, nullable=True)
    reviewed_by  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle      = db.relationship('Vehicle', foreign_keys=[vehicle_id], backref='applications')
    reviewer     = db.relationship('User',    foreign_keys=[reviewed_by])

    def to_dict(self):
        return {
            'id':          self.id,
            'user_id':     self.user_id,
            'vehicle_id':  self.vehicle_id,
            'type':        self.type,
            'amount':      self.amount,
            'status':      self.status,
            'notes':       self.notes,
            'created_at':  self.created_at.isoformat(),
            'updated_at':  self.updated_at.isoformat() if self.updated_at else None,
            'user':        self.user.name if self.user else None,
            'vehicle_reg': self.vehicle.registration if self.vehicle else None,
        }
