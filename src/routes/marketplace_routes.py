"""API routes for marketplace."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db, User, Transaction
from logger import logger
from datetime import datetime

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/api/marketplace')

# Define available packages (in a real app, these might be in the DB)
PACKAGES = [
    {
        "id": "starter",
        "name": "Starter Pack",
        "credits": 100,
        "price": 29.00,
        "description": "Perfect for trying out LeadForge",
        "features": ["100 Lead Credits", "Basic Support", "Standard Scoring"]
    },
    {
        "id": "pro",
        "name": "Pro Bundle",
        "credits": 500,
        "price": 99.00,
        "description": "Best value for growing businesses",
        "features": ["500 Lead Credits", "Priority Support", "Advanced Scoring", "Export to CSV"]
    },
    {
        "id": "enterprise",
        "name": "Enterprise Scale",
        "credits": 2000,
        "price": 299.00,
        "description": "For high-volume lead generation",
        "features": ["2000 Lead Credits", "Dedicated Account Manager", "Custom Integrations", "API Access"]
    }
]

@marketplace_bp.route('/packages', methods=['GET'])
@jwt_required()
def get_packages():
    """List available credit packages."""
    return jsonify({
        "packages": PACKAGES
    }), 200

@marketplace_bp.route('/purchase', methods=['POST'])
@jwt_required()
def purchase_package():
    """
    Purchase a credit package.
    Mock payment implementation.
    """
    data = request.get_json()
    package_id = data.get('package_id')
    
    if not package_id:
        return jsonify({"error": "Package ID is required"}), 400
        
    # Find package
    package = next((p for p in PACKAGES if p['id'] == package_id), None)
    if not package:
        return jsonify({"error": "Invalid package ID"}), 404
        
    current_user_email = get_jwt_identity()
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Mock Payment Processing
        # In a real app, we would integrate Stripe/PayPal here
        payment_success = True 
        
        if payment_success:
            # Create transaction record
            transaction = Transaction(
                user_id=user.id,
                amount=package['price'],
                credits=package['credits'],
                package_name=package['name'],
                status='completed'
            )
            db.add(transaction)
            
            # Update user credits
            user.credits += package['credits']
            
            # If purchasing Pro/Enterprise, update tier as well (optional logic)
            if package_id == 'pro' and user.subscription_tier == 'Free':
                user.subscription_tier = 'Pro'
            elif package_id == 'enterprise':
                user.subscription_tier = 'Enterprise'
                
            db.commit()
            
            logger.info(f"User {user.email} purchased {package['name']}")
            
            return jsonify({
                "message": "Purchase successful",
                "new_credits": user.credits,
                "transaction_id": transaction.id
            }), 200
        else:
            return jsonify({"error": "Payment failed"}), 400
            
    except Exception as e:
        db.rollback()
        logger.error(f"Purchase error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@marketplace_bp.route('/history', methods=['GET'])
@jwt_required()
def get_transaction_history():
    """Get user's transaction history."""
    current_user_email = get_jwt_identity()
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.created_at.desc()).all()
        
        history = [{
            "id": t.id,
            "package": t.package_name,
            "amount": t.amount,
            "credits": t.credits,
            "status": t.status,
            "date": t.created_at.isoformat()
        } for t in transactions]
        
        return jsonify({
            "history": history,
            "current_credits": user.credits
        }), 200
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
