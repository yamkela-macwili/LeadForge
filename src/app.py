from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from database import init_db, get_db
from auth import create_default_admin
from logger import logger
from websocket_server import init_socketio
    
# Import blueprints
from routes.auth_routes import auth_bp
from routes.lead_routes import lead_bp
from routes.scraper_routes import scraper_bp
from routes.health_routes import health_bp
from routes.ui_routes import ui_bp
from routes.scoring_routes import scoring_bp
from routes.recommendation_routes import recommendation_bp
from routes.marketplace_routes import marketplace_bp

def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt = JWTManager(app)
    CORS(app)
    
    # Initialize database
    with app.app_context():
        init_db()
        db = next(get_db())
        try:
            create_default_admin(db)
            logger.info("Database initialized and default admin created")
        finally:
            db.close()
    
    # Register blueprints
    app.register_blueprint(ui_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(lead_bp)
    app.register_blueprint(scraper_bp)
    app.register_blueprint(scoring_bp)  # Phase 1: ML Lead Scoring
    app.register_blueprint(recommendation_bp)  # Phase 1: Recommendation Engine
    app.register_blueprint(marketplace_bp)  # Phase 1: Marketplace MVP
    
    # Initialize WebSocket server (Phase 1: Real-Time Dashboard)
    socketio = init_socketio(app)
    app.socketio = socketio
    
    logger.info("Flask application initialized with WebSocket support")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Use socketio.run() instead of app.run() for WebSocket support
    app.socketio.run(
        app,
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
