#!/usr/bin/env python3
"""
PDF Report Generator - Professional ERC-formatted market analysis report
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
import json
from datetime import datetime

print("=" * 80)
print("GENERATING PDF REPORT")
print("=" * 80)

# Load data
stats_df = pd.read_csv('statistics_summary.csv')

with open('validation_info.json', 'r') as f:
    validation_info = json.load(f)

with open('adjustment_summary.json', 'r') as f:
    adjustment_summary = json.load(f)

# Create PDF
pdf_file = 'Market_Analysis_Report_528_S_Taper_Ave.pdf'
doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                        topMargin=0.5*inch, bottomMargin=0.5*inch,
                        leftMargin=0.75*inch, rightMargin=0.75*inch)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#003366'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=12,
    textColor=colors.HexColor('#003366'),
    spaceAfter=8,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

normal_style = styles['Normal']
normal_style.fontSize = 10
normal_style.leading = 14

# ============================================================================
# PAGE 1: TITLE AND SUBJECT INFORMATION
# ============================================================================

print("\n[Page 1] Creating title and subject information...")

# Title
elements.append(Paragraph("REAL PROPERTY MARKET ANALYSIS", title_style))
elements.append(Paragraph("Comprehensive Statistical Analysis - Version 2.3.1", 
                         ParagraphStyle('Subtitle', parent=normal_style, 
                                      alignment=TA_CENTER, fontSize=11, italic=True)))
elements.append(Spacer(1, 0.3*inch))

# Subject Property Information
elements.append(Paragraph("SUBJECT PROPERTY", heading_style))

subject_data = [
    ['Address:', '528 S. Taper Ave, Compton, CA 90220'],
    ['Living Area:', '951 SF'],
    ['Bedrooms / Bathrooms:', '2 / 1'],
    ['Garage:', '1 car'],
    ['Year Built:', '1946'],
]

subject_table = Table(subject_data, colWidths=[2*inch, 5*inch])
subject_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 0),
]))
elements.append(subject_table)
elements.append(Spacer(1, 0.2*inch))

# Report Information
elements.append(Paragraph("REPORT INFORMATION", heading_style))

report_data = [
    ['Appraiser:', 'Craig Gilbert, ASA, SRA, CRP'],
    ['Credentials:', 'Certified General Appraiser'],
    ['File Number:', '25-060'],
    ['Date of Value:', 'December 31, 2013'],
]

report_table = Table(report_data, colWidths=[2*inch, 5*inch])
report_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 0),
]))
elements.append(report_table)
elements.append(Spacer(1, 0.2*inch))

# Market Segment Criteria
elements.append(Paragraph("MARKET SEGMENT CRITERIA", heading_style))

criteria_data = [
    ['Property Type:', 'Single Family Residence (non-distressed)'],
    ['Location:', 'Within 2 miles of subject'],
    ['City:', 'Compton'],
    ['County:', 'Los Angeles'],
    ['MLS Area:', 'RQ - Compton West of Central'],
    ['Living Area:', '800 - 1,300 SF'],
    ['Bedrooms:', '1 - 3'],
    ['Bathrooms:', '1'],
    ['Lot Size:', '5,000+ SF'],
    ['Sale Period:', '01/01/2013 to 03/01/2014'],
]

criteria_table = Table(criteria_data, colWidths=[2*inch, 5*inch])
criteria_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 0),
]))
elements.append(criteria_table)

print("  ✓ Page 1 created")

# ============================================================================
# PAGE 2: DATA COVERAGE AND STATISTICS
# ============================================================================

elements.append(PageBreak())
print("[Page 2] Creating data coverage and statistics...")

elements.append(Paragraph("DATA COVERAGE VALIDATION", heading_style))

# Data Coverage Summary
coverage_text = f"""
<b>Analysis Period:</b> {validation_info['actual_coverage_months']:.1f} months<br/>
<b>Sales Date Range:</b> {pd.to_datetime(validation_info['earliest_sale']).strftime('%B %d, %Y')} to {pd.to_datetime(validation_info['latest_sale']).strftime('%B %d, %Y')}<br/>
<b>Total Sales Analyzed:</b> {int(stats_df['N_Sales'].iloc[-1])} sales<br/>
<b>Valid Time Periods:</b> {len(validation_info['valid_periods'])} periods included<br/>
<b>Omitted Time Periods:</b> {len(validation_info['omitted_periods'])} periods (beyond data coverage)
"""
elements.append(Paragraph(coverage_text, normal_style))
elements.append(Spacer(1, 0.2*inch))

# Note box
note_text = f"""
<b>NOTE:</b> Time periods beyond {validation_info['actual_coverage_months']:.1f} months ({validation_info['omitted_periods'][0]['name'] if validation_info['omitted_periods'] else 'N/A'}, etc.) were omitted from analysis as they contain no additional sales data beyond the {validation_info['valid_periods'][-1]['name']} period. This prevents misleading redundant statistics and ensures transparent reporting of actual data depth.
"""
note_para = Paragraph(note_text, ParagraphStyle('Note', parent=normal_style, 
                                               fontSize=9, italic=True,
                                               leftIndent=20, rightIndent=20,
                                               textColor=colors.HexColor('#666666')))
elements.append(note_para)
elements.append(Spacer(1, 0.3*inch))

# Statistics Table
elements.append(Paragraph("SALES STATISTICS BY TIME PERIOD", heading_style))

stats_data = [['Period', 'N', 'Months', 'Abs Rate', 'Mean Price', 'Median Price', '$/SF Mean', '$/SF Median']]

for _, row in stats_df.iterrows():
    stats_data.append([
        row['Period'],
        int(row['N_Sales']),
        int(row['Months']),
        f"{row['Absorption_Rate']:.2f}",
        f"${row['Price_Mean']:,.0f}",
        f"${row['Price_Median']:,.0f}",
        f"${row['PriceSF_Mean']:.2f}",
        f"${row['PriceSF_Median']:.2f}"
    ])

stats_table = Table(stats_data, colWidths=[1.2*inch, 0.5*inch, 0.7*inch, 0.7*inch, 1.0*inch, 1.0*inch, 0.9*inch, 0.9*inch])
stats_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
elements.append(stats_table)

print("  ✓ Page 2 created")

# ============================================================================
# PAGE 3: MARKET TREND ANALYSIS
# ============================================================================

elements.append(PageBreak())
print("[Page 3] Creating market trend analysis...")

elements.append(Paragraph("MARKET TREND ANALYSIS", heading_style))

trend_results = validation_info['trend_results']

trend_text = f"""
<b>Market Trend Determination:</b> {trend_results['market_trend']}<br/>
<b>Monthly Price Change:</b> {trend_results['monthly_price_change_pct']:+.2f}% per month<br/>
<b>Daily Price Change:</b> ${trend_results['daily_price_change']:+.2f} per day<br/>
<b>Statistical Reliability:</b> R² = {trend_results['r_squared']:.3f}
"""
elements.append(Paragraph(trend_text, normal_style))
elements.append(Spacer(1, 0.2*inch))

# Add interpretation
if trend_results['market_trend'] == 'INCREASING':
    interpretation = "The market exhibits a positive upward trend, with sale prices increasing over the analysis period. This indicates improving market conditions and buyer demand exceeding supply."
elif trend_results['market_trend'] == 'DECREASING':
    interpretation = "The market exhibits a negative downward trend, with sale prices decreasing over the analysis period. This may indicate weakening market conditions or increased inventory levels."
elif trend_results['market_trend'] == 'STABLE':
    interpretation = "The market exhibits stable pricing with minimal directional movement. This indicates balanced market conditions with supply and demand in equilibrium."
else:
    interpretation = "The market exhibits unstable or unclear directional movement, suggesting a transitional market period."

elements.append(Paragraph(f"<b>Interpretation:</b> {interpretation}", normal_style))
elements.append(Spacer(1, 0.3*inch))

# Add Sale Price Trend Chart
try:
    img1 = Image('01_Sale_Price_Trend.png', width=6.5*inch, height=4*inch)
    elements.append(img1)
except:
    elements.append(Paragraph("[Chart: Sale Price Trend]", normal_style))

print("  ✓ Page 3 created")

# ============================================================================
# PAGE 4: COMPARABLE SALES ADJUSTMENT ANALYSIS
# ============================================================================

elements.append(PageBreak())
print("[Page 4] Creating comparable sales adjustment analysis...")

elements.append(Paragraph("COMPARABLE SALES ADJUSTMENT ANALYSIS", heading_style))

adj_text = f"""
<b>Subject Living Area:</b> {adjustment_summary['subject_living_area']:,} SF<br/>
<b>Number of Comparables:</b> {adjustment_summary['n_comparables']}<br/>
<b>Adjustment Thresholds:</b> Time = {adjustment_summary['time_threshold_days']} days, Living Area = {adjustment_summary['sf_threshold_pct']}%<br/>
<b>Market Trend Applied:</b> {trend_results['monthly_price_change_pct']:+.2f}% per month<br/>
<b>Marginal Value per SF:</b> ${adjustment_summary['marginal_value_per_sf']:.2f}/SF
"""
elements.append(Paragraph(adj_text, normal_style))
elements.append(Spacer(1, 0.2*inch))

# Adjustment Results
adj_results_data = [
    ['Metric', 'Value'],
    ['Unadjusted Median Price', f"${adjustment_summary['unadjusted_median']:,.0f}"],
    ['Adjusted Median Price', f"${adjustment_summary['adjusted_median']:,.0f}"],
    ['Net Adjustment Impact', f"${adjustment_summary['adjustment_impact']:+,.0f} ({adjustment_summary['adjustment_impact_pct']:+.2f}%)"],
    ['Time Adjustments Applied', f"{adjustment_summary['time_adjustments_applied']} of {adjustment_summary['n_comparables']}"],
    ['Living Area Adjustments Applied', f"{adjustment_summary['sf_adjustments_applied']} of {adjustment_summary['n_comparables']}"],
]

adj_results_table = Table(adj_results_data, colWidths=[3*inch, 3.5*inch])
adj_results_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#FFFF99')),  # Highlight adjusted median
]))
elements.append(adj_results_table)
elements.append(Spacer(1, 0.2*inch))

# Key Finding Box
finding_text = f"""
<b>ADJUSTED MEDIAN PRICE: ${adjustment_summary['adjusted_median']:,.0f}</b><br/><br/>
This represents the median sale price of comparable properties after adjusting for differences in sale date (time) and living area relative to the subject property. Adjustments are applied only when differences exceed professional thresholds (30 days for time, 5% for living area).
"""
finding_para = Paragraph(finding_text, ParagraphStyle('Finding', parent=normal_style,
                                                     fontSize=10, leftIndent=20, rightIndent=20,
                                                     backColor=colors.HexColor('#E6F2FF'),
                                                     borderPadding=10))
elements.append(finding_para)
elements.append(Spacer(1, 0.2*inch))

# Add Adjustment Comparison Chart
try:
    img2 = Image('08_Adjustment_Comparison.png', width=6.5*inch, height=4*inch)
    elements.append(img2)
except:
    elements.append(Paragraph("[Chart: Adjustment Comparison]", normal_style))

print("  ✓ Page 4 created")

# ============================================================================
# PAGE 5: VALUE INDICATION (BLANK FOR APPRAISER)
# ============================================================================

elements.append(PageBreak())
print("[Page 5] Creating value indication page...")

elements.append(Paragraph("VALUE INDICATION", heading_style))

indication_text = """
<b>STATISTICAL SUPPORT:</b><br/>
The comparable sales adjustment analysis provides objective statistical support for the valuation conclusion. 
The adjusted median price represents the central tendency of comparable sales after accounting for market conditions 
and physical differences.<br/><br/>

<b>APPRAISER'S RECONCILIATION:</b><br/>
While the statistical analysis provides quantitative support, the final value conclusion requires professional 
judgment considering factors including but not limited to:<br/>
• Quality and comparability of individual sales<br/>
• Neighborhood trends and market dynamics<br/>
• Property-specific characteristics not captured in adjustments<br/>
• Current market conditions and buyer motivations<br/>
• Other relevant market evidence<br/><br/>

<b>INDICATED VALUE (as of December 31, 2013):</b><br/><br/>
<u>$________________</u><br/><br/>

<i>The indicated value shall be determined by the appraiser based on reconciliation of the statistical evidence 
presented in this analysis along with other appraisal methods and professional judgment.</i>
"""

elements.append(Paragraph(indication_text, normal_style))

print("  ✓ Page 5 created")

# ============================================================================
# ADDITIONAL PAGES: CHARTS
# ============================================================================

elements.append(PageBreak())
print("[Additional Pages] Adding charts...")

elements.append(Paragraph("SUPPORTING CHARTS AND GRAPHS", heading_style))
elements.append(Spacer(1, 0.2*inch))

# Add charts
charts = [
    ('02_Price_Per_SF_Trend.png', 'Price Per Square Foot Trend'),
    ('03_Price_By_Period.png', 'Price Statistics by Time Period'),
    ('04_Absorption_Rate.png', 'Absorption Rate Analysis'),
    ('07_Living_Area_vs_Price.png', 'Living Area vs Sale Price Regression'),
]

for chart_file, chart_title in charts:
    try:
        elements.append(Paragraph(chart_title, heading_style))
        img = Image(chart_file, width=6.5*inch, height=4*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.3*inch))
    except:
        elements.append(Paragraph(f"[Chart: {chart_title}]", normal_style))
        elements.append(Spacer(1, 0.3*inch))

print("  ✓ Charts added")

# ============================================================================
# BUILD PDF
# ============================================================================

doc.build(elements)

print("\n" + "=" * 80)
print("✓ PDF REPORT CREATED SUCCESSFULLY")
print("=" * 80)
print(f"File: {pdf_file}")
print(f"Pages: 8+ (including title, statistics, trends, adjustments, and charts)")
print("=" * 80)
