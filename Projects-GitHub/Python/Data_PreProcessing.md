# DATA PREPROCESSING AND VALIDATION MODULE

## Input Data Validation

```python
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class DataPreprocessor:
    """Data preprocessing and validation class"""
    
    def __init__(self, date_of_value: datetime):
        self.date_of_value = date_of_value
        self.geolocator = Nominatim(user_agent="market_analysis")
        
    def validate_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check for required columns"""
        REQUIRED_COLUMNS = [
            'sale_date', 'sale_price', 'address', 'living_area',
            'property_type', 'year_built', 'beds', 'baths'
        ]
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        return missing
    
    def clean_sale_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate sale prices"""
        df = df.copy()
        
        # Remove non-numeric characters
        df['sale_price'] = df['sale_price'].replace('[\$,]', '', regex=True)
        df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
        
        # Flag outliers (outside 1.5 * IQR)
        Q1 = df['sale_price'].quantile(0.25)
        Q3 = df['sale_price'].quantile(0.75)
        IQR = Q3 - Q1
        df['price_outlier'] = (
            (df['sale_price'] < (Q1 - 1.5 * IQR)) | 
            (df['sale_price'] > (Q3 + 1.5 * IQR))
        )
        
        return df
    
    def clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate dates"""
        df = df.copy()
        
        # Convert to datetime
        df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
        
        # Remove future dates
        df['invalid_date'] = df['sale_date'] > self.date_of_value
        
        # Calculate days from date of value
        df['days_from_dov'] = (
            self.date_of_value - df['sale_date']).dt.days
        
        return df
    
    def clean_living_area(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate living areas"""
        df = df.copy()
        
        # Convert to numeric
        df['living_area'] = pd.to_numeric(
            df['living_area'], errors='coerce')
        
        # Flag unreasonable values
        df['sf_outlier'] = (
            (df['living_area'] < 300) | 
            (df['living_area'] > 10000)
        )
        
        return df
    
    def geocode_addresses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lat/lon for addresses missing coordinates"""
        df = df.copy()
        
        # Only process rows missing coordinates
        missing_coords = (
            df['latitude'].isna() | 
            df['longitude'].isna()
        )
        
        for idx, row in df[missing_coords].iterrows():
            try:
                location = self.geolocator.geocode(row['address'])
                if location:
                    df.at[idx, 'latitude'] = location.latitude
                    df.at[idx, 'longitude'] = location.longitude
            except GeocoderTimedOut:
                continue
        
        return df
    
    def process_dataset(self, df: pd.DataFrame) -> Dict:
        """Complete data preprocessing pipeline"""
        results = {
            'data': df.copy(),
            'warnings': [],
            'errors': []
        }
        
        # Check required columns
        missing_cols = self.validate_required_columns(results['data'])
        if missing_cols:
            results['errors'].append(
                f"Missing required columns: {', '.join(missing_cols)}")
            return results
        
        # Clean sale prices
        results['data'] = self.clean_sale_prices(results['data'])
        price_outliers = results['data']['price_outlier'].sum()
        if price_outliers:
            results['warnings'].append(
                f"Found {price_outliers} price outliers")
        
        # Clean dates
        results['data'] = self.clean_dates(results['data'])
        invalid_dates = results['data']['invalid_date'].sum()
        if invalid_dates:
            results['warnings'].append(
                f"Found {invalid_dates} invalid dates")
        
        # Clean living areas
        results['data'] = self.clean_living_area(results['data'])
        sf_outliers = results['data']['sf_outlier'].sum()
        if sf_outliers:
            results['warnings'].append(
                f"Found {sf_outliers} living area outliers")
        
        # Add geocoding if needed
        if 'latitude' not in results['data'].columns:
            results['data']['latitude'] = np.nan
        if 'longitude' not in results['data'].columns:
            results['data']['longitude'] = np.nan
        
        results['data'] = self.geocode_addresses(results['data'])
        missing_coords = (
            results['data']['latitude'].isna() | 
            results['data']['longitude'].isna()
        ).sum()
        if missing_coords:
            results['warnings'].append(
                f"Could not geocode {missing_coords} addresses")
        
        return results
```