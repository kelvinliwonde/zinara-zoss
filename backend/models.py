from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
import re
import hashlib

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='citizen')
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)
    radio_licenses = db.relationship('RadioLicense', backref='owner', lazy=True)
    renewal_applications = db.relationship('RenewalApplication', backref='applicant', lazy=True)
    payments = db.relationship('Payment', backref='payer', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    
    def __init__(self, national_id, full_name, email, phone, password, role='citizen'):
        self.national_id = national_id.upper().strip()
        self.full_name = full_name.title().strip()
        self.email = email.lower().strip()
        self.phone = self._format_phone(phone)
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
    
    def _format_phone(self, phone):
        phone = re.sub(r'\D', '', phone)
        if phone.startswith('0'):
            phone = '263' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
        return phone
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_access_token(self):
        return create_access_token(identity=str(self.id), additional_claims={
            'role': self.role,
            'name': self.full_name
        })
    
    def generate_refresh_token(self):
        return create_refresh_token(identity=str(self.id))
    
    def to_dict(self):
        return {
            'id': self.id,
            'national_id': self.national_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    engine_number = db.Column(db.String(50), nullable=False)
    chassis_number = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    seating_capacity = db.Column(db.Integer, default=5)
    tare_weight = db.Column(db.Integer)
    insurance_provider = db.Column(db.String(100), nullable=False)
    insurance_policy_number = db.Column(db.String(50), nullable=False)
    insurance_expiry_date = db.Column(db.Date, nullable=False)
    last_renewal_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    renewal_applications = db.relationship('RenewalApplication', backref='vehicle', lazy=True)
    
    def calculate_fee(self):
        fees = {
            'Car': 50.00,
            'Kombi': 80.00,
            'Bus': 120.00,
            'Truck': 100.00,
            'Motorcycle': 30.00,
            'Trailer': 40.00
        }
        return fees.get(self.vehicle_type, 50.00)
    
    def calculate_penalty(self):
        if not self.expiry_date:
            return 0.00
        days_late = (datetime.now().date() - self.expiry_date).days
        if days_late <= 0:
            return 0.00
        penalty = min(days_late * 0.50, 45.00)
        return round(penalty, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'registration_number': self.registration_number,
            'vehicle_type': self.vehicle_type,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'engine_number': self.engine_number,
            'chassis_number': self.chassis_number,
            'color': self.color,
            'seating_capacity': self.seating_capacity,
            'tare_weight': self.tare_weight,
            'insurance_provider': self.insurance_provider,
            'insurance_policy_number': self.insurance_policy_number,
            'insurance_expiry_date': self.insurance_expiry_date.isoformat() if self.insurance_expiry_date else None,
            'last_renewal_date': self.last_renewal_date.isoformat() if self.last_renewal_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'fee': self.calculate_fee(),
            'penalty': self.calculate_penalty()
        }

class RadioLicense(db.Model):
    __tablename__ = 'radio_licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    radio_serial_number = db.Column(db.String(50), unique=True, nullable=False)
    radio_make = db.Column(db.String(50), nullable=False)
    radio_model = db.Column(db.String(50), nullable=False)
    radio_type = db.Column(db.String(30), nullable=False)
    installation_location = db.Column(db.String(100))
    last_renewal_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    renewal_applications = db.relationship('RenewalApplication', backref='radio_license', lazy=True)
    
    def calculate_fee(self):
        return 15.00
    
    def calculate_penalty(self):
        if not self.expiry_date:
            return 0.00
        days_late = (datetime.now().date() - self.expiry_date).days
        if days_late <= 0:
            return 0.00
        penalty = min(days_late * 0.25, 22.50)
        return round(penalty, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'radio_serial_number': self.radio_serial_number,
            'radio_make': self.radio_make,
            'radio_model': self.radio_model,
            'radio_type': self.radio_type,
            'installation_location': self.installation_location,
            'last_renewal_date': self.last_renewal_date.isoformat() if self.last_renewal_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'fee': self.calculate_fee(),
            'penalty': self.calculate_penalty()
        }

class RenewalApplication(db.Model):
    __tablename__ = 'renewal_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    radio_license_id = db.Column(db.Integer, db.ForeignKey('radio_licenses.id'))
    application_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='pending')
    fee_amount = db.Column(db.Numeric(10,2), nullable=False)
    penalty_fee = db.Column(db.Numeric(10,2), default=0.00)
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    verification_date = db.Column(db.DateTime)
    payment_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    qr_code = db.Column(db.String(255))
    digital_license_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    
    payments = db.relationship('Payment', backref='application', lazy=True)
    
    def generate_qr_code(self):
        import qrcode
        from io import BytesIO
        import base64
        
        data = f"ZINARA|{self.id}|{self.user_id}|{self.application_date.isoformat()}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        self.qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return self.qr_code
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vehicle_id': self.vehicle_id,
            'radio_license_id': self.radio_license_id,
            'application_type': self.application_type,
            'status': self.status,
            'fee_amount': float(self.fee_amount),
            'penalty_fee': float(self.penalty_fee),
            'total_amount': float(self.total_amount),
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'qr_code': self.qr_code,
            'digital_license_path': self.digital_license_path,
            'notes': self.notes
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('renewal_applications.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    payment_reference = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    settlement_date = db.Column(db.DateTime)
    gateway_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def generate_reference(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_hash = hashlib.md5(str(self.id).encode()).hexdigest()[:6]
        return f"ZIN{timestamp}{random_hash}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'user_id': self.user_id,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'amount': float(self.amount),
            'status': self.status,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'settlement_date': self.settlement_date.isoformat() if self.settlement_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }