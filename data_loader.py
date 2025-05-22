"""
Data loader module for FinanceGPT
Handles CSV loading, validation, and preprocessing of spending data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpendingDataLoader:
    """Handles loading and validation of spending data from CSV files."""
    
    def __init__(self):
        self.required_columns = ['date', 'category', 'amount']
        self.optional_columns = ['notes', 'description']
        
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load spending data from CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Cleaned and validated spending data
        """
        try:
            # Try different encodings and separators
            df = self._try_load_csv(file_path)
            
            # Validate and clean the data
            df = self._validate_and_clean(df)
            
            logger.info(f"Successfully loaded {len(df)} spending records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            raise
            
    def _try_load_csv(self, file_path: str) -> pd.DataFrame:
        """Try different CSV loading strategies."""
        try:
            # First try with default settings
            return pd.read_csv(file_path)
        except:
            try:
                # Try with semicolon separator
                return pd.read_csv(file_path, sep=';')
            except:
                # Try with tab separator
                return pd.read_csv(file_path, sep='\t')
                
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean the loaded data."""
        original_len = len(df)
        
        # Check for required columns
        self._check_required_columns(df)
        
        # Clean column names (remove extra spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert amount to float
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Clean category names
        df['category'] = df['category'].astype(str).str.strip().str.title()
        
        # Remove rows with invalid data
        df = df.dropna(subset=['date', 'amount', 'category'])
        
        # Remove negative amounts (assuming expenses are positive)
        df = df[df['amount'] > 0]
        
        # Add time-based features
        df = self._add_time_features(df)
        
        logger.info(f"Cleaned data: {original_len} -> {len(df)} records")
        
        return df.reset_index(drop=True)
        
    def _check_required_columns(self, df: pd.DataFrame):
        """Check if all required columns are present."""
        missing_cols = []
        df_cols_lower = [col.lower().strip() for col in df.columns]
        
        for req_col in self.required_columns:
            if req_col.lower() not in df_cols_lower:
                missing_cols.append(req_col)
                
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features for analysis."""
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['weekday'] = df['date'].dt.day_name()
        df['week_number'] = df['date'].dt.isocalendar().week
        df['is_weekend'] = df['date'].dt.weekday >= 5
        df['month_name'] = df['date'].dt.month_name()
        
        return df
        
    def create_sample_data(self, output_path: str = "sample_spending.csv", num_records: int = 200):
        """Create a sample spending CSV file for testing."""
        
        # Sample categories and their typical spending ranges
        categories = {
            'Groceries': (20, 150),
            'Dining': (15, 80),
            'Transport': (5, 50),
            'Entertainment': (10, 100),
            'Shopping': (25, 200),
            'Utilities': (50, 300),
            'Healthcare': (20, 200),
            'Gas': (30, 80),
            'Coffee': (3, 15)
        }
        
        # Generate random dates over the last 6 months
        start_date = datetime.now() - pd.DateOffset(months=6)
        end_date = datetime.now()
        
        records = []
        
        for _ in range(num_records):
            # Random date
            random_date = start_date + (end_date - start_date) * np.random.random()
            
            # Random category
            category = np.random.choice(list(categories.keys()))
            min_amount, max_amount = categories[category]
            
            # Random amount with some weekend bias for certain categories
            amount = np.random.uniform(min_amount, max_amount)
            
            # Weekend spending tends to be higher for dining and entertainment
            if random_date.weekday() >= 5 and category in ['Dining', 'Entertainment']:
                amount *= 1.3
                
            # Add some notes occasionally
            notes = ""
            if np.random.random() < 0.3:  # 30% chance of having notes
                notes_options = [
                    "Regular purchase", "Special occasion", "Bulk buy", 
                    "Emergency", "Planned expense", "Impulse buy"
                ]
                notes = np.random.choice(notes_options)
                
            records.append({
                'date': random_date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': round(amount, 2),
                'notes': notes
            })
            
        # Create DataFrame and save to CSV
        sample_df = pd.DataFrame(records)
        sample_df = sample_df.sort_values('date').reset_index(drop=True)
        sample_df.to_csv(output_path, index=False)
        
        logger.info(f"Created sample data with {len(sample_df)} records: {output_path}")
        return output_path

def load_spending_data(file_path: str) -> pd.DataFrame:
    """Convenience function to load spending data."""
    loader = SpendingDataLoader()
    return loader.load_csv(file_path)

def create_sample_data(output_path: str = "sample_spending.csv") -> str:
    """Convenience function to create sample data."""
    loader = SpendingDataLoader()
    return loader.create_sample_data(output_path) 