from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db, Lead, Source, User, init_db
from collectors.real_estate_collector import RealEstateCollector
from collectors.tutor_collector import TutorCollector
from collectors.service_provider_collector import ServiceProviderCollector
from auth import authenticate_user, create_access_token, get_current_user, create_default_admin, ACCESS_TOKEN_EXPIRE_MINUTES
from logger import logger
import asyncio
from datetime import timedelta

app = FastAPI(title="LeadForge API", version="3.0.0")

# Initialize database and create default admin on startup
@app.on_event("startup")
def startup_event():
    init_db()
    db = next(get_db())
    try:
        create_default_admin(db)
        logger.info("Database initialized and default admin created")
    finally:
        db.close()

# Dependency to get DB session
def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to LeadForge API v3.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint to get JWT token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def run_collector_task(collector_cls, niche_name: str, db: Session):
    logger.info(f"Starting background task for {niche_name}")
    collector = collector_cls(db)
    await collector.collect(num_samples=20)
    logger.info(f"Background task for {niche_name} completed")

@app.post("/scrape/{niche}")
async def trigger_scrape(
    niche: str, 
    background_tasks: BackgroundTasks, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Trigger scraping job. Requires Pro or Enterprise subscription."""
    # Check subscription tier
    if current_user.subscription_tier == "Free":
        raise HTTPException(
            status_code=403,
            detail="Scraping is not available on Free tier. Please upgrade to Pro or Enterprise."
        )
    
    niche_map = {
        "real_estate": (RealEstateCollector, "Real Estate"),
        "tutors": (TutorCollector, "Tutors"),
        "service_providers": (ServiceProviderCollector, "Service Providers")
    }
    
    key = niche.lower().replace(" ", "_")
    if key not in niche_map:
        raise HTTPException(status_code=404, detail=f"Niche '{niche}' not found. Available: {list(niche_map.keys())}")
    
    collector_cls, name = niche_map[key]
    
    await run_collector_task(collector_cls, name, db)
    
    return {"message": f"Scraping started for {name}", "status": "processing"}

@app.get("/leads")
def get_leads(
    niche: str = None, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get leads. Free tier limited to 5 leads."""
    # Enforce subscription limits
    if current_user.subscription_tier == "Free":
        limit = min(limit, 5)
    
    query = db.query(Lead)
    if niche:
        query = query.filter(Lead.niche == niche)
    
    leads = query.order_by(Lead.date_added.desc()).limit(limit).all()
    return [lead.to_dict() for lead in leads]

@app.get("/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    """Get lead statistics. Requires authentication."""
    from sqlalchemy import func
    stats = db.query(Lead.niche, func.count(Lead.id)).group_by(Lead.niche).all()
    return {niche: count for niche, count in stats}
