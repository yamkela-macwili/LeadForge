from .base_collector import BaseCollector
import random
from logger import logger

class TutorCollector(BaseCollector):
    def __init__(self, db_session=None):
        super().__init__("Tutors", db_session)

    async def collect(self, num_samples=10):
        logger.info(f"Starting Tutor collection... Target: {num_samples}")
        
        subjects = ["Math", "Science", "English", "History", "Coding"]
        
        for i in range(num_samples):
            await self.random_delay(0.5, 1.5)
            
            subject = random.choice(subjects)
            
            lead = {
                "first_name": f"Tutor{i}",
                "last_name": f"Smith{i}",
                "email": f"tutor{i}@teachme.co.za",
                "phone": f"+278{random.randint(10000000, 99999999)}",
                "company": "Private Tutor",
                "role": f"{subject} Tutor",
                "source": "Superprof (Simulated)",
                "url": f"https://www.superprof.co.za/tutor/{i}",
                "location": "Online"
            }
            
            self.save_lead(lead)
            
        logger.info(f"Tutor collection complete. Collected {len(self.data)} leads.")
