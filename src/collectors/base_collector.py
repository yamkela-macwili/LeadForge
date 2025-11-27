from abc import ABC, abstractmethod
import pandas as pd
import time
import random
from sqlalchemy.orm import Session
from database import Lead
from logger import logger

class BaseCollector(ABC):
    def __init__(self, niche_name, db_session: Session = None):
        self.niche_name = niche_name
        self.data = [] # Keeping for backward compatibility for now, but primary storage is DB
        self.db_session = db_session

    @abstractmethod
    def collect(self):
        """
        Main method to execute the collection process.
        Should populate self.data with dictionaries.
        """
        pass

    def save_lead(self, lead_data: dict):
        """
        Saves a single lead to the database.
        Checks for duplicates based on email or phone.
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
            self.db_session.add(new_lead)
            try:
                self.db_session.commit()
                logger.info(f"Saved new lead: {lead_data.get('email') or lead_data.get('phone')}")
                self.data.append(lead_data) # Keep in memory for now for the report generator
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
