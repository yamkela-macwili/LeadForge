from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from database import get_db, User

# Security Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user."""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_default_admin(db: Session):
    """Create a default admin user if none exists."""
    admin = get_user_by_email(db, "admin@leadforge.com")
    if not admin:
        admin = User(
            email="admin@leadforge.com",
            hashed_password=get_password_hash("admin"),
            is_active=1,
            is_superuser=1,
            subscription_tier="Enterprise"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin
