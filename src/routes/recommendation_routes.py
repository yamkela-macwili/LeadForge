"""API routes for recommendation engine."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db, Lead, User
from ml.recommender import get_recommender
from logger import logger

recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/api/recommendations')

@recommendation_bp.route('/similar/<int:lead_id>', methods=['GET'])
@jwt_required()
def get_similar_leads(lead_id):
    """Get leads similar to a specific lead."""
    limit = request.args.get('limit', 5, type=int)
    
    db = next(get_db())
    try:
        recommender = get_recommender(db)
        similar_leads = recommender.get_similar_leads(lead_id, limit=limit)
        
        return jsonify({
            "lead_id": lead_id,
            "count": len(similar_leads),
            "similar_leads": similar_leads
        }), 200
    except Exception as e:
        logger.error(f"Error getting similar leads: {e}")
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()

@recommendation_bp.route('/trending', methods=['GET'])
@jwt_required()
def get_trending_niches():
    """Get trending niches based on recent activity."""
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 5, type=int)
    
    db = next(get_db())
    try:
        recommender = get_recommender(db)
        trending = recommender.get_trending_niches(days=days, limit=limit)
        
        return jsonify({
            "period_days": days,
            "trending": trending
        }), 200
    except Exception as e:
        logger.error(f"Error getting trending niches: {e}")
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()

@recommendation_bp.route('/for-you', methods=['GET'])
@jwt_required()
def get_personalized_recommendations():
    """Get personalized lead recommendations."""
    limit = request.args.get('limit', 5, type=int)
    
    db = next(get_db())
    try:
        # In a real app, we'd use the user ID to personalize
        # current_user = get_jwt_identity()
        
        recommender = get_recommender(db)
        recommendations = recommender.get_recommended_leads(limit=limit)
        
        return jsonify({
            "count": len(recommendations),
            "recommendations": recommendations
        }), 200
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()
