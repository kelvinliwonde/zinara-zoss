# ============================================================
# ZINARA Integration Routes
# API endpoints that simulate ZINARA backend connection
# ============================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Vehicle, RadioLicense, RenewalApplication
from services.zinara_integration import ZINARAIntegration
from datetime import datetime

integration_bp = Blueprint('integration', __name__)

@integration_bp.route('/verify-vehicle', methods=['POST'])
@jwt_required()
def verify_vehicle():
    """Verify a vehicle with ZINARA's database"""
    data = request.get_json()
    registration_number = data.get('registration_number')
    
    if not registration_number:
        return jsonify({'error': 'Registration number is required'}), 400
    
    result = ZINARAIntegration.check_vehicle_status(registration_number)
    return jsonify(result), 200 if result['success'] else 404

@integration_bp.route('/verify-radio', methods=['POST'])
@jwt_required()
def verify_radio():
    """Verify radio license with ZBC"""
    data = request.get_json()
    radio_serial = data.get('radio_serial_number')
    
    if not radio_serial:
        return jsonify({'error': 'Radio serial number is required'}), 400
    
    result = ZINARAIntegration.check_radio_license(radio_serial)
    return jsonify(result), 200 if result['success'] else 404

@integration_bp.route('/submit-application', methods=['POST'])
@jwt_required()
def submit_to_zinara():
    """Submit renewal application to ZINARA"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    application_id = data.get('application_id')
    if not application_id:
        return jsonify({'error': 'Application ID is required'}), 400
    
    application = RenewalApplication.query.get(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Prepare application data for ZINARA
    user = User.query.get(user_id)
    vehicle = Vehicle.query.get(application.vehicle_id) if application.vehicle_id else None
    radio = RadioLicense.query.get(application.radio_license_id) if application.radio_license_id else None
    
    application_data = {
        'application_id': application.id,
        'user': {
            'full_name': user.full_name,
            'national_id': user.national_id,
            'email': user.email,
            'phone': user.phone
        },
        'vehicle': vehicle.to_dict() if vehicle else None,
        'radio': radio.to_dict() if radio else None,
        'application_type': application.application_type,
        'fee_amount': float(application.fee_amount),
        'penalty_fee': float(application.penalty_fee),
        'total_amount': float(application.total_amount)
    }
    
    # Submit to ZINARA
    result = ZINARAIntegration.submit_application(application_data)
    
    if result['success']:
        # Update application status
        application.status = 'verified'
        application.verification_date = datetime.utcnow()
        application.notes = f"Submitted to ZINARA. Reference: {result.get('reference_number', 'N/A')}"
        db.session.commit()
    
    return jsonify(result), 200

@integration_bp.route('/check-status/<reference_number>', methods=['GET'])
@jwt_required()
def check_application_status(reference_number):
    """Check application status with ZINARA"""
    result = ZINARAIntegration.check_application_status(reference_number)
    return jsonify(result), 200

@integration_bp.route('/process-payment', methods=['POST'])
@jwt_required()
def process_zinara_payment():
    """Process payment through ZINARA's gateway"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    application_id = data.get('application_id')
    payment_method = data.get('payment_method', 'ecocash')
    
    if not application_id:
        return jsonify({'error': 'Application ID is required'}), 400
    
    application = RenewalApplication.query.get(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Process payment
    result = ZINARAIntegration.process_payment(
        application_id,
        float(application.total_amount),
        payment_method
    )
    
    if result['success']:
        # Create payment record
        from models import Payment
        import hashlib
        import random
        
        payment = Payment(
            application_id=application.id,
            user_id=user_id,
            payment_method=payment_method,
            payment_reference=result['payment_reference'],
            amount=application.total_amount,
            status='completed',
            transaction_id=result['transaction_id'],
            payment_date=datetime.utcnow(),
            gateway_response=jsonify({
                'status': 'success',
                'reference': result['payment_reference']
            }).get_data(as_text=True)
        )
        db.session.add(payment)
        
        # Update application
        application.status = 'paid'
        application.payment_date = datetime.utcnow()
        db.session.commit()
        
        # Generate digital license
        user = User.query.get(user_id)
        vehicle = Vehicle.query.get(application.vehicle_id)
        
        license_result = ZINARAIntegration.generate_digital_license(
            application.id,
            user.to_dict(),
            vehicle.to_dict() if vehicle else {'registration_number': 'N/A'}
        )
        
        if license_result['success']:
            application.status = 'completed'
            application.completion_date = datetime.utcnow()
            application.qr_code = license_result['qr_code_data']
            application.digital_license_path = license_result['digital_download_url']
            db.session.commit()
            
            return jsonify({
                'message': 'Payment processed and license issued successfully!',
                'payment': result,
                'license': license_result
            }), 200
    
    return jsonify(result), 400 if not result['success'] else 200

@integration_bp.route('/system-status', methods=['GET'])
@jwt_required()
def get_system_status():
    """Get ZINARA system status"""
    result = ZINARAIntegration.get_real_time_data()
    return jsonify(result), 200

@integration_bp.route('/generate-license/<int:application_id>', methods=['POST'])
@jwt_required()
def generate_digital_license(application_id):
    """Generate a digital license for a completed application"""
    user_id = int(get_jwt_identity())
    
    application = RenewalApplication.query.get(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    if application.status != 'completed':
        return jsonify({'error': 'Application must be completed first'}), 400
    
    user = User.query.get(user_id)
    vehicle = Vehicle.query.get(application.vehicle_id)
    
    result = ZINARAIntegration.generate_digital_license(
        application.id,
        user.to_dict(),
        vehicle.to_dict() if vehicle else {'registration_number': 'N/A'}
    )
    
    if result['success']:
        application.qr_code = result['qr_code_data']
        application.digital_license_path = result['digital_download_url']
        db.session.commit()
    
    return jsonify(result), 200 if result['success'] else 400