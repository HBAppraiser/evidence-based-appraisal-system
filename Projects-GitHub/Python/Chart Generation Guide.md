# REAL PROPERTY MARKET ANALYSIS
# Chart Generation Guide

## CHART SPECIFICATIONS

### Common Chart Settings
```python
CHART_SETTINGS = {
    'figure_size': (12, 8),
    'dpi': 300,
    'style': 'seaborn',
    'colors': {
        'primary': '#1f77b4',  # Blue for data points
        'trend': 'black',      # Black for trend lines
        'poly': '#d62728',     # Red for polynomial
        'highlight': '#2ca02c'  # Green for highlights
    },
    'font': {
        'family': 'Arial',
        'size': 10,
        'title_size': 12,
        'label_size': 10
    },
    'grid': {
        'alpha': 0.3,
        'style': '--'
    }
}

# Set global style
plt.style.use(CHART_SETTINGS['style'])
```

### Chart Generation Functions

1. **Price Trend Charts**
```python
def create_price_trend_charts(df, valid_periods, date_of_value, 
                            output_dir):
    """
    Create price and price/SF trend charts for valid periods
    
    Parameters:
    df: DataFrame with sales data
    valid_periods: List of valid analysis periods
    date_of_value: Analysis date
    output_dir: Directory for output files
    """
    for period in valid_periods:
        months = period['months']
        start_date = period['start_date']
        
        # Price trend chart
        fig = create_price_trend_chart(
            df, 'sale_price',
            f'{months}-Month Sale Price Trend',
            start_date, date_of_value
        )
        fig.savefig(
            f'{output_dir}/price_trend_{months}mo.png',
            dpi=CHART_SETTINGS['dpi'],
            bbox_inches='tight'
        )
        plt.close(fig)
        
        # Price per SF trend chart
        df['price_sf'] = df['sale_price'] / df['living_area']
        fig = create_price_trend_chart(
            df, 'price_sf',
            f'{months}-Month Price per SF Trend',
            start_date, date_of_value
        )
        fig.savefig(
            f'{output_dir}/price_sf_trend_{months}mo.png',
            dpi=CHART_SETTINGS['dpi'],
            bbox_inches='tight'
        )
        plt.close(fig)
```

2. **Distribution Charts**
```python
def create_distribution_charts(df, output_dir):
    """
    Create price and price/SF distribution charts
    
    Parameters:
    df: DataFrame with sales data
    output_dir: Directory for output files
    """
    # Price distribution
    fig, ax = plt.subplots(figsize=CHART_SETTINGS['figure_size'])
    
    # Calculate optimal bins using Freedman-Diaconis rule
    prices = df['sale_price']
    iqr = prices.quantile(0.75) - prices.quantile(0.25)
    bin_width = 2 * iqr / (len(prices) ** (1/3))
    bins = int((prices.max() - prices.min()) / bin_width)
    
    # Create histogram
    n, bins, patches = ax.hist(
        prices, bins=bins,
        color=CHART_SETTINGS['colors']['primary'],
        alpha=0.7
    )
    
    # Add normal distribution curve
    mu = prices.mean()
    sigma = prices.std()
    x = np.linspace(prices.min(), prices.max(), 100)
    y = norm.pdf(x, mu, sigma) * len(prices) * bin_width
    ax.plot(x, y, 'r-', lw=2)
    
    # Add mean and median lines
    ax.axvline(mu, color='r', linestyle='--', alpha=0.8)
    ax.axvline(prices.median(), color='g', linestyle='--', alpha=0.8)
    
    # Add count labels on bars
    for i in range(len(n)):
        if n[i] > 0:
            ax.text(
                bins[i] + (bins[i+1]-bins[i])/2,
                n[i],
                int(n[i]),
                ha='center', va='bottom'
            )
    
    # Formatting
    ax.set_title('Sale Price Distribution')
    ax.set_xlabel('Sale Price ($)')
    ax.set_ylabel('Count')
    ax.grid(True, alpha=CHART_SETTINGS['grid']['alpha'])
    
    # Format x-axis with dollar signs
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    fig.savefig(
        f'{output_dir}/price_distribution.png',
        dpi=CHART_SETTINGS['dpi'],
        bbox_inches='tight'
    )
    plt.close(fig)
    
    # Repeat for Price per SF
    # [Similar code for price/SF distribution]
```

3. **Comparable Sales Adjustment Chart**
```python
def create_adjustment_chart(comp_analysis, output_dir):
    """
    Create comparable sales adjustment visualization
    
    Parameters:
    comp_analysis: DataFrame with comparable analysis
    output_dir: Directory for output files
    """
    fig, ax = plt.subplots(figsize=CHART_SETTINGS['figure_size'])
    
    # Set up data
    comps = comp_analysis.sort_values('sale_price')
    x = range(len(comps))
    
    # Create grouped bars
    width = 0.35
    ax.bar(
        [i - width/2 for i in x],
        comps['sale_price'],
        width,
        label='Original Price',
        color=CHART_SETTINGS['colors']['primary']
    )
    ax.bar(
        [i + width/2 for i in x],
        comps['adjusted_price'],
        width,
        label='Adjusted Price',
        color=CHART_SETTINGS['colors']['highlight']
    )
    
    # Add median lines
    ax.axhline(
        comps['sale_price'].median(),
        color=CHART_SETTINGS['colors']['primary'],
        linestyle='--',
        alpha=0.8
    )
    ax.axhline(
        comps['adjusted_price'].median(),
        color=CHART_SETTINGS['colors']['highlight'],
        linestyle='--',
        alpha=0.8
    )
    
    # Formatting
    ax.set_title('Comparable Sales Adjustments')
    ax.set_xlabel('Comparable Properties')
    ax.set_ylabel('Price ($)')
    ax.set_xticks(x)
    ax.set_xticklabels([f'Comp {i+1}' for i in x])
    
    # Format y-axis with dollar signs
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    ax.grid(True, alpha=CHART_SETTINGS['grid']['alpha'])
    ax.legend()
    
    plt.tight_layout()
    fig.savefig(
        f'{output_dir}/comparable_adjustments.png',
        dpi=CHART_SETTINGS['dpi'],
        bbox_inches='tight'
    )
    plt.close(fig)
```

[Additional chart functions continue...]