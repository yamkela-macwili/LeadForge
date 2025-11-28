from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from database import get_db, Lead, User
from auth import authenticate_user
from sqlalchemy import func, or_
from logger import logger
import pandas as pd
import io

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    """Redirect root to login."""
    return redirect(url_for('ui.login'))

@ui_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = next(get_db())
        try:
            user = authenticate_user(db, email, password)
            if user:
                access_token = create_access_token(identity=user.email)
                response = make_response(redirect(url_for('ui.dashboard')))
                set_access_cookies(response, access_token)
                flash('Login successful!', 'success')
                return response
            else:
                flash('Invalid email or password', 'error')
        finally:
            db.close()
    
    return render_template('login.html')

@ui_bp.route('/dashboard')
@jwt_required()
def dashboard():
    """Dashboard page with stats."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        # Get user info
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Get stats
        stats = db.query(Lead.niche, func.count(Lead.id)).group_by(Lead.niche).all()
        stats_dict = {niche: count for niche, count in stats}
        
        return render_template('dashboard.html', user=user, stats=stats_dict)
    finally:
        db.close()

@ui_bp.route('/leads')
@jwt_required()
def leads():
    """Leads page with filtering and search."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Apply subscription limits
        limit = 500 if user.subscription_tier != "Free" else 5
        
        # Get filter parameters
        niche_filter = request.args.get('niche', '')
        search_query = request.args.get('search', '')
        
        # Build query
        query = db.query(Lead)
        
        # Apply niche filter
        if niche_filter:
            query = query.filter(Lead.niche == niche_filter)
        
        # Apply search
        if search_query:
            query = query.filter(
                or_(
                    Lead.first_name.ilike(f'%{search_query}%'),
                    Lead.last_name.ilike(f'%{search_query}%'),
                    Lead.email.ilike(f'%{search_query}%'),
                    Lead.company.ilike(f'%{search_query}%')
                )
            )
        
        # Get leads
        all_leads = query.order_by(Lead.date_added.desc()).limit(limit).all()
        
        # Get unique niches for filter dropdown
        niches = db.query(Lead.niche).distinct().all()
        niche_list = [n[0] for n in niches]
        
        return render_template('leads.html', user=user, leads=all_leads, niches=niche_list, current_niche=niche_filter, search_query=search_query)
    finally:
        db.close()

@ui_bp.route('/leads/download')
@jwt_required()
def download_leads():
    """Download leads as CSV."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Apply subscription limits
        limit = 500 if user.subscription_tier != "Free" else 5
        
        # Get filter parameters
        niche_filter = request.args.get('niche', '')
        search_query = request.args.get('search', '')
        
        # Build query
        query = db.query(Lead)
        
        if niche_filter:
            query = query.filter(Lead.niche == niche_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    Lead.first_name.ilike(f'%{search_query}%'),
                    Lead.last_name.ilike(f'%{search_query}%'),
                    Lead.email.ilike(f'%{search_query}%'),
                    Lead.company.ilike(f'%{search_query}%')
                )
            )
        
        all_leads = query.order_by(Lead.date_added.desc()).limit(limit).all()
        
        # Convert to DataFrame
        data = [lead.to_dict() for lead in all_leads]
        df = pd.DataFrame(data)
        
        # Create CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Send file
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='leads.csv'
        )
    finally:
        db.close()

@ui_bp.route('/logs')
@jwt_required()
def logs():
    """Logs viewer page."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        
        # Read last 100 lines of log file
        try:
            with open('app.log', 'r') as f:
                lines = f.readlines()
                log_content = ''.join(lines[-100:])
        except FileNotFoundError:
            log_content = 'Log file not found'
        
        return render_template('logs.html', user=user, logs=log_content)
    finally:
        db.close()
@ui_bp.route('/scraper')
@jwt_required()
def scraper():
    """Scraper control page."""
    current_user_email = get_jwt_identity()
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        return render_template('scraper.html', user=user)
    finally:
        db.close()

@ui_bp.route('/logout')
def logout():
    """Logout and clear cookies."""
    response = make_response(redirect(url_for('ui.login')))
    unset_jwt_cookies(response)
    flash('Logged out successfully', 'success')
    return response
