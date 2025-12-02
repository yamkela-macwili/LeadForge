"""
ML-powered lead scoring system.

This module provides intelligent lead quality scoring based on multiple features:
- Contact completeness (phone, email, social profiles)
- Business presence (website, reviews, ratings)
- Data freshness and verification status
- Engagement indicators

Scores range from 0-100, with higher scores indicating higher quality leads.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re


class LeadScorer:
    """
    Machine learning-based lead scoring system.
    
    Currently uses a rule-based scoring system that can be easily
    replaced with a trained ML model in the future.
    """
    
    def __init__(self):
        """Initialize the lead scorer with feature weights."""
        self.feature_weights = {
            'contact_completeness': 0.30,  # Has phone + email + social
            'business_presence': 0.25,      # Website, reviews, ratings
            'data_freshness': 0.20,         # How recent the data is
            'verification_status': 0.15,    # Verified vs unverified
            'engagement_signals': 0.10      # Activity indicators
        }
    
    def score_lead(self, lead_data: Dict) -> Dict[str, any]:
        """
        Score a single lead and return score with feature breakdown.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dictionary with 'score' (0-100) and 'features' breakdown
        """
        features = self._extract_features(lead_data)
        score = self._calculate_score(features)
        
        return {
            'score': round(score, 2),
            'features': features,
            'score_date': datetime.utcnow().isoformat()
        }
    
    def score_leads_batch(self, leads_data: List[Dict]) -> List[Dict]:
        """
        Score multiple leads efficiently.
        
        Args:
            leads_data: List of lead dictionaries
            
        Returns:
            List of scoring results
        """
        return [self.score_lead(lead) for lead in leads_data]
    
    def _extract_features(self, lead_data: Dict) -> Dict[str, float]:
        """Extract and normalize features from lead data."""
        features = {}
        
        # Contact Completeness (0-100)
        features['contact_completeness'] = self._score_contact_completeness(lead_data)
        
        # Business Presence (0-100)
        features['business_presence'] = self._score_business_presence(lead_data)
        
        # Data Freshness (0-100)
        features['data_freshness'] = self._score_data_freshness(lead_data)
        
        # Verification Status (0-100)
        features['verification_status'] = self._score_verification(lead_data)
        
        # Engagement Signals (0-100)
        features['engagement_signals'] = self._score_engagement(lead_data)
        
        return features
    
    def _calculate_score(self, features: Dict[str, float]) -> float:
        """Calculate weighted score from features."""
        total_score = 0.0
        
        for feature_name, feature_value in features.items():
            weight = self.feature_weights.get(feature_name, 0.0)
            total_score += feature_value * weight
        
        return min(100.0, max(0.0, total_score))
    
    def _score_contact_completeness(self, lead_data: Dict) -> float:
        """Score based on available contact information."""
        score = 0.0
        max_score = 100.0
        
        # Phone number (40 points)
        if lead_data.get('phone'):
            phone = str(lead_data['phone'])
            if self._is_valid_phone(phone):
                score += 40.0
            else:
                score += 20.0  # Has phone but might be invalid
        
        # Email (40 points)
        if lead_data.get('email'):
            email = str(lead_data['email'])
            if self._is_valid_email(email):
                score += 40.0
            else:
                score += 20.0  # Has email but might be invalid
        
        # Social media (10 points)
        if lead_data.get('social_media_url'):
            score += 10.0
        
        # Website (10 points)
        if lead_data.get('website'):
            score += 10.0
        
        return min(max_score, score)
    
    def _score_business_presence(self, lead_data: Dict) -> float:
        """Score based on business online presence."""
        score = 0.0
        max_score = 100.0
        
        # Has company name (20 points)
        if lead_data.get('company'):
            score += 20.0
        
        # Has address/location (20 points)
        if lead_data.get('address') or lead_data.get('location'):
            score += 20.0
        
        # Has rating (30 points, scaled by rating value)
        if lead_data.get('rating'):
            try:
                rating = float(lead_data['rating'])
                # Assume rating is 0-5 scale
                score += (rating / 5.0) * 30.0
            except (ValueError, TypeError):
                pass
        
        # Has reviews (15 points)
        if lead_data.get('reviews'):
            try:
                review_count = int(lead_data['reviews'])
                # More reviews = better, capped at 15 points
                score += min(15.0, review_count / 10.0)
            except (ValueError, TypeError):
                pass
        
        # Has description/bio (15 points)
        if lead_data.get('description') or lead_data.get('bio'):
            score += 15.0
        
        return min(max_score, score)
    
    def _score_data_freshness(self, lead_data: Dict) -> float:
        """Score based on how recent the data is."""
        score = 100.0  # Start with max score
        
        date_added = lead_data.get('date_added')
        if not date_added:
            return 50.0  # Unknown date = medium score
        
        try:
            if isinstance(date_added, str):
                date_added = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
            
            days_old = (datetime.utcnow() - date_added).days
            
            # Decay score based on age
            if days_old <= 7:
                score = 100.0  # Fresh data (< 1 week)
            elif days_old <= 30:
                score = 80.0   # Recent data (< 1 month)
            elif days_old <= 90:
                score = 60.0   # Somewhat old (< 3 months)
            elif days_old <= 180:
                score = 40.0   # Old (< 6 months)
            else:
                score = 20.0   # Very old (> 6 months)
        
        except (ValueError, TypeError, AttributeError):
            score = 50.0  # Error parsing date = medium score
        
        return score
    
    def _score_verification(self, lead_data: Dict) -> float:
        """Score based on verification status."""
        score = 0.0
        
        # Verified status (100 points if verified)
        if lead_data.get('verified') or lead_data.get('is_verified'):
            score = 100.0
        else:
            # Partial credit for having verifiable information
            verifiable_fields = 0
            if lead_data.get('phone'):
                verifiable_fields += 1
            if lead_data.get('email'):
                verifiable_fields += 1
            if lead_data.get('website'):
                verifiable_fields += 1
            
            score = (verifiable_fields / 3.0) * 50.0  # Max 50 points if unverified
        
        return score
    
    def _score_engagement(self, lead_data: Dict) -> float:
        """Score based on engagement indicators."""
        score = 0.0
        max_score = 100.0
        
        # Has recent activity (50 points)
        last_activity = lead_data.get('last_activity')
        if last_activity:
            try:
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                
                days_since_activity = (datetime.utcnow() - last_activity).days
                
                if days_since_activity <= 7:
                    score += 50.0
                elif days_since_activity <= 30:
                    score += 30.0
                elif days_since_activity <= 90:
                    score += 15.0
            except (ValueError, TypeError, AttributeError):
                pass
        
        # Active on social media (25 points)
        if lead_data.get('social_media_active'):
            score += 25.0
        
        # Responsive to contact (25 points)
        if lead_data.get('response_rate'):
            try:
                response_rate = float(lead_data['response_rate'])
                score += response_rate * 25.0
            except (ValueError, TypeError):
                pass
        
        return min(max_score, score)
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check if it's a reasonable length (7-15 digits)
        return len(cleaned) >= 7 and len(cleaned) <= 15 and cleaned.isdigit()
    
    def get_score_interpretation(self, score: float) -> str:
        """Get human-readable interpretation of score."""
        if score >= 80:
            return "Excellent - High quality lead"
        elif score >= 60:
            return "Good - Quality lead worth pursuing"
        elif score >= 40:
            return "Fair - Moderate quality, needs verification"
        elif score >= 20:
            return "Poor - Low quality, missing information"
        else:
            return "Very Poor - Insufficient data"


# Singleton instance
_scorer_instance = None

def get_lead_scorer() -> LeadScorer:
    """Get the global lead scorer instance."""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = LeadScorer()
    return _scorer_instance
