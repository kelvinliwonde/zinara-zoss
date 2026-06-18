from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Vehicle, RadioLicense, RenewalApplication
from datetime import datetime

renewal_bp = Blueprint('renewal', __name__)

@renewal_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_renewal():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if 'application_type' not in data:
        return jsonify({'error': 'application_type is required'}), 400
    
    app_type = data['application_type']
    if app_type not in ['vehicle', 'radio', 'both']:
        return jsonify({'error': 'Invalid application_type. Must be vehicle, radio, or both'}), 400
    
    vehicle_id = data.get('vehicle_id')
    radio_license_id = data.get('radio_license_id')
    
    if app_type in ['vehicle', 'both'] and not vehicle_id:
        return jsonify({'error': 'vehicle_id is required for vehicle renewal'}), 400
    
    if app_type in ['radio', 'both'] and not radio_license_id:
        return jsonify({'error': 'radio_license_id is required for radio renewal'}), 400
    
    fee_amount = 0.00
    penalty_fee = 0.00
    
    if vehicle_id:
        vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        fee_amount += vehicle.calculate_fee()
        penalty_fee += vehicle.calculate_penalty()
    
    if radio_license_id:
        radio = RadioLicense.query.filter_by(id=radio_license_id, user_id=user_id).first()
        if not radio:
            return jsonify({'error': 'Radio license not found'}), 404
        fee_amount += radio.calculate_fee()
        penalty_fee += radio.calculate_penalty()
    
    total_amount = fee_amount + penalty_fee
    
    try:
        application = RenewalApplication(
            user_id=user_id,
            vehicle_id=vehicle_id,
            radio_license_id=radio_license_id,
            application_type=app_type,
            status='pending',
            fee_amount=fee_amount,
            penalty_fee=penalty_fee,
            total_amount=total_amount,
            notes=f"Renewal for {app_type} license"
        )
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Renewal application created successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@renewal_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = int(get_jwt_identity())
    
    applications = RenewalApplication.query.filter_by(user_id=user_id).order_by(
        RenewalApplication.application_date.desc()
    ).all()
    
    return jsonify({
        'applications': [app.to_dict() for app in applications]
    }), 200

@renewal_bp.route('/applications/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    user_id = int(get_jwt_identity())
    
    application = RenewalApplication.query.filter_by(id=application_id, user_id=user_id).first()
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    return jsonify({
        'application': application.to_dict()
    }), 200

@renewal_bp.route('/calculate-fees', methods=['POST'])
@jwt_required()
def calculate_fees():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    vehicle_id = data.get('vehicle_id')
    radio_license_id = data.get('radio_license_id')
    
    fee_amount = 0.00
    penalty_fee = 0.00
    
    if vehicle_id:
        vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()
        if vehicle:
            fee_amount += vehicle.calculate_fee()
            penalty_fee += vehicle.calculate_penalty()
    
    if radio_license_id:
        radio = RadioLicense.query.filter_by(id=radio_license_id, user_id=user_id).first()
        if radio:
            fee_amount += radio.calculate_fee()
            penalty_fee += radio.calculate_penalty()
    
    total_amount = fee_amount + penalty_fee
    
    return jsonify({
        'fee_amount': round(fee_amount, 2),
        'penalty_fee': round(penalty_fee, 2),
        'total_amount': round(total_amount, 2),
        'currency': 'USD'
    }), 200