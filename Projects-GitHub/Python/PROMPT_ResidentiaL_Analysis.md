# REAL PROPERTY MARKET ANALYSIS
# Implementation Guide and Requirements

## VERSION INFORMATION
**Current Version:** 2.3.1  
**Release Date:** October 31, 2025  
**Last Updated:** November 5, 2025  
**Status:** Production / Implementation Ready

### Version History
- **2.3.1** (Oct 31, 2025): Time adjustment formula correction
- **2.3.0** (Oct 31, 2025): Added comparable sales adjustments
- **2.2.0** (Base): Data coverage validation

### Key Dependencies
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import folium
import contextily as ctx
from geopy.geocoders import Nominatim
from openpyxl import Workbook
from reportlab.pdfgen import canvas
```

## IMPLEMENTATION NOTES

### Critical Formulas and Calculations

1. **Data Coverage Calculation**
```python
def calculate_data_coverage(sales_df, date_of_value):
    """
    Calculate actual data coverage in months
    
    Parameters:
    sales_df: DataFrame with 'sale_date' column
    date_of_value: datetime object for analysis date
    
    Returns:
    float: Actual coverage in months
    """
    earliest_sale = sales_df['sale_date'].min()
    coverage_days = (date_of_value - earliest_sale).days
    coverage_months = coverage_days / 30.44  # Average month length
    return coverage_months
```

2. **Time Adjustment Formula** ⚠️
```python
def calculate_time_adjustment(sale_price, sale_date, date_of_value, monthly_trend_pct):
    """
    Calculate time adjustment with 30-day threshold
    
    Parameters:
    sale_price: float - Original sale price
    sale_date: datetime - Date of sale
    date_of_value: datetime - Analysis date
    monthly_trend_pct: float - Market trend percentage per month
    
    Returns:
    float: Adjustment amount
    str: Explanation note
    """
    days_diff = (date_of_value - sale_date).days  # CRITICAL: This order for correct sign
    
    if abs(days_diff) <= 30:
        return 0, "Within 30-day threshold"
    
    # Convert monthly percentage to daily factor
    daily_factor = monthly_trend_pct / 100 / 30.44
    
    # Calculate adjustment
    adjustment = sale_price * daily_factor * days_diff
    note = f"{abs(days_diff)} days at {monthly_trend_pct:+.1f}%/month"
    
    return adjustment, note
```

3. **Living Area Adjustment Formula**
```python
def calculate_sf_adjustment(subject_sf, comp_sf, marginal_value):
    """
    Calculate size adjustment with 5% threshold
    
    Parameters:
    subject_sf: float - Subject property living area
    comp_sf: float - Comparable property living area
    marginal_value: float - Value per SF from regression
    
    Returns:
    float: Adjustment amount
    str: Explanation note
    """
    sf_diff = subject_sf - comp_sf
    pct_diff = abs(sf_diff) / subject_sf
    
    if pct_diff <= 0.05:  # 5% threshold
        return 0, f"Within 5% threshold ({pct_diff:.1%})"
    
    adjustment = marginal_value * sf_diff
    note = f"{sf_diff:+.0f} SF ({pct_diff:.1%})"
    
    return adjustment, note
```

### Chart Generation Requirements

1. **Price Trend Chart Function**
```python
def create_price_trend_chart(df, y_column, title, start_date, end_date):
    """
    Create standardized price trend chart
    
    Parameters:
    df: DataFrame with sale data
    y_column: Column name for Y-axis (price or price/sf)
    title: Chart title
    start_date, end_date: Date range for X-axis
    """
    plt.figure(figsize=(12, 8))
    
    # Scatter plot of actual sales
    plt.scatter(df['sale_date'], df[y_column], color='blue', alpha=0.5, 
               label='Sales', zorder=5)
    
    # Linear regression
    X = (df['sale_date'] - df['sale_date'].min()).dt.days
    y = df[y_column]
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
    
    # Calculate trend lines
    x_line = pd.date_range(start_date, end_date)
    x_nums = (x_line - df['sale_date'].min()).days
    y_line = slope * x_nums + intercept
    
    # Add trend line
    plt.plot(x_line, y_line, 'k-', linewidth=2, 
            label=f'Trend: {slope:.2f}/day ({slope*30.44:.1%}/month)')
    
    # Formatting
    plt.grid(True, alpha=0.3)
    plt.title(title, pad=20)
    plt.xlabel('Sale Date')
    plt.ylabel('Price ($)' if 'price' in y_column.lower() else 'Price/SF ($)')
    
    # Rotate X-axis labels
    plt.xticks(rotation=45)
    
    # Format Y-axis with dollar signs
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Ensure Y-axis starts at 0
    plt.ylim(bottom=0)
    
    # Add padding above highest point
    ymax = df[y_column].max()
    plt.ylim(top=ymax * 1.2)  # 20% padding
    
    plt.tight_layout()
    return plt.gcf()
```

[Additional improvements continue in subsequent sections...]