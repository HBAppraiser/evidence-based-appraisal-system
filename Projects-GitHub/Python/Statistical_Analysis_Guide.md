# REAL PROPERTY MARKET ANALYSIS
# Statistical Analysis and Report Generation Guide

## STATISTICAL ANALYSIS FUNCTIONS

### Market Trend Analysis
```python
def analyze_market_trend(df, period_months, date_of_value):
    """
    Analyze market trend and determine direction
    
    Parameters:
    df: DataFrame with sales data
    period_months: Analysis period in months
    date_of_value: Analysis date
    
    Returns:
    dict: Trend analysis results
    """
    start_date = date_of_value - pd.Timedelta(days=period_months * 30.44)
    period_sales = df[df['sale_date'].between(start_date, date_of_value)]
    
    # Convert dates to numeric for regression
    days_from_start = (period_sales['sale_date'] - start_date).dt.days
    
    # Price trend
    price_slope, price_intercept, r_value, _, _ = stats.linregress(
        days_from_start, period_sales['sale_price'])
    
    # Price per SF trend
    price_sf = period_sales['sale_price'] / period_sales['living_area']
    sf_slope, sf_intercept, sf_r_value, _, _ = stats.linregress(
        days_from_start, price_sf)
    
    # Calculate monthly percentages
    avg_price = period_sales['sale_price'].mean()
    monthly_price_pct = (price_slope * 30.44 / avg_price) * 100
    
    avg_sf_price = price_sf.mean()
    monthly_sf_pct = (sf_slope * 30.44 / avg_sf_price) * 100
    
    # Determine trend direction
    def get_trend(slope_per_day, r_squared):
        if r_squared < 0.3:
            return "Unstable"
        if abs(slope_per_day) < 0.5:
            return "Stable"
        return "Increasing" if slope_per_day > 0 else "Decreasing"
    
    return {
        'price_trend': {
            'slope_per_day': price_slope,
            'monthly_pct': monthly_price_pct,
            'r_squared': r_value ** 2,
            'direction': get_trend(price_slope, r_value ** 2)
        },
        'price_sf_trend': {
            'slope_per_day': sf_slope,
            'monthly_pct': monthly_sf_pct,
            'r_squared': sf_r_value ** 2,
            'direction': get_trend(sf_slope, sf_r_value ** 2)
        }
    }
```

### Comparable Sales Analysis
```python
def analyze_comparable_sales(subject_sf, sales_df, date_of_value, 
                           monthly_trend_pct):
    """
    Analyze and adjust comparable sales
    
    Parameters:
    subject_sf: Subject property living area
    sales_df: DataFrame with comparable sales
    date_of_value: Analysis date
    monthly_trend_pct: Market trend percentage per month
    
    Returns:
    DataFrame: Adjusted comparables with analysis
    """
    # Calculate marginal value per SF (regression)
    X = sales_df['living_area']
    y = sales_df['sale_price']
    slope, intercept, r_value, _, _ = stats.linregress(X, y)
    marginal_value_per_sf = slope
    
    results = []
    
    for _, sale in sales_df.iterrows():
        # Time adjustment
        time_adj, time_note = calculate_time_adjustment(
            sale['sale_price'],
            sale['sale_date'],
            date_of_value,
            monthly_trend_pct
        )
        
        # Living area adjustment
        sf_adj, sf_note = calculate_sf_adjustment(
            subject_sf,
            sale['living_area'],
            marginal_value_per_sf
        )
        
        # Net adjustment
        net_adj = time_adj + sf_adj
        adjusted_price = sale['sale_price'] + net_adj
        
        results.append({
            'address': sale['address'],
            'sale_date': sale['sale_date'],
            'living_area': sale['living_area'],
            'sale_price': sale['sale_price'],
            'time_adj': time_adj,
            'time_note': time_note,
            'sf_adj': sf_adj,
            'sf_note': sf_note,
            'net_adj': net_adj,
            'adjusted_price': adjusted_price,
            'net_adj_pct': (net_adj / sale['sale_price']) * 100
        })
    
    return pd.DataFrame(results)
```

### Data Coverage Validation
```python
def validate_data_coverage(df, date_of_value, analysis_periods):
    """
    Validate data coverage for analysis periods
    
    Parameters:
    df: DataFrame with sales data
    date_of_value: Analysis date
    analysis_periods: List of period lengths in months
    
    Returns:
    dict: Valid periods and coverage info
    """
    # Calculate actual coverage
    earliest_sale = df['sale_date'].min()
    coverage_days = (date_of_value - earliest_sale).days
    actual_coverage_months = coverage_days / 30.44
    
    valid_periods = []
    messages = []
    
    # Previous period sales count for comparison
    prev_count = 0
    
    for months in sorted(analysis_periods):
        # Get sales for this period
        start_date = date_of_value - pd.Timedelta(days=months * 30.44)
        period_sales = df[df['sale_date'].between(start_date, date_of_value)]
        sales_count = len(period_sales)
        
        # Apply validation rules
        if months > actual_coverage_months + 1:
            messages.append(
                f"{months}-month period extends beyond data coverage "
                f"({actual_coverage_months:.1f} months)")
            continue
            
        if sales_count == prev_count and prev_count > 0:
            messages.append(
                f"{months}-month period duplicate of shorter period "
                f"(same {sales_count} sales)")
            continue
            
        if sales_count < 3:
            messages.append(
                f"⚠ WARNING: {months}-month period has insufficient data "
                f"(n={sales_count})")
        
        valid_periods.append({
            'months': months,
            'sales_count': sales_count,
            'start_date': start_date,
            'end_date': date_of_value
        })
        
        prev_count = sales_count
    
    return {
        'actual_coverage_months': actual_coverage_months,
        'earliest_sale': earliest_sale,
        'valid_periods': valid_periods,
        'messages': messages
    }
```

### Statistical Reporting
```python
def generate_statistics_summary(df, valid_periods, date_of_value):
    """
    Generate comprehensive statistics for valid periods
    
    Parameters:
    df: DataFrame with sales data
    valid_periods: List of valid analysis periods
    date_of_value: Analysis date
    
    Returns:
    dict: Statistics for all valid periods
    """
    summary = {}
    
    for period in valid_periods:
        months = period['months']
        start_date = period['start_date']
        
        # Get sales for period
        period_sales = df[df['sale_date'].between(start_date, date_of_value)]
        
        # Calculate price per SF
        price_sf = period_sales['sale_price'] / period_sales['living_area']
        
        # Basic statistics
        stats = {
            'count': len(period_sales),
            'months': months,
            'absorption_rate': len(period_sales) / months,
            'price': {
                'min': period_sales['sale_price'].min(),
                'max': period_sales['sale_price'].max(),
                'mean': period_sales['sale_price'].mean(),
                'median': period_sales['sale_price'].median(),
                'std': period_sales['sale_price'].std()
            },
            'price_sf': {
                'min': price_sf.min(),
                'max': price_sf.max(),
                'mean': price_sf.mean(),
                'median': price_sf.median(),
                'std': price_sf.std()
            },
            'dom': {
                'mean': period_sales['dom'].mean(),
                'median': period_sales['dom'].median(),
                'std': period_sales['dom'].std()
            }
        }
        
        # Add trend analysis
        stats['trend'] = analyze_market_trend(
            period_sales, months, date_of_value)
        
        summary[f'{months}mo'] = stats
    
    return summary
```

## REPORT GENERATION

### Excel Report Generation
```python
def create_excel_report(stats_summary, comp_analysis, coverage_info, 
                       file_path):
    """
    Generate comprehensive Excel report
    
    Parameters:
    stats_summary: Dictionary of period statistics
    comp_analysis: DataFrame of comparable analysis
    coverage_info: Data coverage validation results
    file_path: Output Excel file path
    """
    wb = Workbook()
    
    # Data Coverage sheet
    ws_coverage = wb.active
    ws_coverage.title = "Data Coverage Analysis"
    
    ws_coverage['A1'] = "DATA COVERAGE ANALYSIS"
    ws_coverage['A3'] = "Actual Coverage Months:"
    ws_coverage['B3'] = coverage_info['actual_coverage_months']
    ws_coverage['A4'] = "Earliest Sale Date:"
    ws_coverage['B4'] = coverage_info['earliest_sale']
    
    row = 6
    ws_coverage['A6'] = "VALIDATION MESSAGES"
    for msg in coverage_info['messages']:
        row += 1
        ws_coverage[f'A{row}'] = msg
    
    # Statistics Summary sheet
    ws_stats = wb.create_sheet("Statistics Summary")
    # [Add statistics formatting here]
    
    # Comparable Analysis sheet
    ws_comps = wb.create_sheet("Comp Sales Adjustments")
    # [Add comparables formatting here]
    
    # Save workbook
    wb.save(file_path)
```

### PDF Report Generation
```python
def create_pdf_report(stats_summary, comp_analysis, coverage_info, 
                     file_path):
    """
    Generate professional PDF report
    
    Parameters:
    stats_summary: Dictionary of period statistics
    comp_analysis: DataFrame of comparable analysis
    coverage_info: Data coverage validation results
    file_path: Output PDF file path
    """
    # Initialize PDF
    c = canvas.Canvas(file_path)
    
    # Add page 1 - Market Analysis
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "MARKET TREND ANALYSIS")
    
    # Add coverage statement
    c.setFont("Helvetica", 10)
    coverage_text = (
        f"DATA COVERAGE: Analysis includes sales from "
        f"{coverage_info['earliest_sale'].strftime('%m/%d/%Y')} through "
        f"the date of value, providing "
        f"{coverage_info['actual_coverage_months']:.1f} months of "
        f"historical data."
    )
    c.drawString(72, 720, coverage_text)
    
    # Add statistics table
    # [Add table formatting here]
    
    # Add subsequent pages
    # [Add chart pages, comp analysis, etc.]
    
    c.save()
```

[Additional implementation details continue...]