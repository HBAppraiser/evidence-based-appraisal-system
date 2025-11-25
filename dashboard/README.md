# Streamlit Dashboard

Additional Python dependency for interactive web dashboard:

```bash
pip install streamlit
```

## Running the Dashboard

```bash
# From project root directory
streamlit run dashboard/streamlit_dashboard.py
```

The dashboard will open automatically in your default web browser at `http://localhost:8501`

## Features

### Interactive Analysis
- **Real-time data upload** - Drag and drop CSV files
- **Dynamic filtering** - Adjust parameters with sliders
- **Live calculations** - Instant regression and statistics
- **Responsive charts** - Zoom, pan, and download

### Five Analysis Tabs

1. **📊 Trend Analysis**
   - Sale price trend with linear regression
   - R² value, daily/monthly price changes
   - Market direction indicator

2. **📉 Distributions**
   - Sale price histogram with mean/median
   - Price per SF histogram
   - Subject property positioning

3. **🔍 Scatter Analysis**
   - Living area vs sale price
   - Regression equation and marginal $/SF
   - Subject property marker

4. **📋 Data Table**
   - Sortable, searchable sales data
   - Column filtering
   - CSV download

5. **🤖 ML Prediction**
   - Random Forest model
   - Feature importance chart
   - Value comparison

### Configuration Sidebar

- Upload CSV file
- Subject property details (address, SF, BR, BA)
- Analysis parameters (date range, filters)
- Appraiser information

## Deployment Options

### Local (Desktop)
```bash
streamlit run dashboard/streamlit_dashboard.py
```

### Network (Share on LAN)
```bash
streamlit run dashboard/streamlit_dashboard.py --server.address=0.0.0.0
```
Access from other computers: `http://YOUR_IP:8501`

### Cloud (Streamlit Cloud - Free)
1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Deploy in 1 click
5. Get public URL: `https://your-app.streamlit.app`

### Docker
```bash
docker build -t appraisal-dashboard .
docker run -p 8501:8501 appraisal-dashboard
```

## Usage Examples

### Basic Workflow
1. Launch dashboard: `streamlit run dashboard/streamlit_dashboard.py`
2. Upload CSV file (drag and drop)
3. Configure subject property in sidebar
4. Explore tabs for different analyses
5. Download results

### Sharing with Clients
1. Deploy to Streamlit Cloud (free)
2. Get public URL
3. Share link with clients
4. They can upload their own data
5. No installation required

### Batch Analysis
1. Upload multiple CSV files (one at a time)
2. Adjust parameters between runs
3. Download results for each property
4. Compare across properties

## Customization

Edit `streamlit_dashboard.py` to:
- Change color schemes
- Add custom charts
- Modify filters
- Add new analysis tabs
- Integrate with databases

## Troubleshooting

### Port already in use
```bash
streamlit run dashboard/streamlit_dashboard.py --server.port=8502
```

### Module not found
```bash
pip install streamlit matplotlib seaborn scipy scikit-learn pandas numpy
```

### Charts not displaying
- Ensure matplotlib backend is correct
- Try clearing Streamlit cache: `streamlit cache clear`

### CSV upload fails
- Check file encoding (UTF-8 recommended)
- Verify column headers exist
- Test with `data/test_small.csv` first

## Performance Tips

- Keep CSV files under 50MB for best performance
- Use date range filters to limit data
- Deploy to Streamlit Cloud for faster loading
- Enable caching for repeated calculations

## Security Notes

When deploying publicly:
- Remove client-specific default values
- Add authentication if needed
- Use environment variables for sensitive data
- Enable HTTPS in production

## Mobile Responsive

The dashboard is mobile-friendly:
- ✅ Works on phones and tablets
- ✅ Responsive layout adjusts automatically
- ✅ Touch-friendly controls
- ✅ Optimized for smaller screens
