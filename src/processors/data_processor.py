import pandas as pd
import re

class DataProcessor:
    def __init__(self, data):
        self.df = pd.DataFrame(data)

    def clean_data(self):
        """
        Cleans and validates the data.
        """
        if self.df.empty:
            return self.df

        # Remove duplicates based on phone or email
        self.df.drop_duplicates(subset=['phone'], keep='first', inplace=True)
        self.df.drop_duplicates(subset=['email'], keep='first', inplace=True)

        # Basic validation (e.g., ensure phone number has digits)
        self.df = self.df[self.df['phone'].apply(self._is_valid_phone)]
        
        return self.df

    def _is_valid_phone(self, phone):
        """
        Simple check if phone contains at least 10 digits.
        """
        digits = re.sub(r'\D', '', str(phone))
        return len(digits) >= 10

    def score_leads(self):
        """
        Adds a score column to the dataframe based on multiple factors.
        """
        if self.df.empty:
            return self.df
            
        # Base score
        self.df['score'] = 0
        
        # Factor 1: Contact Info Completeness (Max 50)
        if 'phone' in self.df.columns:
             self.df.loc[self.df['phone'].apply(self._is_valid_phone), 'score'] += 30
        if 'email' in self.df.columns:
            self.df.loc[self.df['email'].notna(), 'score'] += 20
            
        # Factor 2: Activity/Quality Indicators (Max 50)
        if 'listings_count' in self.df.columns:
             # Real Estate specific
             self.df.loc[self.df['listings_count'] > 20, 'score'] += 25
             self.df.loc[self.df['listings_count'] > 10, 'score'] += 10
             
        if 'hourly_rate' in self.df.columns:
            # Tutor specific - higher rate might imply more experience/serious pro
            self.df.loc[self.df['hourly_rate'] > 250, 'score'] += 25
            
        if 'rating' in self.df.columns:
            # Service Provider specific
            self.df.loc[self.df['rating'] >= 4.5, 'score'] += 25
            self.df.loc[self.df['reviews_count'] > 20, 'score'] += 25

        return self.df
