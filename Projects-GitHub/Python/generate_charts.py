#!/usr/bin/env python3
"""
Chart Generation Script - Professional real estate market analysis charts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
import seaborn as sns
from scipy import stats

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load processed data
df = pd.read_csv('sales_data_processed.csv')
df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
stats_df = pd.read_csv('statistics_summary.csv')

with open('validation_info.json', 'r') as f:
    validation_info = json.load(f)

DATE_OF_VALUE = datetime(2013, 12, 31)

print("=" * 80)
print("GENERATING PROFESSIONAL CHARTS")
print("=" * 80)

# ============================================================================
# CHART 1: SALES PRICE TREND WITH LINEAR REGRESSION
# ============================================================================

print("\n[Chart 1] Sales Price Trend with Linear Regression...")

fig, ax = plt.subplots(figsize=(12, 7))

# Scatter plot of sales
ax.scatter(df['Sale_Date'], df['Sale_Price'], s=100, alpha=0.6, 
           c='#2E86AB', edgecolors='black', linewidth=1, label='Closed Sales')

# Linear regression line
df['Days_Numeric'] = (df['Sale_Date'] - df['Sale_Date'].min()).dt.days
slope, intercept, r_value, _, _ = stats.linregress(df['Days_Numeric'], df['Sale_Price'])

x_line = np.array([df['Days_Numeric'].min(), df['Days_Numeric'].max()])
y_line = slope * x_line + intercept
dates_line = [df['Sale_Date'].min(), df['Sale_Date'].max()]

ax.plot(dates_line, y_line, 'r--', linewidth=2, label=f'Linear Trend (R²={r_value**2:.3f})')

# Formatting
ax.set_xlabel('Sale Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Sale Price ($)', fontsize=12, fontweight='bold')
ax.set_title('Sale Price Trend Analysis\n528 S. Taper Ave, Compton, CA', 
             fontsize=14, fontweight='bold', pad=20)

# Format y-axis as currency
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Format x-axis dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45)

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Add text box with statistics
textstr = f'N = {len(df)} sales\n'
textstr += f'Date Range: {df["Sale_Date"].min().strftime("%m/%d/%Y")} - {df["Sale_Date"].max().strftime("%m/%d/%Y")}\n'
textstr += f'Median Price: ${df["Sale_Price"].median():,.0f}\n'
textstr += f'Mean Price: ${df["Sale_Price"].mean():,.0f}\n'
textstr += f'Trend: +${slope:.2f}/day'

props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)

ax.legend(loc='lower right', fontsize=10)
plt.tight_layout()
plt.savefig('01_Sale_Price_Trend.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 01_Sale_Price_Trend.png")

# ============================================================================
# CHART 2: PRICE PER SQUARE FOOT TREND
# ============================================================================

print("[Chart 2] Price Per Square Foot Trend...")

fig, ax = plt.subplots(figsize=(12, 7))

# Scatter plot
ax.scatter(df['Sale_Date'], df['Price_Per_SF'], s=100, alpha=0.6,
           c='#A23B72', edgecolors='black', linewidth=1, label='Closed Sales')

# Linear regression
slope_sf, intercept_sf, r_value_sf, _, _ = stats.linregress(df['Days_Numeric'], df['Price_Per_SF'])
y_line_sf = slope_sf * x_line + intercept_sf

ax.plot(dates_line, y_line_sf, 'r--', linewidth=2, label=f'Linear Trend (R²={r_value_sf**2:.3f})')

# Formatting
ax.set_xlabel('Sale Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Price Per Square Foot ($/SF)', fontsize=12, fontweight='bold')
ax.set_title('Price Per Square Foot Trend Analysis\n528 S. Taper Ave, Compton, CA',
             fontsize=14, fontweight='bold', pad=20)

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45)

ax.grid(True, alpha=0.3, linestyle='--')

# Statistics box
textstr = f'N = {len(df)} sales\n'
textstr += f'Median: ${df["Price_Per_SF"].median():.2f}/SF\n'
textstr += f'Mean: ${df["Price_Per_SF"].mean():.2f}/SF\n'
textstr += f'Std Dev: ${df["Price_Per_SF"].std():.2f}/SF\n'
textstr += f'Trend: +${slope_sf:.3f}/SF/day'

props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)

ax.legend(loc='lower right', fontsize=10)
plt.tight_layout()
plt.savefig('02_Price_Per_SF_Trend.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 02_Price_Per_SF_Trend.png")

# ============================================================================
# CHART 3: PRICE STATISTICS BY TIME PERIOD
# ============================================================================

print("[Chart 3] Price Statistics by Time Period...")

fig, ax = plt.subplots(figsize=(12, 7))

periods = stats_df['Period'].tolist()
mean_prices = stats_df['Price_Mean'].tolist()
median_prices = stats_df['Price_Median'].tolist()

x = np.arange(len(periods))
width = 0.35

bars1 = ax.bar(x - width/2, mean_prices, width, label='Mean', 
               color='#FF6B6B', alpha=0.8, edgecolor='black')
bars2 = ax.bar(x + width/2, median_prices, width, label='Median',
               color='#4ECDC4', alpha=0.8, edgecolor='black')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')

ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
ax.set_ylabel('Sale Price ($)', fontsize=12, fontweight='bold')
ax.set_title('Mean and Median Sale Prices by Time Period\n528 S. Taper Ave, Compton, CA',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(periods, rotation=45, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('03_Price_By_Period.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 03_Price_By_Period.png")

# ============================================================================
# CHART 4: ABSORPTION RATE CHART
# ============================================================================

print("[Chart 4] Absorption Rate by Time Period...")

fig, ax = plt.subplots(figsize=(12, 7))

periods = stats_df['Period'].tolist()
absorption_rates = stats_df['Absorption_Rate'].tolist()
n_sales = stats_df['N_Sales'].tolist()

bars = ax.bar(periods, absorption_rates, color='#95E1D3', alpha=0.8, 
              edgecolor='black', linewidth=1.5)

# Add value labels
for i, (bar, n) in enumerate(zip(bars, n_sales)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}\n(n={n})',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
ax.set_ylabel('Absorption Rate (Sales/Month)', fontsize=12, fontweight='bold')
ax.set_title('Monthly Absorption Rate by Time Period\n528 S. Taper Ave, Compton, CA',
             fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('04_Absorption_Rate.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 04_Absorption_Rate.png")

# ============================================================================
# CHART 5: PRICE DISTRIBUTION (HISTOGRAM)
# ============================================================================

print("[Chart 5] Price Distribution...")

fig, ax = plt.subplots(figsize=(12, 7))

ax.hist(df['Sale_Price'], bins=15, color='#F38181', alpha=0.7, 
        edgecolor='black', linewidth=1.5)

# Add vertical lines for mean and median
ax.axvline(df['Sale_Price'].mean(), color='red', linestyle='--', 
           linewidth=2, label=f'Mean: ${df["Sale_Price"].mean():,.0f}')
ax.axvline(df['Sale_Price'].median(), color='blue', linestyle='--',
           linewidth=2, label=f'Median: ${df["Sale_Price"].median():,.0f}')

ax.set_xlabel('Sale Price ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Frequency (Number of Sales)', fontsize=12, fontweight='bold')
ax.set_title('Sale Price Distribution\n528 S. Taper Ave, Compton, CA',
             fontsize=14, fontweight='bold', pad=20)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('05_Price_Distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 05_Price_Distribution.png")

# ============================================================================
# CHART 6: PRICE PER SF DISTRIBUTION
# ============================================================================

print("[Chart 6] Price Per SF Distribution...")

fig, ax = plt.subplots(figsize=(12, 7))

ax.hist(df['Price_Per_SF'], bins=15, color='#AA96DA', alpha=0.7,
        edgecolor='black', linewidth=1.5)

ax.axvline(df['Price_Per_SF'].mean(), color='red', linestyle='--',
           linewidth=2, label=f'Mean: ${df["Price_Per_SF"].mean():.2f}/SF')
ax.axvline(df['Price_Per_SF'].median(), color='blue', linestyle='--',
           linewidth=2, label=f'Median: ${df["Price_Per_SF"].median():.2f}/SF')

ax.set_xlabel('Price Per Square Foot ($/SF)', fontsize=12, fontweight='bold')
ax.set_ylabel('Frequency (Number of Sales)', fontsize=12, fontweight='bold')
ax.set_title('Price Per Square Foot Distribution\n528 S. Taper Ave, Compton, CA',
             fontsize=14, fontweight='bold', pad=20)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}'))
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('06_PriceSF_Distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 06_PriceSF_Distribution.png")

# ============================================================================
# CHART 7: LIVING AREA VS SALE PRICE SCATTER
# ============================================================================

print("[Chart 7] Living Area vs Sale Price...")

fig, ax = plt.subplots(figsize=(12, 7))

# Scatter plot
ax.scatter(df['Living_Area'], df['Sale_Price'], s=100, alpha=0.6,
           c='#FFD93D', edgecolors='black', linewidth=1, label='Closed Sales')

# Add regression line
slope_la, intercept_la, r_value_la, _, _ = stats.linregress(df['Living_Area'], df['Sale_Price'])
x_la = np.array([df['Living_Area'].min(), df['Living_Area'].max()])
y_la = slope_la * x_la + intercept_la
ax.plot(x_la, y_la, 'r--', linewidth=2, label=f'Linear Fit (R²={r_value_la**2:.3f})')

# Mark subject property
ax.axvline(951, color='green', linestyle=':', linewidth=2, label='Subject (951 SF)')

ax.set_xlabel('Living Area (Square Feet)', fontsize=12, fontweight='bold')
ax.set_ylabel('Sale Price ($)', fontsize=12, fontweight='bold')
ax.set_title('Sale Price vs Living Area\n528 S. Taper Ave, Compton, CA',
             fontsize=14, fontweight='bold', pad=20)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Add slope info
textstr = f'Slope: ${slope_la:.2f}/SF\n'
textstr += f'Regression equation:\n'
textstr += f'Price = ${intercept_la:,.0f} + ${slope_la:.2f} × SF'

props = dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
ax.text(0.98, 0.02, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='bottom', horizontalalignment='right', bbox=props)

plt.tight_layout()
plt.savefig('07_Living_Area_vs_Price.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: 07_Living_Area_vs_Price.png")

print("\n" + "=" * 80)
print("✓ All charts generated successfully!")
print("  Location: Current directory")
print("=" * 80)
