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
    role          = db.Column(db.String(20), default='citizen')  # citizen | admin | super_admin
    id_number     = db.Column(db.String(50), unique=True, nullable=True)
    phone         = db.Column(db.String(20), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    vehicles       = db.relationship('Vehicle',      backref='owner', lazy=True)
    radio_licenses = db.relationship('RadioLicense', backref='owner', lazy=True)
    applications   = db.relationship('Application',  backref='user',  lazy=True)

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

    id                      = db.Column(db.Integer, primary_key=True)
    user_id                 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_number     = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type            = db.Column(db.String(50), nullable=True)
    make                    = db.Column(db.String(50))
    model                   = db.Column(db.String(50))
    year                    = db.Column(db.Integer)
    color                   = db.Column(db.String(30))
    engine_number           = db.Column(db.String(50), nullable=True)
    chassis_number          = db.Column(db.String(50), nullable=True)
    seating_capacity        = db.Column(db.Integer, default=5)
    tare_weight             = db.Column(db.Float, nullable=True)
    insurance_provider      = db.Column(db.String(100), nullable=True)
    insurance_policy_number = db.Column(db.String(100), nullable=True)
    insurance_expiry_date   = db.Column(db.String(20), nullable=True)
    license_expiry          = db.Column(db.Date, nullable=True)
    status                  = db.Column(db.String(20), default='active')
    is_active               = db.Column(db.Boolean, default=True)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                      self.id,
            'registration_number':     self.registration_number,
            'vehicle_type':            self.vehicle_type,
            'make':                    self.make,
            'model':                   self.model,
            'year':                    self.year,
            'color':                   self.color,
            'engine_number':           self.engine_number,
            'chassis_number':          self.chassis_number,
            'seating_capacity':        self.seating_capacity,
            'tare_weight':             self.tare_weight,
            'insurance_provider':      self.insurance_provider,
            'insurance_policy_number': self.insurance_policy_number,
            'insurance_expiry_date':   self.insurance_expiry_date,
            'license_expiry':          self.license_expiry.isoformat() if self.license_expiry else None,
            'status':                  self.status,
            'is_active':               self.is_active,
        }


class RadioLicense(db.Model):
    __tablename__ = 'radio_licenses'

    id                    = db.Column(db.Integer, primary_key=True)
    user_id               = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    radio_serial_number   = db.Column(db.String(100), unique=True, nullable=False)
    radio_make            = db.Column(db.String(100), nullable=False)
    radio_model           = db.Column(db.String(100), nullable=False)
    radio_type            = db.Column(db.String(50), nullable=False)
    installation_location = db.Column(db.String(200), nullable=True)
    license_expiry        = db.Column(db.Date, nullable=True)
    status                = db.Column(db.String(20), default='active')
    is_active             = db.Column(db.Boolean, default=True)
    created_at            = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                    self.id,
            'user_id':               self.user_id,
            'radio_serial_number':   self.radio_serial_number,
            'radio_make':            self.radio_make,
            'radio_model':           self.radio_model,
            'radio_type':            self.radio_type,
            'installation_location': self.installation_location,
            'license_expiry':        self.license_expiry.isoformat() if self.license_expiry else None,
            'status':                self.status,
            'is_active':             self.is_active,
            'created_at':            self.created_at.isoformat(),
        }


class Application(db.Model):
    __tablename__ = 'applications'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id  = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    radio_id    = db.Column(db.Integer, db.ForeignKey('radio_licenses.id'), nullable=True)
    type        = db.Column(db.String(20), nullable=False)
    amount      = db.Column(db.Float, default=0.0)
    status      = db.Column(db.String(20), default='pending')
    notes       = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle  = db.relationship('Vehicle',      foreign_keys=[vehicle_id])
    radio    = db.relationship('RadioLicense', foreign_keys=[radio_id])
    reviewer = db.relationship('User',         foreign_keys=[reviewed_by])

    def to_dict(self):
        return {
            'id':          self.id,
            'user_id':     self.user_id,
            'vehicle_id':  self.vehicle_id,
            'radio_id':    self.radio_id,
            'type':        self.type,
            'amount':      self.amount,
            'status':      self.status,
            'notes':       self.notes,
            'created_at':  self.created_at.isoformat(),
            'updated_at':  self.updated_at.isoformat() if self.updated_at else None,
            'user':        self.user.name if self.user else None,
            'vehicle_reg': self.vehicle.registration_number if self.vehicle else None,
        }
