from .base_collector import BaseCollector
import random
from datetime import datetime

class ServiceProviderCollector(BaseCollector):
    def __init__(self):
        super().__init__("Service Providers")

    def collect(self, num_samples=50):
        """
        Simulates collection of service provider data (Plumbers, Electricians, etc.).
        """
        print(f"Starting collection for {self.niche_name}...")
        
        services = ["Plumber", "Electrician", "Handyman", "Locksmith", "Painter"]
        areas = ["Randburg", "Midrand", "Centurion", "Bellville", "Umhlanga"]
        
        for i in range(num_samples):
            # self.random_delay(0.1, 0.5)
            
            provider = {
                "name": f"Provider {i+1}",
                "service": random.choice(services),
                "area": random.choice(areas),
                "phone": f"06{random.randint(2, 9)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
                "email": f"info@provider{i+1}.co.za",
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(5, 100),
                "verified": True,
                "collected_at": datetime.now().isoformat()
            }
            self.data.append(provider)
            
        print(f"Collected {len(self.data)} items.")
