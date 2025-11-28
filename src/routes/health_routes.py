from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def root():
    """API welcome message."""
    return jsonify({"message": "Welcome to LeadForge API v3.0 (Flask)"}), 200

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200
