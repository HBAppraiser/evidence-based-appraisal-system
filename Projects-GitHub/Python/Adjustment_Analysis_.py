#!/usr/bin/env python3
"""
Comparable Sales Adjustment Analysis - Version 2.3.3
NOW READS FROM SHARED CONFIG! No more hardcoded values.
Calculate time and living area adjustments for comparable sales
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json
import sys

print("=" * 80)
print("COMPARABLE SALES ADJUSTMENT ANALYSIS - VERSION 2.3.3")
print("=" * 80)

# ============================================================================
# LOAD CONFIGURATION FROM SHARED FILES (NEW IN VERSION 2.3.3)
# ============================================================================

print("\n[LOADING] Reading configuration from shared files...")

# Load processed data from market_analysis
try:
    df = pd.read_csv('sales_data_processed.csv')
    df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
    print(f"✓ Loaded {len(df)} processed sales records")
except Exception as e:
    print(f"❌ Error loading processed sales data: {e}")
    print("   Please run market_analysis_v2.3.3.py first")
    sys.exit(1)

# Load validation info with all configuration
try:
    with open('validation_info.json', 'r') as f:
        validation_info = json.load(f)
    print("✓ Loaded validation info and configuration")
except Exception as e:
    print(f"❌ Error loading validation info: {e}")
    print("   Please run market_analysis_v2.3.3.py first")
    sys.exit(1)

# Extract configuration values
SUBJECT_LIVING_AREA = validation_info['subject_property']['living_area']
DATE_OF_VALUE = datetime.fromisoformat(validation_info['date_of_value'])
TIME_THRESHOLD_DAYS = validation_info['thresholds']['time_adjustment_days']
SF_THRESHOLD_PCT = validation_info['thresholds']['sf_adjustment_pct']

# Get trend results
trend_results = validation_info['trend_results']
monthly_trend_pct = trend_results['monthly_price_change_pct']
daily_price_change = trend_results['daily_price_change']

print(f"Subject Living Area: {SUBJECT_LIVING_AREA:,} SF")
print(f"Date of Value: {DATE_OF_VALUE.strftime('%B %d, %Y')}")
print(f"Time Adjustment Threshold: {TIME_THRESHOLD_DAYS} days")
print(f"Living Area Adjustment Threshold: {SF_THRESHOLD_PCT}%")
print("=" * 80)

# ============================================================================
# STEP 1: SELECT COMPARABLE SALES (0-12 MONTH PERIOD)
# ============================================================================

print("\n[STEP 1] Selecting comparable sales from 0-12 month period...")

# Use all sales from the 0-12 month period (most comprehensive valid period)
comp_sales = df.copy()

print(f"  - Selected {len(comp_sales)} comparable sales")

# ============================================================================
# STEP 2: CALCULATE TIME ADJUSTMENTS
# ============================================================================

print("\n[STEP 2] Calculating time adjustments...")

# Calculate days difference
# Days_Difference = Date_of_Value - Sale_Date (positive for past sales)
comp_sales['Days_Difference'] = (DATE_OF_VALUE - comp_sales['Sale_Date']).dt.days

# Apply time adjustment threshold
comp_sales['Time_Adj_Amount'] = 0.0
comp_sales['Time_Adj_Pct'] = 0.0

for idx in comp_sales.index:
    days_diff = comp_sales.loc[idx, 'Days_Difference']
    
    if abs(days_diff) > TIME_THRESHOLD_DAYS:
        # Calculate adjustment using daily trend
        # Positive days_diff (past sale) in appreciating market = adjust UP
        adj_amount = daily_price_change * days_diff
        adj_pct = (monthly_trend_pct / 30.44) * days_diff
        
        comp_sales.loc[idx, 'Time_Adj_Amount'] = adj_amount
        comp_sales.loc[idx, 'Time_Adj_Pct'] = adj_pct

print(f"  ✓ Time adjustments calculated")
print(f"  - Market trend: {monthly_trend_pct:+.2f}% per month")
print(f"  - Daily change: ${daily_price_change:+.2f}/day")
print(f"  - Adjustments applied: {(comp_sales['Time_Adj_Amount'] != 0).sum()} of {len(comp_sales)}")

# ============================================================================
# STEP 3: CALCULATE LIVING AREA ADJUSTMENTS
# ============================================================================

print("\n[STEP 3] Calculating living area adjustments...")

# Calculate SF difference from subject
comp_sales['SF_Difference'] = comp_sales['Living_Area'] - SUBJECT_LIVING_AREA
comp_sales['SF_Difference_Pct'] = (comp_sales['SF_Difference'] / SUBJECT_LIVING_AREA) * 100

# Calculate marginal value per SF using regression
from scipy import stats
slope_sf, intercept_sf, r_value_sf, _, _ = stats.linregress(
    comp_sales['Living_Area'], comp_sales['Sale_Price'])

marginal_value_per_sf = slope_sf

print(f"  - Marginal value per SF: ${marginal_value_per_sf:.2f}/SF")
print(f"  - Regression R²: {r_value_sf**2:.3f}")

# Apply living area adjustment threshold
comp_sales['SF_Adj_Amount'] = 0.0
comp_sales['SF_Adj_Pct'] = 0.0

for idx in comp_sales.index:
    sf_diff_pct = abs(comp_sales.loc[idx, 'SF_Difference_Pct'])
    
    if sf_diff_pct > SF_THRESHOLD_PCT:
        # Calculate adjustment
        sf_diff = comp_sales.loc[idx, 'SF_Difference']
        adj_amount = -sf_diff * marginal_value_per_sf  # Negative because bigger comp needs negative adjustment
        adj_pct = -(sf_diff / SUBJECT_LIVING_AREA) * 100
        
        comp_sales.loc[idx, 'SF_Adj_Amount'] = adj_amount
        comp_sales.loc[idx, 'SF_Adj_Pct'] = adj_pct

print(f"  ✓ Living area adjustments calculated")
print(f"  - Adjustments applied: {(comp_sales['SF_Adj_Amount'] != 0).sum()} of {len(comp_sales)}")

# ============================================================================
# STEP 4: CALCULATE NET ADJUSTMENTS AND ADJUSTED VALUES
# ============================================================================

print("\n[STEP 4] Calculating net adjustments and adjusted values...")

# Calculate net adjustment
comp_sales['Net_Adj_Amount'] = comp_sales['Time_Adj_Amount'] + comp_sales['SF_Adj_Amount']
comp_sales['Net_Adj_Pct'] = comp_sales['Time_Adj_Pct'] + comp_sales['SF_Adj_Pct']

# Calculate adjusted sale price
comp_sales['Adjusted_Sale_Price'] = comp_sales['Sale_Price'] + comp_sales['Net_Adj_Amount']
comp_sales['Adjusted_Price_Per_SF'] = comp_sales['Adjusted_Sale_Price'] / comp_sales['Living_Area']

print(f"  ✓ Net adjustments calculated")

# ============================================================================
# STEP 5: CALCULATE ADJUSTED STATISTICS
# ============================================================================

print("\n[STEP 5] Calculating statistics for adjusted values...")

# Unadjusted statistics
unadj_mean = comp_sales['Sale_Price'].mean()
unadj_median = comp_sales['Sale_Price'].median()
unadj_mean_psf = comp_sales['Price_Per_SF'].mean()
unadj_median_psf = comp_sales['Price_Per_SF'].median()

# Adjusted statistics
adj_mean = comp_sales['Adjusted_Sale_Price'].mean()
adj_median = comp_sales['Adjusted_Sale_Price'].median()
adj_mean_psf = comp_sales['Adjusted_Price_Per_SF'].mean()
adj_median_psf = comp_sales['Adjusted_Price_Per_SF'].median()

print(f"\n  UNADJUSTED VALUES:")
print(f"    Mean Sale Price:   ${unadj_mean:,.0f}")
print(f"    Median Sale Price: ${unadj_median:,.0f}")
print(f"    Mean Price/SF:     ${unadj_mean_psf:,.2f}/SF")
print(f"    Median Price/SF:   ${unadj_median_psf:,.2f}/SF")

print(f"\n  ADJUSTED VALUES:")
print(f"    Mean Sale Price:   ${adj_mean:,.0f}   (change: {((adj_mean/unadj_mean)-1)*100:+.2f}%)")
print(f"    Median Sale Price: ${adj_median:,.0f}   (change: {((adj_median/unadj_median)-1)*100:+.2f}%)")
print(f"    Mean Price/SF:     ${adj_mean_psf:,.2f}/SF   (change: {((adj_mean_psf/unadj_mean_psf)-1)*100:+.2f}%)")
print(f"    Median Price/SF:   ${adj_median_psf:,.2f}/SF   (change: {((adj_median_psf/unadj_median_psf)-1)*100:+.2f}%)")

# ============================================================================
# STEP 6: ADJUSTMENT SUMMARY
# ============================================================================

print("\n[STEP 6] Adjustment summary...")

# Count adjustments by type
time_adj_count = (comp_sales['Time_Adj_Amount'] != 0).sum()
sf_adj_count = (comp_sales['SF_Adj_Amount'] != 0).sum()
both_adj_count = ((comp_sales['Time_Adj_Amount'] != 0) & (comp_sales['SF_Adj_Amount'] != 0)).sum()
no_adj_count = ((comp_sales['Time_Adj_Amount'] == 0) & (comp_sales['SF_Adj_Amount'] == 0)).sum()

print(f"\n  ADJUSTMENT APPLICATION:")
print(f"    Time adjustments only:        {time_adj_count - both_adj_count:2d} sales")
print(f"    Living area adjustments only: {sf_adj_count - both_adj_count:2d} sales")
print(f"    Both adjustments:             {both_adj_count:2d} sales")
print(f"    No adjustments:               {no_adj_count:2d} sales")

# Average adjustment amounts
avg_time_adj = comp_sales.loc[comp_sales['Time_Adj_Amount'] != 0, 'Time_Adj_Amount'].mean()
avg_sf_adj = comp_sales.loc[comp_sales['SF_Adj_Amount'] != 0, 'SF_Adj_Amount'].mean()
avg_net_adj = comp_sales['Net_Adj_Amount'].mean()

print(f"\n  AVERAGE ADJUSTMENTS (when applied):")
if not pd.isna(avg_time_adj):
    print(f"    Time adjustment:        ${avg_time_adj:+,.0f}")
if not pd.isna(avg_sf_adj):
    print(f"    Living area adjustment: ${avg_sf_adj:+,.0f}")
print(f"    Net adjustment:         ${avg_net_adj:+,.0f}")

print("\n✓ Adjustment analysis complete!")
print("=" * 80)

# ============================================================================
# SAVE RESULTS
# ============================================================================

# Save adjusted sales data
comp_sales.to_csv('adjusted_sales.csv', index=False)

# Save adjustment summary
adjustment_summary = {
    'subject_living_area': SUBJECT_LIVING_AREA,
    'time_threshold_days': TIME_THRESHOLD_DAYS,
    'sf_threshold_pct': SF_THRESHOLD_PCT,
    'marginal_value_per_sf': marginal_value_per_sf,
    'market_trend_pct_per_month': monthly_trend_pct,
    'daily_price_change': daily_price_change,
    'unadjusted_statistics': {
        'mean_price': unadj_mean,
        'median_price': unadj_median,
        'mean_price_psf': unadj_mean_psf,
        'median_price_psf': unadj_median_psf
    },
    'adjusted_statistics': {
        'mean_price': adj_mean,
        'median_price': adj_median,
        'mean_price_psf': adj_mean_psf,
        'median_price_psf': adj_median_psf
    },
    'adjustment_counts': {
        'time_only': int(time_adj_count - both_adj_count),
        'sf_only': int(sf_adj_count - both_adj_count),
        'both': int(both_adj_count),
        'none': int(no_adj_count)
    }
}

with open('adjustment_summary.json', 'w') as f:
    json.dump(adjustment_summary, f, indent=2)

print("Results saved:")
print("  - adjusted_sales.csv")
print("  - adjustment_summary.json")
