from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from database import get_db, User
from auth import authenticate_user, create_default_admin
from logger import logger

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint to get JWT token."""
    data = request.form or request.json
    
    if not data:
        return jsonify({"detail": "No data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"detail": "Username and password required"}), 400
    
    db = next(get_db())
    try:
        user = authenticate_user(db, username, password)
        if not user:
            return jsonify({"detail": "Incorrect email or password"}), 401
        
        access_token = create_access_token(identity=user.email)
        return jsonify({
            "access_token": access_token,
            "token_type": "bearer"
        }), 200
    finally:
        db.close()
