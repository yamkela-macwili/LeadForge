from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db, Lead, User
from sqlalchemy import func
from logger import logger

lead_bp = Blueprint('leads', __name__, url_prefix='/api')

@lead_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_leads():
    """Get leads. Free tier limited to 5 leads."""
    current_user_email = get_jwt_identity()
    niche = request.args.get('niche')
    limit = request.args.get('limit', 100, type=int)
    
    db = next(get_db())
    try:
        # Get current user
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Enforce subscription limits
        if user and user.subscription_tier == "Free":
            limit = min(limit, 5)
        
        query = db.query(Lead)
        if niche:
            query = query.filter(Lead.niche == niche)
        
        leads = query.order_by(Lead.date_added.desc()).limit(limit).all()
        return jsonify([lead.to_dict() for lead in leads]), 200
    finally:
        db.close()

@lead_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get lead statistics. Requires authentication."""
    db = next(get_db())
    try:
        stats = db.query(Lead.niche, func.count(Lead.id)).group_by(Lead.niche).all()
        return jsonify({niche: count for niche, count in stats}), 200
    finally:
        db.close()
