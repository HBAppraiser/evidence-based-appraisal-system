# REAL PROPERTY MARKET ANALYSIS
# Data Structures and Validation Guide

## DATA STRUCTURES

### Required DataFrame Columns
```python
REQUIRED_COLUMNS = {
    'sale_date': 'datetime64[ns]',
    'sale_price': 'float64',
    'address': 'str',
    'zip_code': 'str',
    'property_type': 'str',
    'living_area': 'float64',
    'lot_size': 'float64',
    'year_built': 'int64',
    'beds': 'int64',
    'baths': 'float64',
    'latitude': 'float64',
    'longitude': 'float64'
}

OPTIONAL_COLUMNS = {
    'dom': 'int64',
    'cdom': 'int64',
    'condition': 'str',
    'garage_spaces': 'float64',
    'pool': 'bool',
    'view': 'bool',
    'waterfront': 'bool'
}
```

### Data Validation Functions

```python
def validate_data_structure(df):
    """
    Validate DataFrame structure and data types
    
    Parameters:
    df: DataFrame to validate
    
    Returns:
    bool: Valid status
    list: Validation messages
    """
    messages = []
    valid = True
    
    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        valid = False
        messages.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Check data types
    for col, dtype in REQUIRED_COLUMNS.items():
        if col in df.columns and str(df[col].dtype) != dtype:
            try:
                df[col] = df[col].astype(dtype)
                messages.append(f"Converted {col} to {dtype}")
            except:
                valid = False
                messages.append(f"Cannot convert {col} to {dtype}")
    
    return valid, messages
```

### Professional Thresholds

```python
class AnalysisThresholds:
    """Constants for professional analysis thresholds"""
    
    # Time adjustment threshold
    TIME_THRESHOLD_DAYS = 30
    
    # Living area threshold (5%)
    SF_THRESHOLD_PCT = 0.05
    
    # Minimum sample sizes
    MIN_SALES = {
        '0-3mo': 3,
        '0-6mo': 5,
        '0-12mo': 10,
        '0-24mo': 20,
        'regression': 30
    }
    
    # Missing data thresholds
    MISSING_DATA = {
        'ignore': 0.05,  # 5%
        'warning': 0.20  # 20%
    }
    
    # Outlier thresholds
    PRICE_RANGE_PCT = {
        'min': 0.50,  # 50% of median
        'max': 2.00   # 200% of median
    }
    
    # DOM threshold
    MAX_DOM = 365  # days
```

### Statistical Analysis Functions

```python
def calculate_market_statistics(df, period_months, date_of_value):
    """
    Calculate comprehensive market statistics for a time period
    
    Parameters:
    df: DataFrame with sale data
    period_months: Number of months to analyze
    date_of_value: Analysis date
    
    Returns:
    dict: Statistics for the period
    """
    start_date = date_of_value - pd.Timedelta(days=period_months * 30.44)
    period_sales = df[df['sale_date'].between(start_date, date_of_value)]
    
    if len(period_sales) < AnalysisThresholds.MIN_SALES['0-3mo']:
        return {'error': 'Insufficient data'}
    
    stats = {
        'period_months': period_months,
        'sales_count': len(period_sales),
        'price': {
            'mean': period_sales['sale_price'].mean(),
            'median': period_sales['sale_price'].median(),
            'std': period_sales['sale_price'].std()
        },
        'price_sf': {
            'mean': (period_sales['sale_price'] / 
                    period_sales['living_area']).mean(),
            'median': (period_sales['sale_price'] / 
                      period_sales['living_area']).median(),
            'std': (period_sales['sale_price'] / 
                   period_sales['living_area']).std()
        },
        'dom': {
            'mean': period_sales['dom'].mean(),
            'median': period_sales['dom'].median()
        },
        'monthly_absorption': len(period_sales) / period_months
    }
    
    return stats
```

[Additional improvements continue in subsequent sections...]