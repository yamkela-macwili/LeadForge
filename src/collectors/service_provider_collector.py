from .base_collector import BaseCollector
import random
from logger import logger

class ServiceProviderCollector(BaseCollector):
    def __init__(self, db_session=None):
        super().__init__("Service Providers", db_session)

    async def collect(self, num_samples=10):
        logger.info(f"Starting Service Provider collection... Target: {num_samples}")
        
        services = ["Plumber", "Electrician", "Locksmith", "Mechanic"]
        
        for i in range(num_samples):
            await self.random_delay(0.5, 1.5)
            
            service = random.choice(services)
            
            lead = {
                "first_name": f"Pro{i}",
                "last_name": f"Fixit{i}",
                "email": f"contact@{service.lower()}{i}.co.za",
                "phone": f"+278{random.randint(10000000, 99999999)}",
                "company": f"{service} Pros {i}",
                "role": service,
                "source": "Bark (Simulated)",
                "url": f"https://www.bark.com/en/za/company/{i}",
                "location": "Cape Town"
            }
            
            self.save_lead(lead)
            
        logger.info(f"Service Provider collection complete. Collected {len(self.data)} leads.")
