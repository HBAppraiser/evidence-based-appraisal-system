# ADDITIONAL VISUALIZATION TYPES

## Box Plots and Categorical Analysis

```python
def create_box_plots(df: pd.DataFrame, output_dir: str):
    """Create box plots for categorical comparisons"""
    
    # Price by Property Type
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sns.boxplot(data=df, x='property_type', y='sale_price', ax=ax)
    
    # Add sample sizes
    for i, pt in enumerate(df['property_type'].unique()):
        n = len(df[df['property_type'] == pt])
        ax.text(i, ax.get_ylim()[0], f'n={n}', 
                ha='center', va='top')
    
    ax.set_title('Sale Price Distribution by Property Type')
    ax.set_ylabel('Sale Price ($)')
    plt.xticks(rotation=45)
    
    # Format y-axis with dollar signs
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/price_by_type_box.png')
    plt.close()

## Time Series Analysis

def create_time_series_charts(df: pd.DataFrame, output_dir: str):
    """Create time series analysis charts"""
    
    # Monthly Median Prices
    monthly = df.set_index('sale_date').resample('M').agg({
        'sale_price': 'median',
        'sale_date': 'count'
    }).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Price Trend
    ax1.plot(monthly['sale_date'], monthly['sale_price'], 
             marker='o', linewidth=2)
    ax1.set_title('Monthly Median Sale Price')
    ax1.set_ylabel('Price ($)')
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Sales Volume
    ax2.bar(monthly['sale_date'], monthly['sale_date'], 
            width=20, alpha=0.7)
    ax2.set_title('Monthly Sales Volume')
    ax2.set_ylabel('Number of Sales')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/monthly_trends.png')
    plt.close()

## Market Balance Indicators

def create_market_indicators(df: pd.DataFrame, output_dir: str):
    """Create market balance indicator charts"""
    
    # List Price to Sale Price Ratio
    df['list_sale_ratio'] = df['sale_price'] / df['list_price'] * 100
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Scatter plot of ratios over time
    ax.scatter(df['sale_date'], df['list_sale_ratio'], 
              alpha=0.5)
    
    # Add trend line
    z = np.polyfit(
        (df['sale_date'] - df['sale_date'].min()).dt.days, 
        df['list_sale_ratio'], 
        1
    )
    p = np.poly1d(z)
    x_trend = [df['sale_date'].min(), df['sale_date'].max()]
    y_trend = p([(d - df['sale_date'].min()).days 
                 for d in x_trend])
    ax.plot(x_trend, y_trend, 'r--', linewidth=2)
    
    # Add 100% reference line
    ax.axhline(y=100, color='k', linestyle='-', alpha=0.3)
    
    ax.set_title('List Price to Sale Price Ratio Trend')
    ax.set_ylabel('List/Sale Ratio (%)')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/price_ratio_trend.png')
    plt.close()

## Interactive Visualizations

def create_interactive_dashboard(df: pd.DataFrame, output_dir: str):
    """Create interactive HTML dashboard"""
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Price Trend',
            'Price Distribution',
            'Geographic Distribution',
            'Market Balance'
        )
    )
    
    # Price Trend
    fig.add_trace(
        go.Scatter(
            x=df['sale_date'],
            y=df['sale_price'],
            mode='markers',
            name='Sales'
        ),
        row=1, col=1
    )
    
    # Price Distribution
    fig.add_trace(
        go.Histogram(
            x=df['sale_price'],
            name='Price Distribution'
        ),
        row=1, col=2
    )
    
    # Geographic Distribution
    fig.add_trace(
        go.Scattermapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=9,
                color=df['sale_price'],
                colorscale='Viridis',
                showscale=True
            ),
            text=df['address'],
            name='Sale Locations'
        ),
        row=2, col=1
    )
    
    # Market Balance
    fig.add_trace(
        go.Scatter(
            x=df['sale_date'],
            y=df['list_sale_ratio'],
            mode='markers',
            name='List/Sale Ratio'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=1000,
        title_text="Interactive Market Analysis Dashboard",
        showlegend=True
    )
    
    # Save to HTML
    fig.write_html(f'{output_dir}/interactive_dashboard.html')
```