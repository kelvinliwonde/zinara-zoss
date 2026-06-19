"""
ZINARA ZOSS — backend/routes/integration.py
Handles /api/integration/...  (ZINARA system lookups)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User
from backend.services.zinara_integration import ZinaraIntegrationService

integration_bp = Blueprint('integration', __name__)
zinara_service = ZinaraIntegrationService()


@integration_bp.route('/lookup/vehicle', methods=['POST'])
@jwt_required()
def lookup_vehicle():
    data = request.get_json() or {}
    registration = (data.get('registration') or '').strip().upper()

    if not registration:
        return jsonify({'error': 'Registration number is required'}), 400

    result = zinara_service.lookup_vehicle(registration)
    if result.get('error'):
        return jsonify({'error': result['error']}), 404

    return jsonify({'vehicle': result})


@integration_bp.route('/lookup/radio', methods=['POST'])
@jwt_required()
def lookup_radio():
    data      = request.get_json() or {}
    license_number = (data.get('license_number') or '').strip()

    if not license_number:
        return jsonify({'error': 'Radio license number is required'}), 400

    result = zinara_service.lookup_radio_license(license_number)
    if result.get('error'):
        return jsonify({'error': result['error']}), 404

    return jsonify({'license': result})


@integration_bp.route('/status', methods=['GET'])
@jwt_required()
def integration_status():
    """Check if the ZINARA integration service is reachable."""
    status = zinara_service.health_check()
    return jsonify({'integration': status})
