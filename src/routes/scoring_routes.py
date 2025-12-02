"""API routes for lead scoring functionality."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db, Lead, User
from ml.lead_scorer import get_lead_scorer
from datetime import datetime
from logger import logger

scoring_bp = Blueprint('scoring', __name__, url_prefix='/api')

@scoring_bp.route('/leads/<int:lead_id>/score', methods=['POST'])
@jwt_required()
def score_single_lead(lead_id):
    """Score a single lead by ID."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        # Get the lead
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return jsonify({"detail": f"Lead {lead_id} not found"}), 404
        
        # Score the lead
        scorer = get_lead_scorer()
        lead_data = lead.to_dict()
        score_result = scorer.score_lead(lead_data)
        
        # Update the lead with score
        lead.lead_score = score_result['score']
        lead.score_features = score_result['features']
        lead.score_updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Scored lead {lead_id}: {score_result['score']}")
        
        return jsonify({
            "lead_id": lead_id,
            "score": score_result['score'],
            "features": score_result['features'],
            "interpretation": scorer.get_score_interpretation(score_result['score'])
        }), 200
    
    except Exception as e:
        logger.error(f"Error scoring lead {lead_id}: {str(e)}")
        return jsonify({"detail": f"Error scoring lead: {str(e)}"}), 500
    finally:
        db.close()


@scoring_bp.route('/leads/batch-score', methods=['POST'])
@jwt_required()
def score_leads_batch():
    """Score multiple leads in batch."""
    current_user_email = get_jwt_identity()
    
    data = request.get_json()
    lead_ids = data.get('lead_ids', [])
    
    if not lead_ids:
        return jsonify({"detail": "No lead_ids provided"}), 400
    
    db = next(get_db())
    try:
        scorer = get_lead_scorer()
        results = []
        
        for lead_id in lead_ids:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                results.append({
                    "lead_id": lead_id,
                    "error": "Lead not found"
                })
                continue
            
            # Score the lead
            lead_data = lead.to_dict()
            score_result = scorer.score_lead(lead_data)
            
            # Update the lead
            lead.lead_score = score_result['score']
            lead.score_features = score_result['features']
            lead.score_updated_at = datetime.utcnow()
            
            results.append({
                "lead_id": lead_id,
                "score": score_result['score'],
                "interpretation": scorer.get_score_interpretation(score_result['score'])
            })
        
        db.commit()
        logger.info(f"Batch scored {len(results)} leads")
        
        return jsonify({
            "total_scored": len(results),
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Error in batch scoring: {str(e)}")
        return jsonify({"detail": f"Error in batch scoring: {str(e)}"}), 500
    finally:
        db.close()


@scoring_bp.route('/leads/top-scored', methods=['GET'])
@jwt_required()
def get_top_scored_leads():
    """Get highest quality leads based on score."""
    current_user_email = get_jwt_identity()
    
    limit = request.args.get('limit', 10, type=int)
    niche = request.args.get('niche', None)
    min_score = request.args.get('min_score', 0, type=float)
    
    db = next(get_db())
    try:
        # Get user for subscription limits
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Apply subscription limits
        if user and user.subscription_tier == "Free":
            limit = min(limit, 5)
        
        # Build query
        query = db.query(Lead).filter(Lead.lead_score >= min_score)
        
        if niche:
            query = query.filter(Lead.niche == niche)
        
        # Get top scored leads
        leads = query.order_by(Lead.lead_score.desc()).limit(limit).all()
        
        return jsonify({
            "count": len(leads),
            "leads": [lead.to_dict() for lead in leads]
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting top scored leads: {str(e)}")
        return jsonify({"detail": f"Error: {str(e)}"}), 500
    finally:
        db.close()


@scoring_bp.route('/leads/score-all', methods=['POST'])
@jwt_required()
def score_all_leads():
    """Score all leads that don't have a score yet (admin only)."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        # Check if user is admin
        user = db.query(User).filter(User.email == current_user_email).first()
        if not user or not user.is_superuser:
            return jsonify({"detail": "Admin access required"}), 403
        
        # Get all leads without scores or with old scores
        leads = db.query(Lead).filter(
            (Lead.lead_score == 0.0) | (Lead.lead_score == None)
        ).all()
        
        scorer = get_lead_scorer()
        scored_count = 0
        
        for lead in leads:
            lead_data = lead.to_dict()
            score_result = scorer.score_lead(lead_data)
            
            lead.lead_score = score_result['score']
            lead.score_features = score_result['features']
            lead.score_updated_at = datetime.utcnow()
            scored_count += 1
        
        db.commit()
        logger.info(f"Scored {scored_count} leads in bulk operation")
        
        return jsonify({
            "message": f"Successfully scored {scored_count} leads",
            "scored_count": scored_count
        }), 200
    
    except Exception as e:
        logger.error(f"Error in bulk scoring: {str(e)}")
        return jsonify({"detail": f"Error: {str(e)}"}), 500
    finally:
        db.close()
