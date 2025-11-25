"""
Streamlit Dashboard for Evidence-Based Appraisal Analysis
Interactive web-based interface for real estate market analysis

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime, timedelta
import json
import os

# Page configuration
st.set_page_config(
    page_title="Evidence-Based Appraisal Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #2c3e50;
    }
    .stAlert {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Title
st.title("🏠 Evidence-Based Appraisal Dashboard")
st.markdown("**Statistical Market Analysis & Visualization Platform**")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload MLS CSV Data",
        type=['csv'],
        help="Upload your MLS export file with sales data"
    )
    
    st.markdown("---")
    
    # Subject Property Details
    st.subheader("🏡 Subject Property")
    
    subject_address = st.text_input("Address", "528 S Taper Ave")
    subject_city = st.text_input("City", "Compton")
    subject_state = st.text_input("State", "CA")
    subject_zip = st.text_input("ZIP", "90220")
    
    col1, col2 = st.columns(2)
    with col1:
        subject_living_area = st.number_input("Living Area (SF)", min_value=100, max_value=10000, value=951)
        subject_bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=2)
    with col2:
        subject_bathrooms = st.number_input("Bathrooms", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
        subject_year_built = st.number_input("Year Built", min_value=1800, max_value=2025, value=1950)
    
    subject_value_estimate = st.number_input(
        "Estimated Value ($)",
        min_value=0,
        max_value=10000000,
        value=250000,
        step=10000,
        format="%d"
    )
    
    st.markdown("---")
    
    # Analysis Parameters
    st.subheader("📊 Analysis Parameters")
    
    effective_date = st.date_input(
        "Effective Date",
        value=datetime.now()
    )
    
    max_days_old = st.slider(
        "Maximum Days Old",
        min_value=30,
        max_value=365,
        value=180,
        help="Maximum age of comparable sales to include"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        min_living_area = st.number_input("Min Living Area (SF)", min_value=0, max_value=5000, value=700)
        min_bedrooms = st.number_input("Min Bedrooms", min_value=1, max_value=10, value=2)
    with col2:
        max_living_area = st.number_input("Max Living Area (SF)", min_value=500, max_value=20000, value=1500)
        max_bedrooms = st.number_input("Max Bedrooms", min_value=1, max_value=10, value=4)
    
    st.markdown("---")
    
    # Appraiser Info
    st.subheader("👤 Appraiser Information")
    appraiser_name = st.text_input("Appraiser Name", "Craig Gilbert")
    file_number = st.text_input("File Number", "25-060_2025")
    client_name = st.text_input("Client Name", "Katherine Hinton, esq")

# Main content area
if uploaded_file is not None:
    # Load data
    try:
        df = pd.read_csv(uploaded_file)
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Detect date and price columns
        date_cols = [col for col in df.columns if any(x in col for x in ['close', 'sale', 'date'])]
        price_cols = [col for col in df.columns if any(x in col for x in ['close', 'sale', 'price']) and 'per' not in col]
        area_cols = [col for col in df.columns if any(x in col for x in ['living', 'area', 'gla', 'sqft'])]
        
        if date_cols and price_cols and area_cols:
            # Parse dates
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
            # Filter data
            df_filtered = df[
                (df[date_cols[0]].notna()) &
                (df[price_cols[0]].notna()) &
                (df[area_cols[0]].notna()) &
                (df[price_cols[0]] > 0) &
                (df[area_cols[0]] > 0)
            ].copy()
            
            # Calculate days from effective date
            df_filtered['days_from_effective'] = (pd.to_datetime(effective_date) - df_filtered[date_cols[0]]).dt.days
            
            # Apply filters
            df_filtered = df_filtered[
                (df_filtered['days_from_effective'] >= 0) &
                (df_filtered['days_from_effective'] <= max_days_old) &
                (df_filtered[area_cols[0]] >= min_living_area) &
                (df_filtered[area_cols[0]] <= max_living_area)
            ]
            
            # Calculate price per SF
            df_filtered['price_per_sf'] = df_filtered[price_cols[0]] / df_filtered[area_cols[0]]
            
            st.session_state.data = df_filtered
            
            # Display summary metrics
            st.header("📈 Market Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sales", len(df_filtered))
            
            with col2:
                median_price = df_filtered[price_cols[0]].median()
                st.metric("Median Sale Price", f"${median_price:,.0f}")
            
            with col3:
                median_psf = df_filtered['price_per_sf'].median()
                st.metric("Median Price/SF", f"${median_psf:.2f}")
            
            with col4:
                coverage_months = df_filtered['days_from_effective'].max() / 30.44
                st.metric("Data Coverage", f"{coverage_months:.1f} months")
            
            st.markdown("---")
            
            # Tabs for different analyses
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Trend Analysis",
                "📉 Distributions",
                "🔍 Scatter Analysis",
                "📋 Data Table",
                "🤖 ML Prediction"
            ])
            
            with tab1:
                st.subheader("Price Trend Analysis")
                
                # Calculate linear regression
                x = df_filtered['days_from_effective'].values
                y = df_filtered[price_cols[0]].values
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                line = slope * x + intercept
                
                daily_change = -slope
                monthly_change_pct = (daily_change * 30.44 / y.mean()) * 100
                
                # Display trend metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("R² Value", f"{r_value**2:.4f}")
                with col2:
                    st.metric("Daily Change", f"${daily_change:.2f}")
                with col3:
                    trend_direction = "📈 INCREASING" if daily_change > 0 else "📉 DECREASING" if daily_change < 0 else "➡️ STABLE"
                    st.metric("Market Trend", trend_direction)
                
                # Plot
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.scatter(df_filtered[date_cols[0]], df_filtered[price_cols[0]], 
                          alpha=0.6, s=100, c='#3498db', edgecolors='black', linewidth=0.5)
                ax.plot(df_filtered[date_cols[0]], line, 'r-', linewidth=2, label='Trend Line')
                
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.set_xlabel('Sale Date', fontsize=12, fontweight='bold')
                ax.set_ylabel('Sale Price', fontsize=12, fontweight='bold')
                ax.set_title('Sale Price Trend with Linear Regression', fontsize=14, fontweight='bold')
                
                # Add stats box
                stats_text = f'R² = {r_value**2:.4f}\n'
                stats_text += f'Daily Change: ${daily_change:.2f}\n'
                stats_text += f'Monthly Trend: {monthly_change_pct:+.2f}%\n'
                stats_text += f'N = {len(df_filtered)}'
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                ax.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                # Store results
                st.session_state.analysis_results['trend'] = {
                    'r_squared': r_value**2,
                    'daily_change': daily_change,
                    'monthly_change_pct': monthly_change_pct,
                    'slope': slope,
                    'intercept': intercept
                }
            
            with tab2:
                st.subheader("Price Distributions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sale Price Distribution
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.hist(df_filtered[price_cols[0]], bins=15, color='#3498db', alpha=0.7, edgecolor='black')
                    
                    mean_price = df_filtered[price_cols[0]].mean()
                    median_price = df_filtered[price_cols[0]].median()
                    
                    ax.axvline(mean_price, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_price:,.0f}')
                    ax.axvline(median_price, color='green', linestyle='--', linewidth=2, label=f'Median: ${median_price:,.0f}')
                    ax.axvline(subject_value_estimate, color='orange', linestyle=':', linewidth=2.5, label=f'Subject: ${subject_value_estimate:,.0f}')
                    
                    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                    ax.set_xlabel('Sale Price', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
                    ax.set_title('Sale Price Distribution', fontsize=14, fontweight='bold')
                    ax.legend()
                    ax.grid(True, alpha=0.3, axis='y')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                
                with col2:
                    # Price Per SF Distribution
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.hist(df_filtered['price_per_sf'], bins=15, color='#2ecc71', alpha=0.7, edgecolor='black')
                    
                    mean_psf = df_filtered['price_per_sf'].mean()
                    median_psf = df_filtered['price_per_sf'].median()
                    subject_psf = subject_value_estimate / subject_living_area
                    
                    ax.axvline(mean_psf, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_psf:.2f}')
                    ax.axvline(median_psf, color='green', linestyle='--', linewidth=2, label=f'Median: ${median_psf:.2f}')
                    ax.axvline(subject_psf, color='orange', linestyle=':', linewidth=2.5, label=f'Subject: ${subject_psf:.2f}')
                    
                    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))
                    ax.set_xlabel('Price per SF', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
                    ax.set_title('Price Per SF Distribution', fontsize=14, fontweight='bold')
                    ax.legend()
                    ax.grid(True, alpha=0.3, axis='y')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
            
            with tab3:
                st.subheader("Living Area vs Sale Price")
                
                # Regression
                x_area = df_filtered[area_cols[0]].values
                y_price = df_filtered[price_cols[0]].values
                slope_area, intercept_area, r_value_area, _, _ = stats.linregress(x_area, y_price)
                line_area = slope_area * x_area + intercept_area
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.scatter(df_filtered[area_cols[0]], df_filtered[price_cols[0]],
                          alpha=0.6, s=100, c='#9b59b6', edgecolors='black', linewidth=0.5)
                ax.plot(df_filtered[area_cols[0]], line_area, 'r-', linewidth=2, label='Regression Line')
                
                # Add subject
                ax.scatter([subject_living_area], [subject_value_estimate],
                          s=300, c='orange', marker='*', edgecolors='black', linewidth=2,
                          label='Subject Property', zorder=5)
                
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
                ax.grid(True, alpha=0.3)
                ax.set_xlabel('Living Area (SF)', fontsize=12, fontweight='bold')
                ax.set_ylabel('Sale Price', fontsize=12, fontweight='bold')
                ax.set_title('Living Area vs Sale Price with Linear Regression', fontsize=14, fontweight='bold')
                
                # Stats box
                stats_text = f'Regression Equation:\n'
                stats_text += f'Price = ${intercept_area:,.0f} + ${slope_area:.2f} × SF\n\n'
                stats_text += f'R² = {r_value_area**2:.4f}\n'
                stats_text += f'Marginal Value: ${slope_area:.2f}/SF\n'
                stats_text += f'N = {len(df_filtered)}'
                
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                ax.legend()
                plt.tight_layout()
                st.pyplot(fig)
                
                # Display regression metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("R² Value", f"{r_value_area**2:.4f}")
                with col2:
                    st.metric("Marginal Value ($/SF)", f"${slope_area:.2f}")
                with col3:
                    st.metric("Base Value", f"${intercept_area:,.0f}")
            
            with tab4:
                st.subheader("Sales Data Table")
                
                # Display options
                col1, col2 = st.columns([3, 1])
                with col1:
                    search = st.text_input("🔍 Search", "")
                with col2:
                    show_rows = st.selectbox("Show rows", [10, 25, 50, 100, "All"])
                
                # Filter by search
                display_df = df_filtered.copy()
                if search:
                    display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
                
                # Select columns to display
                display_cols = [date_cols[0], price_cols[0], area_cols[0], 'price_per_sf', 'days_from_effective']
                if 'bedrooms' in df_filtered.columns:
                    display_cols.append('bedrooms')
                if 'bathrooms' in df_filtered.columns:
                    display_cols.append('bathrooms')
                
                display_df = display_df[display_cols]
                
                # Rename for display
                display_df = display_df.rename(columns={
                    date_cols[0]: 'Sale Date',
                    price_cols[0]: 'Sale Price',
                    area_cols[0]: 'Living Area',
                    'price_per_sf': 'Price/SF',
                    'days_from_effective': 'Days Old'
                })
                
                # Show data
                if show_rows == "All":
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.dataframe(display_df.head(int(show_rows)), use_container_width=True)
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"market_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with tab5:
                st.subheader("Machine Learning Prediction")
                
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.model_selection import train_test_split
                
                # Prepare features
                feature_cols = [area_cols[0], 'days_from_effective']
                if 'bedrooms' in df_filtered.columns:
                    feature_cols.append('bedrooms')
                if 'bathrooms' in df_filtered.columns:
                    feature_cols.append('bathrooms')
                
                ml_data = df_filtered[feature_cols + [price_cols[0]]].dropna()
                
                if len(ml_data) >= 10:
                    X = ml_data[feature_cols]
                    y = ml_data[price_cols[0]]
                    
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
                    rf_model.fit(X_train, y_train)
                    
                    train_score = rf_model.score(X_train, y_train)
                    test_score = rf_model.score(X_test, y_test)
                    
                    # Predict subject value
                    subject_features = pd.DataFrame({
                        area_cols[0]: [subject_living_area],
                        'days_from_effective': [0]
                    })
                    
                    if 'bedrooms' in feature_cols:
                        subject_features['bedrooms'] = subject_bedrooms
                    if 'bathrooms' in feature_cols:
                        subject_features['bathrooms'] = subject_bathrooms
                    
                    rf_prediction = rf_model.predict(subject_features)[0]
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Training R²", f"{train_score:.4f}")
                    with col2:
                        st.metric("Testing R²", f"{test_score:.4f}")
                    with col3:
                        st.metric("ML Prediction", f"${rf_prediction:,.0f}")
                    
                    # Feature importance
                    st.subheader("Feature Importance")
                    feature_importance = pd.DataFrame({
                        'Feature': feature_cols,
                        'Importance': rf_model.feature_importances_
                    }).sort_values('Importance', ascending=False)
                    
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.barh(feature_importance['Feature'], feature_importance['Importance'], color='#3498db')
                    ax.set_xlabel('Importance', fontsize=12, fontweight='bold')
                    ax.set_title('Feature Importance in Random Forest Model', fontsize=14, fontweight='bold')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Comparison
                    st.subheader("Value Comparison")
                    comparison_df = pd.DataFrame({
                        'Method': ['ML Prediction', 'Appraiser Opinion', 'Difference'],
                        'Value': [
                            f"${rf_prediction:,.0f}",
                            f"${subject_value_estimate:,.0f}",
                            f"${abs(rf_prediction - subject_value_estimate):,.0f} ({abs(rf_prediction - subject_value_estimate) / subject_value_estimate * 100:.2f}%)"
                        ]
                    })
                    st.table(comparison_df)
                else:
                    st.warning("Insufficient data for machine learning analysis (need at least 10 sales)")
            
        else:
            st.error("Could not detect required columns. Please ensure CSV has date, price, and living area columns.")
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the CSV file is properly formatted.")

else:
    # Show welcome message
    st.info("👈 Please upload a CSV file in the sidebar to begin analysis")
    
    st.markdown("""
    ### Welcome to the Evidence-Based Appraisal Dashboard
    
    This interactive platform provides:
    
    - 📊 **Trend Analysis** - Linear regression with R² and market direction
    - 📉 **Distribution Analysis** - Histograms with subject positioning
    - 🔍 **Scatter Analysis** - Living area vs price with marginal values
    - 📋 **Data Table** - Sortable, searchable, downloadable sales data
    - 🤖 **ML Prediction** - Random Forest validation with feature importance
    
    #### Getting Started
    
    1. Upload your MLS CSV file (left sidebar)
    2. Configure subject property details
    3. Set analysis parameters
    4. Explore the interactive charts and tables
    5. Download results for your report
    
    #### Required CSV Columns
    
    Your CSV should include:
    - Sale/Close Date
    - Sale/Close Price
    - Living Area (SF)
    - Bedrooms (optional)
    - Bathrooms (optional)
    
    The system will auto-detect column names.
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>Evidence-Based Appraisal System v1.0 | 
        Built with Streamlit | 
        © 2025 Craig Gilbert</p>
    </div>
    """, unsafe_allow_html=True)
