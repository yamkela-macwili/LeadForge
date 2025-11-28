from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, Lead, Source
from collectors.real_estate_collector import RealEstateCollector
from collectors.tutor_collector import TutorCollector
from collectors.service_provider_collector import ServiceProviderCollector
from logger import logger
import asyncio

app = FastAPI(title="LeadForge API", version="3.0.0")

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

async def run_collector_task(collector_cls, niche_name: str, db: Session):
    logger.info(f"Starting background task for {niche_name}")
    collector = collector_cls(db)
    await collector.collect(num_samples=20)
    logger.info(f"Background task for {niche_name} completed")

@app.post("/scrape/{niche}")
async def trigger_scrape(niche: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db_session)):
    niche_map = {
        "real_estate": (RealEstateCollector, "Real Estate"),
        "tutors": (TutorCollector, "Tutors"),
        "service_providers": (ServiceProviderCollector, "Service Providers")
    }
    
    key = niche.lower().replace(" ", "_")
    if key not in niche_map:
        raise HTTPException(status_code=404, detail=f"Niche '{niche}' not found. Available: {list(niche_map.keys())}")
    
    collector_cls, name = niche_map[key]
    
    # Note: We need to be careful with passing DB session to background tasks. 
    # Ideally, the background task should create its own session.
    # For now, we'll run it directly here to ensure it works, or refactor to create session inside task.
    # Since we are moving to async, let's await it directly for this step to verify, 
    # or better, use a fresh session in the background task function if we were doing true background processing.
    # For simplicity in this phase, let's await it to ensure completion before returning, 
    # or use BackgroundTasks with a new session factory.
    
    # Let's try awaiting it first to see the result immediately (easier for verification)
    # In a real prod app, we'd push to a queue (Celery/Redis).
    
    await run_collector_task(collector_cls, name, db)
    
    return {"message": f"Scraping started for {name}", "status": "processing"}

@app.get("/leads")
def get_leads(niche: str = None, limit: int = 100, db: Session = Depends(get_db_session)):
    query = db.query(Lead)
    if niche:
        query = query.filter(Lead.niche == niche)
    
    leads = query.order_by(Lead.date_added.desc()).limit(limit).all()
    return [lead.to_dict() for lead in leads]

@app.get("/stats")
def get_stats(db: Session = Depends(get_db_session)):
    from sqlalchemy import func
    stats = db.query(Lead.niche, func.count(Lead.id)).group_by(Lead.niche).all()
    return {niche: count for niche, count in stats}
