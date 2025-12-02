"""
ML-powered recommendation engine.

This module provides:
- Content-based filtering to find similar leads
- Trending niche detection based on recent activity
- Personalized recommendations (placeholder for future collaborative filtering)
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from database import Lead
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from logger import logger

class Recommender:
    """
    Recommendation engine for leads and niches.
    """
    
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def get_similar_leads(self, lead_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find leads similar to the given lead ID using content-based filtering.
        Uses TF-IDF on combined text features (company, niche, role, location).
        """
        if not self.db_session:
            logger.warning("No DB session provided for recommendations")
            return []

        # Fetch target lead
        target_lead = self.db_session.query(Lead).filter(Lead.id == lead_id).first()
        if not target_lead:
            return []

        # Fetch candidate leads (same niche or all leads if few)
        # Optimization: Limit to last 1000 leads to keep it fast
        candidates = self.db_session.query(Lead).filter(
            Lead.id != lead_id
        ).order_by(Lead.date_added.desc()).limit(1000).all()

        if not candidates:
            return []

        # Prepare data for TF-IDF
        all_leads = [target_lead] + candidates
        corpus = [self._create_soup(lead) for lead in all_leads]

        try:
            # Calculate similarity matrix
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            
            # Get top indices
            sim_scores = list(enumerate(cosine_sim[0]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[:limit]
            
            # Retrieve similar leads
            similar_leads = []
            for i, score in sim_scores:
                lead = candidates[i]
                lead_dict = lead.to_dict()
                lead_dict['similarity_score'] = float(score)
                similar_leads.append(lead_dict)
                
            return similar_leads
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return []

    def get_trending_niches(self, days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Identify trending niches based on recent lead volume.
        """
        if not self.db_session:
            return []

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query for count of leads per niche in the last N days
        results = self.db_session.query(
            Lead.niche, func.count(Lead.id).label('count')
        ).filter(
            Lead.date_added >= cutoff_date
        ).group_by(
            Lead.niche
        ).order_by(
            desc('count')
        ).limit(limit).all()

        trending = [
            {'niche': niche, 'count': count, 'trend': 'up'} 
            for niche, count in results
        ]
        
        return trending

    def get_recommended_leads(self, user_id: int = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations.
        For Phase 1, this returns high-scoring leads from trending niches.
        """
        if not self.db_session:
            return []

        # 1. Get trending niches first
        trending = self.get_trending_niches(limit=3)
        trending_niches = [t['niche'] for t in trending]
        
        query = self.db_session.query(Lead).filter(
            Lead.lead_score >= 70  # Only high quality
        )
        
        if trending_niches:
            query = query.filter(Lead.niche.in_(trending_niches))
            
        recommendations = query.order_by(
            Lead.lead_score.desc(), 
            Lead.date_added.desc()
        ).limit(limit).all()
        
        return [lead.to_dict() for lead in recommendations]

    def _create_soup(self, lead: Lead) -> str:
        """Combine lead features into a single string for vectorization."""
        features = [
            str(lead.niche or ''),
            str(lead.company or ''),
            str(lead.role or ''),
            str(lead.location or ''),
            str(lead.source or '')
        ]
        return ' '.join(features).lower()

# Singleton helper (though session needs to be passed per request usually)
def get_recommender(db_session: Session) -> Recommender:
    return Recommender(db_session)
