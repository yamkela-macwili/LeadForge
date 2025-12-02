from abc import ABC, abstractmethod
import csv
import random
import time
from sqlalchemy.orm import Session
from database import Lead
from logger import logger

class BaseCollector(ABC):
    def __init__(self, niche_name, db_session: Session = None):
        self.niche_name = niche_name
        self.data = [] # Keeping for backward compatibility for now, but primary storage is DB
        self.db_session = db_session

    @abstractmethod
    def collect(self, num_samples=10):
        """
        Main method to execute the collection process.
        Should populate self.data with dictionaries and save to DB.
        """
        pass

    def save_lead(self, lead_data: dict):
        """
        Saves a single lead to the database.
        Checks for duplicates based on email or phone.
        Automatically scores the lead using ML.
        """
        if not self.db_session:
            logger.warning("No database session provided. Skipping DB save.")
            self.data.append(lead_data)
            return

        # Check for existing lead
        existing_lead = None
        if lead_data.get('email'):
            existing_lead = self.db_session.query(Lead).filter(Lead.email == lead_data['email']).first()
        
        if not existing_lead and lead_data.get('phone'):
            existing_lead = self.db_session.query(Lead).filter(Lead.phone == lead_data['phone']).first()

        if existing_lead:
            logger.info(f"Lead already exists: {lead_data.get('email') or lead_data.get('phone')}. Updating...")
            # Update fields if needed, for now just skip or update timestamp
            # existing_lead.date_added = datetime.utcnow()
        else:
            new_lead = Lead(
                email=lead_data.get('email'),
                phone=lead_data.get('phone'),
                first_name=lead_data.get('first_name'),
                last_name=lead_data.get('last_name'),
                company=lead_data.get('company'),
                role=lead_data.get('role'),
                niche=self.niche_name,
                source=lead_data.get('source'),
                url=lead_data.get('url'),
                location=lead_data.get('location')
            )
            
            # Phase 1: Automatically score the lead using ML
            try:
                from ml.lead_scorer import get_lead_scorer
                from datetime import datetime
                
                scorer = get_lead_scorer()
                score_result = scorer.score_lead(lead_data)
                
                new_lead.lead_score = score_result['score']
                new_lead.score_features = score_result['features']
                new_lead.score_updated_at = datetime.utcnow()
                
                logger.info(f"Scored new lead: {score_result['score']:.2f}")
            except Exception as e:
                logger.warning(f"Could not score lead: {e}")
                new_lead.lead_score = 0.0
            
            self.db_session.add(new_lead)
            try:
                self.db_session.commit()
                self.db_session.refresh(new_lead)  # Refresh to get the ID
                logger.info(f"Saved new lead: {lead_data.get('email') or lead_data.get('phone')}")
                self.data.append(lead_data) # Keep in memory for now for the report generator
                
                # Phase 1: Emit real-time WebSocket event for new lead
                try:
                    from websocket_server import emit_new_lead, emit_stats_update
                    emit_new_lead(new_lead.to_dict())
                    logger.debug(f"Emitted WebSocket event for new lead {new_lead.id}")
                except Exception as e:
                    logger.warning(f"Could not emit WebSocket event: {e}")
                    
            except Exception as e:
                self.db_session.rollback()
                logger.error(f"Error saving lead: {e}")

    def save_to_csv(self, filename):
        """
        Saves the collected data to a CSV file.
        """
        if not self.data:
            logger.warning("No data to save.")
            return
        
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")

    def random_delay(self, min_seconds=1, max_seconds=3):
        """
        Sleeps for a random amount of time to avoid rate limiting.
        """
        time.sleep(random.uniform(min_seconds, max_seconds))
