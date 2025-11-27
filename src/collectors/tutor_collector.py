from .base_collector import BaseCollector
import random
from datetime import datetime

class TutorCollector(BaseCollector):
    def __init__(self):
        super().__init__("Tutors")

    def collect(self, num_samples=50):
        """
        Simulates collection of tutor data.
        """
        print(f"Starting collection for {self.niche_name}...")
        
        subjects = ["Math", "Science", "English", "Accounting", "Physics"]
        areas = ["Sandton", "Cape Town", "Durban", "Pretoria", "Johannesburg"]
        
        for i in range(num_samples):
            # self.random_delay(0.1, 0.5)
            
            tutor = {
                "name": f"Tutor {i+1}",
                "subject": random.choice(subjects),
                "area": random.choice(areas),
                "phone": f"07{random.randint(2, 9)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
                "email": f"tutor{i+1}@example.com",
                "hourly_rate": random.randint(150, 400),
                "experience_years": random.randint(1, 15),
                "verified": True,
                "collected_at": datetime.now().isoformat()
            }
            self.data.append(tutor)
            
        print(f"Collected {len(self.data)} items.")
