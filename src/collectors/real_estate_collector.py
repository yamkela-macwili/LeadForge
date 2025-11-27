from .base_collector import BaseCollector
import random
from logger import logger

class RealEstateCollector(BaseCollector):
    def __init__(self, db_session=None):
        super().__init__("Real Estate", db_session)

    def collect(self, num_samples=10):
        logger.info(f"Starting Real Estate collection... Target: {num_samples}")
        
        # Simulated data sources
        agencies = ["Pam Golding", "Seeff", "Rawson", "Remax"]
        locations = ["Cape Town", "Johannesburg", "Durban", "Pretoria"]
        
        for i in range(num_samples):
            self.random_delay(0.5, 1.5)
            
            agency = random.choice(agencies)
            location = random.choice(locations)
            
            lead = {
                "first_name": f"Agent{i}",
                "last_name": f"Doe{i}",
                "email": f"agent{i}@{agency.lower().replace(' ', '')}.co.za",
                "phone": f"+278{random.randint(10000000, 99999999)}",
                "company": agency,
                "role": "Property Practitioner",
                "source": "Property24 (Simulated)",
                "url": f"https://www.property24.com/agent/{i}",
                "location": location
            }
            
            self.save_lead(lead)
            
        logger.info(f"Real Estate collection complete. Collected {len(self.data)} leads.")
