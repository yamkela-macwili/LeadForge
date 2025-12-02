"""
Test script for ML lead scoring system.
"""

import sys
sys.path.insert(0, 'src')

from ml.lead_scorer import get_lead_scorer
from datetime import datetime, timedelta

def test_lead_scorer():
    """Test the lead scoring functionality."""
    print("=" * 60)
    print("Testing ML Lead Scoring System")
    print("=" * 60)
    
    scorer = get_lead_scorer()
    
    # Test Case 1: High quality lead
    print("\n1. Testing HIGH QUALITY lead:")
    high_quality_lead = {
        'email': 'john.doe@example.com',
        'phone': '+27123456789',
        'first_name': 'John',
        'last_name': 'Doe',
        'company': 'ABC Real Estate',
        'website': 'https://abcrealestate.com',
        'rating': 4.8,
        'reviews': 150,
        'description': 'Top real estate agent in Johannesburg',
        'date_added': datetime.utcnow(),
        'verified': True,
        'social_media_url': 'https://linkedin.com/in/johndoe'
    }
    
    result = scorer.score_lead(high_quality_lead)
    print(f"   Score: {result['score']:.2f}/100")
    print(f"   Interpretation: {scorer.get_score_interpretation(result['score'])}")
    print(f"   Features:")
    for feature, value in result['features'].items():
        print(f"     - {feature}: {value:.2f}")
    
    # Test Case 2: Medium quality lead
    print("\n2. Testing MEDIUM QUALITY lead:")
    medium_quality_lead = {
        'email': 'jane@example.com',
        'phone': '0821234567',
        'first_name': 'Jane',
        'company': 'Tutoring Services',
        'rating': 3.5,
        'reviews': 20,
        'date_added': datetime.utcnow() - timedelta(days=45)
    }
    
    result = scorer.score_lead(medium_quality_lead)
    print(f"   Score: {result['score']:.2f}/100")
    print(f"   Interpretation: {scorer.get_score_interpretation(result['score'])}")
    print(f"   Features:")
    for feature, value in result['features'].items():
        print(f"     - {feature}: {value:.2f}")
    
    # Test Case 3: Low quality lead
    print("\n3. Testing LOW QUALITY lead:")
    low_quality_lead = {
        'phone': '123',  # Invalid phone
        'date_added': datetime.utcnow() - timedelta(days=200)
    }
    
    result = scorer.score_lead(low_quality_lead)
    print(f"   Score: {result['score']:.2f}/100")
    print(f"   Interpretation: {scorer.get_score_interpretation(result['score'])}")
    print(f"   Features:")
    for feature, value in result['features'].items():
        print(f"     - {feature}: {value:.2f}")
    
    # Test Case 4: Batch scoring
    print("\n4. Testing BATCH SCORING:")
    leads = [high_quality_lead, medium_quality_lead, low_quality_lead]
    batch_results = scorer.score_leads_batch(leads)
    
    print(f"   Scored {len(batch_results)} leads:")
    for i, result in enumerate(batch_results, 1):
        print(f"     Lead {i}: {result['score']:.2f}/100")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_lead_scorer()
