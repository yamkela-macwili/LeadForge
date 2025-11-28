from .base_enricher import BaseEnricher
import random

class GooglePlacesEnricher(BaseEnricher):
    def enrich(self, lead_data: dict) -> dict:
        # Mock enrichment logic
        # In production, this would call the Google Places API
        
        if not lead_data.get('company'):
            return lead_data
            
        # Simulate finding a rating and address
        lead_data['rating'] = round(random.uniform(3.5, 5.0), 1)
        lead_data['review_count'] = random.randint(5, 500)
        lead_data['verified_business'] = True
        lead_data['enrichment_source'] = "Google Places (Mock)"
        
        return lead_data
