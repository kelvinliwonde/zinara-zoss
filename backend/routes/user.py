from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Vehicle, RadioLicense

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(),
        'vehicles': [v.to_dict() for v in user.vehicles if v.is_active],
        'radio_licenses': [r.to_dict() for r in user.radio_licenses if r.is_active]
    }), 200

@user_bp.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    user_id = int(get_jwt_identity())
    vehicles = Vehicle.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        'vehicles': [v.to_dict() for v in vehicles]
    }), 200

@user_bp.route('/vehicles', methods=['POST'])
@jwt_required()
def add_vehicle():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['registration_number', 'vehicle_type', 'make', 'model', 'year', 
                      'engine_number', 'chassis_number', 'color', 'insurance_provider', 
                      'insurance_policy_number', 'insurance_expiry_date']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    if Vehicle.query.filter_by(registration_number=data['registration_number']).first():
        return jsonify({'error': 'Vehicle already registered'}), 409
    
    try:
        vehicle = Vehicle(
            user_id=user_id,
            registration_number=data['registration_number'].upper().strip(),
            vehicle_type=data['vehicle_type'],
            make=data['make'],
            model=data['model'],
            year=data['year'],
            engine_number=data['engine_number'].upper().strip(),
            chassis_number=data['chassis_number'].upper().strip(),
            color=data['color'],
            seating_capacity=data.get('seating_capacity', 5),
            tare_weight=data.get('tare_weight'),
            insurance_provider=data['insurance_provider'],
            insurance_policy_number=data['insurance_policy_number'].upper().strip(),
            insurance_expiry_date=data['insurance_expiry_date']
        )
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle added successfully',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/radio-licenses', methods=['GET'])
@jwt_required()
def get_radio_licenses():
    user_id = int(get_jwt_identity())
    radios = RadioLicense.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        'radio_licenses': [r.to_dict() for r in radios]
    }), 200

@user_bp.route('/radio-licenses', methods=['POST'])
@jwt_required()
def add_radio_license():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['radio_serial_number', 'radio_make', 'radio_model', 'radio_type']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    if RadioLicense.query.filter_by(radio_serial_number=data['radio_serial_number']).first():
        return jsonify({'error': 'Radio serial number already registered'}), 409
    
    try:
        radio = RadioLicense(
            user_id=user_id,
            radio_serial_number=data['radio_serial_number'].upper().strip(),
            radio_make=data['radio_make'],
            radio_model=data['radio_model'],
            radio_type=data['radio_type'],
            installation_location=data.get('installation_location')
        )
        db.session.add(radio)
        db.session.commit()
        
        return jsonify({
            'message': 'Radio license added successfully',
            'radio': radio.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500