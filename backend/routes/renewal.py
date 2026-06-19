"""
ZINARA ZOSS — backend/routes/renewal.py
Handles /api/renewal/...
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Vehicle, RadioLicense, Application

renewal_bp = Blueprint('renewal', __name__)

FEES = {
    'vehicle': 50.00,
    'radio':   20.00,
    'both':    70.00,
}


@renewal_bp.route('/fees', methods=['GET'])
def get_fees():
    return jsonify({'fees': FEES})


@renewal_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_renewal():
    user_id = int(get_jwt_identity())
    data    = request.get_json() or {}

    renewal_type = (data.get('type') or '').lower()
    if renewal_type not in FEES:
        return jsonify({'error': 'type must be vehicle, radio, or both'}), 400

    vehicle_id = None
    radio_id   = None

    if renewal_type in ('vehicle', 'both'):
        vehicle_id = data.get('vehicle_id')
        if vehicle_id:
            vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=user_id).first()
            if not vehicle:
                return jsonify({'error': 'Vehicle not found or not owned by you'}), 404

    if renewal_type in ('radio', 'both'):
        radio_id = data.get('radio_id')
        if radio_id:
            radio = RadioLicense.query.filter_by(id=radio_id, user_id=user_id).first()
            if not radio:
                return jsonify({'error': 'Radio license not found or not owned by you'}), 404

    try:
        application = Application(
            user_id    = user_id,
            vehicle_id = vehicle_id,
            radio_id   = radio_id,
            type       = renewal_type,
            amount     = FEES[renewal_type],
            status     = 'pending',
            notes      = data.get('notes', ''),
        )
        db.session.add(application)
        db.session.commit()

        return jsonify({
            'message':     'Renewal submitted successfully',
            'application': application.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@renewal_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    user_id = int(get_jwt_identity())
    app     = Application.query.get_or_404(app_id)
    user    = User.query.get(user_id)

    if app.user_id != user_id and user.role not in ('admin', 'super_admin'):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({'application': app.to_dict()})


@renewal_bp.route('/my-applications', methods=['GET'])
@jwt_required()
def my_applications():
    user_id = int(get_jwt_identity())
    apps    = Application.query.filter_by(user_id=user_id)\
                               .order_by(Application.created_at.desc()).all()
    return jsonify({'applications': [a.to_dict() for a in apps]})


# ── Admin routes ──────────────────────────────────────────────
@renewal_bp.route('/admin/all', methods=['GET'])
@jwt_required()
def admin_all_applications():
    admin = User.query.get_or_404(int(get_jwt_identity()))
    if admin.role not in ('admin', 'super_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    status = request.args.get('status')
    query  = Application.query
    if status:
        query = query.filter_by(status=status)

    apps = query.order_by(Application.created_at.desc()).all()
    return jsonify({'applications': [a.to_dict() for a in apps]})


@renewal_bp.route('/admin/<int:app_id>/approve', methods=['POST'])
@jwt_required()
def approve_application(app_id):
    admin = User.query.get_or_404(int(get_jwt_identity()))
    if admin.role not in ('admin', 'super_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    app = Application.query.get_or_404(app_id)
    if app.status != 'pending':
        return jsonify({'error': f'Cannot approve an application with status: {app.status}'}), 400

    app.status      = 'verified'
    app.reviewed_by = admin.id
    db.session.commit()
    return jsonify({'message': 'Application approved', 'application': app.to_dict()})


@renewal_bp.route('/admin/<int:app_id>/reject', methods=['POST'])
@jwt_required()
def reject_application(app_id):
    admin = User.query.get_or_404(int(get_jwt_identity()))
    if admin.role not in ('admin', 'super_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    app  = Application.query.get_or_404(app_id)
    data = request.get_json() or {}

    app.status      = 'rejected'
    app.reviewed_by = admin.id
    app.notes       = data.get('reason', app.notes)
    db.session.commit()
    return jsonify({'message': 'Application rejected', 'application': app.to_dict()})


@renewal_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    admin = User.query.get_or_404(int(get_jwt_identity()))
    if admin.role not in ('admin', 'super_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    all_apps = Application.query.all()
    revenue  = sum(a.amount for a in all_apps if a.status in ('paid', 'completed'))

    return jsonify({
        'total':     len(all_apps),
        'pending':   sum(1 for a in all_apps if a.status == 'pending'),
        'verified':  sum(1 for a in all_apps if a.status == 'verified'),
        'paid':      sum(1 for a in all_apps if a.status == 'paid'),
        'completed': sum(1 for a in all_apps if a.status == 'completed'),
        'rejected':  sum(1 for a in all_apps if a.status == 'rejected'),
        'revenue':   round(revenue, 2),
    })
