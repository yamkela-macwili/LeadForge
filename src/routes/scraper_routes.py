from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db, User
from collectors.real_estate_collector import RealEstateCollector
from collectors.tutor_collector import TutorCollector
from collectors.service_provider_collector import ServiceProviderCollector
from logger import logger

scraper_bp = Blueprint('scraper', __name__, url_prefix='/api')

@scraper_bp.route('/scrape/<niche>', methods=['POST'])
@jwt_required()
def trigger_scrape(niche):
    """Trigger scraping job. Requires Pro or Enterprise subscription."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        # Get current user
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Check subscription tier
        if user and user.subscription_tier == "Free":
            return jsonify({
                "detail": "Scraping is not available on Free tier. Please upgrade to Pro or Enterprise."
            }), 403
        
        niche_map = {
            "real_estate": (RealEstateCollector, "Real Estate"),
            "tutors": (TutorCollector, "Tutors"),
            "service_providers": (ServiceProviderCollector, "Service Providers")
        }
        
        key = niche.lower().replace(" ", "_")
        if key not in niche_map:
            return jsonify({
                "detail": f"Niche '{niche}' not found. Available: {list(niche_map.keys())}"
            }), 404
        
        collector_cls, name = niche_map[key]
        
        # Run collector synchronously
        logger.info(f"Starting scraping for {name}")
        collector = collector_cls(db)
        collector.collect(num_samples=20)
        logger.info(f"Scraping completed for {name}")
        
        return jsonify({
            "message": f"Scraping completed for {name}",
            "status": "success"
        }), 200
    finally:
        db.close()
