#!/usr/bin/env python3
"""
Real Property Market Analysis 
NOW READS FROM FORM INPUTS! No more hardcoded values.
Comprehensive statistical analysis with data coverage validation
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from scipy import stats
import seaborn as sns
import json
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# LOAD FORM INPUTS 
# ============================================================================

print("=" * 80)
print("REAL PROPERTY MARKET ANALYSIS")
print("=" * 80)

# Check if form inputs JSON exists
form_json_path = 'market_analysis_inputs.json'
if not os.path.exists(form_json_path):
    print(f"❌ ERROR: Form inputs file not found: {form_json_path}")
    print("   Please ensure the form has been submitted and JSON saved.")
    sys.exit(1)

print(f"✓ Loading form inputs from: {form_json_path}")

# Load form data
try:
    with open(form_json_path, 'r') as f:
        form_data = json.load(f)
    print("✓ Form inputs loaded successfully")
except Exception as e:
    print(f"❌ Error loading form inputs: {e}")
    sys.exit(1)

# === Normalize alternate form JSON keys to canonical keys expected by the script ===
alt_key_map = {
    'subject_gla': 'living_area',
    'subject_living_area': 'living_area',
    'subject_livingarea': 'living_area',
    'subject_bedrooms': 'bedrooms_total',
    'subject_beds': 'bedrooms_total',
    'subject_bathrooms': 'bathrooms_total',
    'subject_baths': 'bathrooms_total',
    'subject_garage': 'garage_spaces',
    'subject_address': 'address',
    'subject_city': 'filter_city',
    'subject_state': 'filter_state',
    'subject_zip': 'filter_zip',
    'adjustment_threshold': 'sf_threshold_percent',
    'time_threshold': 'time_threshold_days',
    'csv_path': 'csv_path'
}
for alt, canon in alt_key_map.items():
    if alt in form_data and canon not in form_data:
        form_data[canon] = form_data[alt]

  # ============================================================================
# CSV PATH (CLI arg OR JSON field) — permanent fix
# ============================================================================
# Robust CSV path resolution supporting CLI arg and optional JSON-like form_data.
# Precedence: CLI arg > form_data keys > optional GUI picker > error out.  

# ============================================================================
# EXTRACT CONFIGURATION FROM FORM 
# ============================================================================

print("\n[CONFIGURATION] Extracting values from form...")

# Subject Property Information
SUBJECT_ADDRESS = form_data.get('address', 'N/A')
SUBJECT_LIVING_AREA = int(form_data.get('living_area', 0))
SUBJECT_BEDROOMS = int(form_data.get('bedrooms_total', 0))
SUBJECT_BATHROOMS = float(form_data.get('bathrooms_total', 0))
SUBJECT_GARAGE = int(form_data.get('garage_spaces', form_data.get('subject_garage', 0) or 0))
SUBJECT_YEAR_BUILT = int(form_data.get('year_built', 0))

# Report Information
APPRAISER_NAME = form_data.get('appraiser_name', 'N/A')
APPRAISER_CREDENTIALS = form_data.get('appraiser_credentials', 'N/A')
FILE_NUMBER = form_data.get('file_number', 'N/A')
date_of_value_str = form_data.get('effective_date', '')
try:
    DATE_OF_VALUE = datetime.strptime(date_of_value_str, '%Y-%m-%d')
except:
    print(f"⚠ Warning: Could not parse date '{date_of_value_str}', using today")
    DATE_OF_VALUE = datetime.now()

# Analysis thresholds
TIME_ADJUSTMENT_THRESHOLD_DAYS = int(form_data.get('time_threshold_days', form_data.get('time_threshold', 30)))
LIVING_AREA_ADJUSTMENT_THRESHOLD_PCT = float(form_data.get('sf_threshold_percent', form_data.get('adjustment_threshold', 5.0)))

# Market segment criteria from form
MARKET_SEGMENT = {
    'Property Type': form_data.get('property_type', 'N/A'),
    'County': form_data.get('filter_county', 'N/A'),
    'City': form_data.get('filter_city', 'N/A'),
    'Zip': form_data.get('filter_zip', 'N/A'),
    'MLS Area': form_data.get('filter_mls_area', 'N/A'),
    'Bedrooms': form_data.get('filter_bedrooms', 'N/A'),
    'Bathrooms': form_data.get('filter_bathrooms', 'N/A'),
    'Living Area Range': form_data.get('filter_living_area', 'N/A'),
    'Lot Size': form_data.get('filter_lot_size', 'N/A'),
    'Transaction Type': form_data.get('transaction_type', 'N/A'),
    'Date Range': form_data.get('transaction_date_range', 'N/A')
}

print(f"Subject Property: {SUBJECT_ADDRESS}")
print(f"Living Area: {SUBJECT_LIVING_AREA:,} SF")
print(f"Appraiser: {APPRAISER_NAME}")
print(f"File Number: {FILE_NUMBER}")
print(f"Date of Value: {DATE_OF_VALUE.strftime('%B %d, %Y')}")
print(f"Time Adjustment Threshold: {TIME_ADJUSTMENT_THRESHOLD_DAYS} days")
print(f"Living Area Adjustment Threshold: {LIVING_AREA_ADJUSTMENT_THRESHOLD_PCT}%")
print("=" * 80)

#

import argparse

# Ensure form_data exists (avoid NameError if not provided by the caller)
try:
    form_data
except NameError:
    form_data = {}

# Parse CLI args (keep -h/--help for discoverability)
parser = argparse.ArgumentParser(description="Select a sales CSV to analyze.")
parser.add_argument("csv_path", nargs="?", help="Path to sales CSV file")
parser.add_argument("--allow-gui-picker", action="store_true", help="Open a file dialog if no path is provided")
args, _ = parser.parse_known_args()

# 1) CLI arg
csv_path = None
if args.csv_path:
    csv_path = str(args.csv_path).strip()

# 2) JSON-like form_data keys
if not csv_path:
    for key in ("csv_path", "csv", "sales_csv", "data_file"):
        val = form_data.get(key, "")
        if isinstance(val, str) and val.strip():
            csv_path = val.strip()
            break

# 3) Optional GUI picker
if not csv_path and args.allow_gui_picker:
    try:
        import tkinter as tk
        from tkinter import filedialog
        tkroot = tk.Tk()
        tkroot.withdraw()
        chosen = filedialog.askopenfilename(
            title="Select Sales CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        tkroot.destroy()
        if chosen:
            csv_path = chosen
    except Exception:
        pass

# Final validation
if not csv_path:
    print("ERROR: No CSV path provided. Provide a path as a CLI arg or via form_data keys: csv_path, csv, sales_csv, data_file. Optionally use --allow-gui-picker to open a file dialog.")
    sys.exit(2)

# Resolve CSV path: prefer absolute, but allow filename-only matches in the script directory
csv_path = os.path.abspath(os.path.expanduser(csv_path))
script_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(csv_path):
    # Try a candidate in the script directory
    candidate = os.path.join(script_dir, os.path.basename(csv_path))
    if os.path.exists(candidate):
        csv_path = candidate
    else:
        # Try case-insensitive match in script directory
        basename = os.path.basename(csv_path).lower()
        matches = [os.path.join(script_dir, f) for f in os.listdir(script_dir) if f.lower() == basename]
        if matches:
            csv_path = matches[0]
        else:
            print("ERROR: CSV not found at:")
            print("   " + csv_path)
            print("Tried script directory candidates: ", candidate)
            sys.exit(1)

# Proceed after this point; csv_path is valid
# Example:
# df = pd.read_csv(csv_path, parse_dates=['Close Date'])

# Load CSV into DataFrame
df = pd.read_csv(csv_path)

# Normalize column names (strip whitespace)
df.columns = [c.strip() for c in df.columns]

# Heuristic mapping: map common header variants to final canonical column names used below
rename_map = {}
for col in df.columns:
    low = col.lower()
    if ('price' in low and ('close' in low or 'sale' in low)) or low.strip() == 'price':
        rename_map[col] = 'Sale_Price'
    elif (('close' in low or 'sale' in low) and 'date' in low) or low.strip() in ('closedate', 'saledate'):
        rename_map[col] = 'Sale_Date'
    elif 'living' in low or 'gla' in low or 'sqft' in low or 'square' in low:
        rename_map[col] = 'Living_Area'
    elif 'bed' in low and 'room' not in low:
        # bedrooms, beds
        rename_map[col] = 'Bedrooms'
    elif 'bath' in low:
        rename_map[col] = 'Bathrooms'
    elif 'street number' in low or 'street_number' in low or 'street no' in low:
        rename_map[col] = 'Street_Number'
    elif ('street' in low and 'name' in low) or (low.startswith('street') and 'name' not in low and 'st' in low):
        rename_map[col] = 'Street_Name'
    elif 'dom' == low or 'days on market' in low or 'days active' in low or 'days_active' in low:
        rename_map[col] = 'DOM'
    elif 'cdom' in low or 'cumulative' in low:
        rename_map[col] = 'CDOM'
    elif 'garage' in low:
        rename_map[col] = 'Garage'

# Apply renames
if rename_map:
    df.rename(columns=rename_map, inplace=True)

# Verify required final columns exist
required_final = ['Sale_Price', 'Sale_Date', 'Living_Area', 'Bedrooms', 'Bathrooms', 'Street_Number', 'Street_Name', 'DOM', 'CDOM', 'Garage']
missing_final = [c for c in required_final if c not in df.columns]
if missing_final:
    print(f"❌ ERROR: Missing required final columns in CSV after heuristic mapping: {', '.join(missing_final)}")
    sys.exit(1)

# Ensure Sale_Date is datetime
try:
    df['Sale_Date'] = pd.to_datetime(df['Sale_Date'], errors='coerce')
except Exception:
    print("❌ ERROR: Could not parse Sale_Date column into dates.")
    sys.exit(1)

# Fix output paths to be relative to script directory
output_dir = os.path.dirname(os.path.abspath(__file__))

# Validate required form fields
required_fields = ['address', 'living_area', 'bedrooms_total', 'bathrooms_total']
missing_fields = [f for f in required_fields if not form_data.get(f)]
if missing_fields:
    print("❌ ERROR: Missing required form fields:", ", ".join(missing_fields))
    sys.exit(1)

# At this point columns have been mapped to final canonical names (Sale_Price, Sale_Date, Living_Area, Bedrooms, Bathrooms, Street_Number, Street_Name, DOM, CDOM, Garage)

# Filter sales on or before date of value
df = df[df['Sale_Date'] <= DATE_OF_VALUE].copy()

print(f"  - Sales on or before {DATE_OF_VALUE.strftime('%m/%d/%Y')}: {len(df)}")

if df.empty:
    print(f"⚠ WARNING: No sales on or before {DATE_OF_VALUE.strftime('%Y-%m-%d')}. Nothing to analyze.")
    validation_info = {
        'date_of_value': DATE_OF_VALUE.isoformat(),
        'message': 'No sales on or before date of value',
        'subject_property': {
            'address': SUBJECT_ADDRESS,
            'living_area': SUBJECT_LIVING_AREA
        }
    }
    with open(os.path.join(output_dir, 'validation_info.json'), 'w') as f:
        json.dump(validation_info, f, indent=2, default=str)
    # Save an empty processed CSV for tooling expectations
    df.to_csv(os.path.join(output_dir, 'sales_data_processed.csv'), index=False)
    sys.exit(0)

# Calculate derived metrics
df['Price_Per_SF'] = df['Sale_Price'] / df['Living_Area']
df['Days_From_DOV'] = (DATE_OF_VALUE - df['Sale_Date']).dt.days

# Sort by sale date
df = df.sort_values('Sale_Date').reset_index(drop=True)

# ============================================================================
# STEP 2: DATA COVERAGE VALIDATION
# ============================================================================

print("\n[STEP 2] DATA COVERAGE VALIDATION")
print("-" * 80)

# Calculate actual data coverage
earliest_sale = df['Sale_Date'].min()
latest_sale = df['Sale_Date'].max()
actual_coverage_days = (DATE_OF_VALUE - earliest_sale).days
actual_coverage_months = actual_coverage_days / 30.44

print(f"  Earliest Sale Date: {earliest_sale.strftime('%B %d, %Y')}")
print(f"  Latest Sale Date: {latest_sale.strftime('%B %d, %Y')}")  
print(f"  Date of Value: {DATE_OF_VALUE.strftime('%B %d, %Y')}")
print(f"  Actual Data Coverage: {actual_coverage_months:.1f} months ({actual_coverage_days} days)")

# Define standard time periods
time_periods = [
    ('0-3 months', 3),
    ('4-6 months', 6),
    ('7-9 months', 9),
    ('9-12 months', 12),
    ('0-6 months', 6),
    ('0-12 months', 12),
    ('0-18 months', 18),
    ('0-24 months', 24),
    ('0-36 months', 36)
]

# Validate periods
valid_periods = []
omitted_periods = []
period_sales_counts = {}

print("\n  Period Validation:")
print("  " + "-" * 76)

buffer_months = 1  # 1-month buffer for period validation

for period_name, period_months in time_periods:
    # Calculate cutoff date for this period
    cutoff_date = DATE_OF_VALUE - timedelta(days=int(period_months * 30.44))
    
    # Count sales in this period
    period_sales = df[df['Sale_Date'] >= cutoff_date]
    sales_count = len(period_sales)
    period_sales_counts[period_name] = sales_count
    
    # Check 1: Does period extend beyond data coverage?
    if period_months > (actual_coverage_months + buffer_months):
        reason = f"extends beyond data coverage ({actual_coverage_months:.1f} months)"
        omitted_periods.append({
            'name': period_name,
            'months': period_months,
            'reason': reason,
            'sales_count': sales_count
        })
        print(f"  ✗ OMIT {period_name:15s}: {reason}")
        continue
    
    # Check 2: Does period duplicate previous period?
    if valid_periods:
        last_count = valid_periods[-1]['sales_count']
        if sales_count == last_count:
            reason = f"identical sales count to {valid_periods[-1]['name']} (n={sales_count})"
            omitted_periods.append({
                'name': period_name,
                'months': period_months,
                'reason': reason,
                'sales_count': sales_count
            })
            print(f"  ✗ OMIT {period_name:15s}: {reason}")
            continue
    
    # Check 3: Minimum data threshold
    status_flag = ""
    if sales_count < 3:
        status_flag = " ⚠ INSUFFICIENT DATA"
    
    # Period is valid - include it
    valid_periods.append({
        'name': period_name,
        'months': period_months,
        'sales_count': sales_count,
        'cutoff_date': cutoff_date,
        'status': 'valid'
    })
    print(f"  ✓ INCLUDE {period_name:12s}: n={sales_count:2d} sales{status_flag}")

print(f"\n  Summary: {len(valid_periods)} periods included, {len(omitted_periods)} periods omitted")

# ============================================================================
# STEP 3: CALCULATE STATISTICS FOR VALID PERIODS
# ============================================================================

print("\n[STEP 3] Calculating statistics for valid time periods...")

statistics = []

for period in valid_periods:
    period_name = period['name']
    cutoff_date = period['cutoff_date']
    
    # Filter sales for this period
    period_df = df[df['Sale_Date'] >= cutoff_date].copy()
    n = len(period_df)
    
    if n == 0:
        continue
    
    # Calculate statistics
    stats_dict = {
        'Period': period_name,
        'Months': period['months'],
        'N_Sales': n,
        'Absorption_Rate': n / period['months'],
        'Price_Mean': period_df['Sale_Price'].mean(),
        'Price_Median': period_df['Sale_Price'].median(),
        'Price_Std': period_df['Sale_Price'].std(),
        'PriceSF_Mean': period_df['Price_Per_SF'].mean(),
        'PriceSF_Median': period_df['Price_Per_SF'].median(),
        'PriceSF_Std': period_df['Price_Per_SF'].std()
    }
    
    # Add DOM statistics if available
    if 'DOM' in period_df.columns and period_df['DOM'].notna().sum() > 0:
        stats_dict['DOM_Mean'] = period_df['DOM'].mean()
        stats_dict['DOM_Median'] = period_df['DOM'].median()
    
    statistics.append(stats_dict)
    
    print(f"  ✓ {period_name:12s}: {n:2d} sales, ${stats_dict['Price_Median']:,.0f} median")

stats_df = pd.DataFrame(statistics)

# ============================================================================
# STEP 4: TREND ANALYSIS
# ============================================================================

print("\n[STEP 4] Performing trend analysis...")

# Use sales from 0-12 month period for trend analysis
if '0-12 months' in [p['name'] for p in valid_periods]:
    trend_cutoff = DATE_OF_VALUE - timedelta(days=int(12 * 30.44))
    trend_df = df[df['Sale_Date'] >= trend_cutoff].copy()
else:
    # Use all available data
    trend_df = df.copy()

# Convert dates to numeric for regression
trend_df['Days_Numeric'] = (trend_df['Sale_Date'] - trend_df['Sale_Date'].min()).dt.days

# Linear regression for Sale Price
# Initialize regression variables to safe defaults
slope_price = intercept_price = r_value_price = p_value_price = std_err_price = 0
slope_pricesf = intercept_pricesf = r_value_pricesf = p_value_pricesf = std_err_pricesf = 0

if len(trend_df) >= 2:
    slope_price, intercept_price, r_value_price, p_value_price, std_err_price = \
        stats.linregress(trend_df['Days_Numeric'], trend_df['Sale_Price'])
    
    slope_pricesf, intercept_pricesf, r_value_pricesf, p_value_pricesf, std_err_pricesf = \
        stats.linregress(trend_df['Days_Numeric'], trend_df['Price_Per_SF'])
    
    # Calculate daily and monthly changes
    daily_price_change = slope_price
    monthly_price_change_pct = (slope_price * 30.44 / trend_df['Sale_Price'].mean()) * 100
    
    daily_pricesf_change = slope_pricesf
    monthly_pricesf_change_pct = (slope_pricesf * 30.44 / trend_df['Price_Per_SF'].mean()) * 100
    
    print(f"  Linear Trend (Sale Price):")
    print(f"    - Daily change: ${daily_price_change:,.2f}/day")
    print(f"    - Monthly change: {monthly_price_change_pct:+.2f}%/month")
    print(f"    - R² = {r_value_price**2:.3f}")
    
    print(f"  Linear Trend (Price/SF):")
    print(f"    - Daily change: ${daily_pricesf_change:,.3f}/SF/day")
    print(f"    - Monthly change: {monthly_pricesf_change_pct:+.2f}%/month")
    print(f"    - R² = {r_value_pricesf**2:.3f}")
    
    # Determine market trend
    if daily_price_change > 0.50:
        market_trend = "INCREASING"
    elif daily_price_change < -0.50:
        market_trend = "DECREASING"
    elif r_value_price**2 < 0.3:
        market_trend = "UNSTABLE"
    else:
        market_trend = "STABLE"
    
    print(f"\n  Market Trend Determination: {market_trend}")
    
else:
    print("  ⚠ Insufficient data for trend analysis")
    slope_price = 0
    daily_price_change = 0
    monthly_price_change_pct = 0
    slope_pricesf = 0
    market_trend = "INSUFFICIENT DATA"

# Save trend analysis results
trend_results = {
    'slope_price': slope_price if len(trend_df) >= 2 else 0,
    'daily_price_change': daily_price_change if len(trend_df) >= 2 else 0,
    'monthly_price_change_pct': monthly_price_change_pct if len(trend_df) >= 2 else 0,
    'slope_pricesf': slope_pricesf if len(trend_df) >= 2 else 0,
    'market_trend': market_trend,
    'r_squared': r_value_price**2 if len(trend_df) >= 2 else 0
}

print(f"\n✓ Analysis complete for {len(df)} sales in {len(valid_periods)} valid time periods")
print("=" * 80)

# ============================================================================
# SAVE INTERMEDIATE RESULTS
# ============================================================================

# Save processed data
df.to_csv(os.path.join(output_dir, 'sales_data_processed.csv'), index=False)
stats_df.to_csv(os.path.join(output_dir, 'statistics_summary.csv'), index=False)

# Save all configuration and validation info
validation_info = {
    'date_of_value': DATE_OF_VALUE.isoformat(),
    'earliest_sale': earliest_sale.isoformat(),
    'latest_sale': latest_sale.isoformat(),
    'actual_coverage_months': actual_coverage_months,
    'valid_periods': valid_periods,
    'omitted_periods': omitted_periods,
    'trend_results': trend_results,
    'subject_property': {
        'address': SUBJECT_ADDRESS,
        'living_area': SUBJECT_LIVING_AREA,
        'bedrooms': SUBJECT_BEDROOMS,
        'bathrooms': SUBJECT_BATHROOMS,
        'garage': SUBJECT_GARAGE,
        'year_built': SUBJECT_YEAR_BUILT
    },
    'report_info': {
        'appraiser_name': APPRAISER_NAME,
        'appraiser_credentials': APPRAISER_CREDENTIALS,
        'file_number': FILE_NUMBER
    },
    'thresholds': {
        'time_adjustment_days': TIME_ADJUSTMENT_THRESHOLD_DAYS,
        'sf_adjustment_pct': LIVING_AREA_ADJUSTMENT_THRESHOLD_PCT
    },
    'market_segment': MARKET_SEGMENT
}

with open(os.path.join(output_dir, 'validation_info.json'), 'w') as f:
    json.dump(validation_info, f, indent=2, default=str)

print("Data processed and statistics calculated successfully!")
print("Intermediate files saved:")
print("  - sales_data_processed.csv")
print("  - statistics_summary.csv")
print("  - validation_info.json")
