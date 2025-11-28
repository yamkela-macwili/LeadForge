from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from database import init_db, get_db
from auth import create_default_admin
from logger import logger
    
# Import blueprints
from routes.auth_routes import auth_bp
from routes.lead_routes import lead_bp
from routes.scraper_routes import scraper_bp
from routes.health_routes import health_bp
from routes.ui_routes import ui_bp

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
    
    logger.info("Flask application initialized")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
