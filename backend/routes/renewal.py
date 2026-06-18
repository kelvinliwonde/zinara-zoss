from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Vehicle, RadioLicense, RenewalApplication, Payment
from datetime import datetime
import json

renewal_bp = Blueprint('renewal', __name__)

@renewal_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_renewal():
    """Apply for license renewal with auto-integration to ZINARA"""
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
    vehicle = None
    radio = None
    
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
        # Create renewal application
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
        
        # ---------- AUTO-INTEGRATION WITH ZINARA ----------
        from services.zinara_integration import ZINARAIntegration
        user = User.query.get(user_id)
        
        # Step 1: Verify vehicle with ZINARA
        vehicle_verified = True
        if vehicle:
            vehicle_result = ZINARAIntegration.check_vehicle_status(vehicle.registration_number)
            if not vehicle_result['success']:
                application.notes = f"Vehicle verification failed: {vehicle_result.get('message', 'Unknown error')}"
                db.session.commit()
                return jsonify({
                    'error': f'Vehicle verification failed: {vehicle_result.get("message", "Vehicle not found")}',
                    'application': application.to_dict()
                }), 400
            vehicle_verified = True
        
        # Step 2: Verify radio with ZBC
        radio_verified = True
        if radio:
            radio_result = ZINARAIntegration.check_radio_license(radio.radio_serial_number)
            if not radio_result['success']:
                application.notes = f"Radio verification failed: {radio_result.get('message', 'Unknown error')}"
                db.session.commit()
                return jsonify({
                    'error': f'Radio verification failed: {radio_result.get("message", "Radio license not valid")}',
                    'application': application.to_dict()
                }), 400
            radio_verified = True
        
        # Step 3: Submit to ZINARA
        application_data = {
            'application_id': application.id,
            'user': user.to_dict(),
            'vehicle': vehicle.to_dict() if vehicle else None,
            'radio': radio.to_dict() if radio else None,
            'application_type': application.application_type,
            'fee_amount': float(application.fee_amount),
            'penalty_fee': float(application.penalty_fee),
            'total_amount': float(application.total_amount)
        }
        
        zinara_result = ZINARAIntegration.submit_application(application_data)
        
        if zinara_result['success']:
            application.status = 'verified'
            application.verification_date = datetime.utcnow()
            application.notes = f"Submitted to ZINARA. Ref: {zinara_result.get('reference_number', 'N/A')}"
            db.session.commit()
            
            # Step 4: Process payment automatically
            payment_result = ZINARAIntegration.process_payment(
                application.id,
                float(application.total_amount),
                'ecocash'
            )
            
            if payment_result['success']:
                # Create payment record
                payment = Payment(
                    application_id=application.id,
                    user_id=user_id,
                    payment_method='ecocash',
                    payment_reference=payment_result['payment_reference'],
                    amount=application.total_amount,
                    status='completed',
                    transaction_id=payment_result['transaction_id'],
                    payment_date=datetime.utcnow(),
                    gateway_response=json.dumps(payment_result)
                )
                db.session.add(payment)
                
                # Step 5: Generate digital license
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
                        'message': '✅ Renewal completed successfully! Your digital license is ready.',
                        'application': application.to_dict(),
                        'license': license_result,
                        'payment': payment_result
                    }), 201
                else:
                    # License generation failed but payment was processed
                    application.status = 'paid'
                    db.session.commit()
                    return jsonify({
                        'message': 'Payment processed but license generation failed. Please contact support.',
                        'application': application.to_dict(),
                        'payment': payment_result
                    }), 200
            else:
                # Payment failed but application was submitted
                return jsonify({
                    'message': 'Application submitted to ZINARA but payment failed. Please try again.',
                    'application': application.to_dict(),
                    'payment': payment_result
                }), 200
        else:
            # ZINARA submission failed
            application.notes = f"ZINARA submission failed: {zinara_result.get('message', 'Unknown error')}"
            db.session.commit()
            return jsonify({
                'message': 'Application created but ZINARA submission failed. Please try again.',
                'application': application.to_dict(),
                'error': zinara_result.get('message', 'Unknown error')
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@renewal_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get all renewal applications for current user"""
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
    """Get specific renewal application"""
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
    """Calculate renewal fees without creating application"""
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