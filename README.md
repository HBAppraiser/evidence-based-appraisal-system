# Evidence-Based Appraisal System

**A hybrid R + Python statistical analysis platform for residential real estate appraisals**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![R 4.0+](https://img.shields.io/badge/R-4.0+-blue.svg)](https://www.r-project.org/)

## 📋 Overview

This system integrates **Evidence-Based Valuation (EBV)** methodology with professional appraisal reporting, combining the statistical power of R and Python into unified Quarto Markdown templates.

**Key Features:**
- 📊 **Population-based analysis** - Analyze entire market, not just 3-4 comparables
- 📈 **7 Professional charts** with linear regression and statistical annotations
- 🤖 **Machine Learning validation** using Random Forest
- 📝 **Narrative reports** (no adjustment grids) with USPAP compliance
- 🔄 **Form-driven workflow** - No hardcoded values, all JSON-configured
- 🎨 **Interactive GUI** - Tkinter file picker and data entry forms

## 🏗️ Project Structure

```
Evidence-Based-Appraisal-System/
├── templates/
│   ├── Evidence_Based_Appraisal_Report.qmd    # Main narrative template
│   ├── Hybrid_Appraisal_Report.qmd             # Alternative hybrid version
│   └── 01-Hybrid-Wrangle.qmd                   # Educational R↔Python example
│
├── python/
│   ├── market_analysis_v2.3.3.py               # Main analysis engine (300+ lines)
│   ├── generate_charts.py                      # 7 professional charts (320 lines)
│   ├── adjustment_analysis.py                  # Time/area adjustments (262 lines)
│   ├── simple_appraiser_v7_1.py                # Simple mode with GUI (170 lines)
│   ├── create_excel.py                         # Excel workbook generator (434 lines)
│   ├── create_pdf.py                           # PDF report generator (394 lines)
│   ├── Run_Integrated_Analysis.py              # Main orchestrator
│   └── csv_picker.py                           # Tkinter file picker
│
├── config/
│   ├── market_analysis_inputs.json             # User configuration
│   ├── market_analysis_inputs_example.json     # Template
│   └── validation_info.json                    # Trend analysis results
│
├── data/
│   ├── sales_data_processed.csv                # Processed sales
│   ├── statistics_summary.csv                  # Period statistics
│   └── test_small.csv                          # Test data
│
├── docs/
│   ├── Chart_Generation_Guide.md               # Chart specifications
│   ├── Statistical_Analysis_Guide.md           # Statistical methods
│   ├── PROMPT_Residential_Analysis.md          # Implementation guide
│   └── extracted_reports/                      # Reference PDFs (text)
│
├── batch/
│   ├── Run_Analysis.bat                        # Windows: Run analysis
│   └── Open_Form.bat                           # Windows: Open HTML form
│
├── requirements.txt                            # Python dependencies
└── README.md                                   # This file
```

## 🚀 Quick Start

### Prerequisites

**Python 3.8+** with packages:
```bash
pip install -r requirements.txt
```

**R 4.0+** with packages:
```r
install.packages(c("tidyverse", "ggplot2", "gt", "reticulate", 
                   "lubridate", "scales", "jsonlite", "ggthemes"))
```

**Quarto** (for rendering reports):
```bash
# Download from: https://quarto.org/docs/get-started/
```

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/evidence-based-appraisal-system.git
cd evidence-based-appraisal-system

# Install Python dependencies
pip install -r requirements.txt

# Install R packages
Rscript -e "install.packages(c('tidyverse', 'ggplot2', 'gt', 'reticulate'))"
```

### Usage

#### Method 1: Integrated Workflow (Recommended)

1. **Run the integrated pipeline:**
   ```bash
   python python/Run_Integrated_Analysis.py
   ```

2. **Fill out the HTML form** that opens in your browser with:
   - Subject property details (address, SF, bedrooms, bathrooms)
   - MLS CSV file path
   - Client information
   - Analysis parameters

3. **Submit form** - Pipeline automatically runs:
   - Market analysis with trend detection
   - Adjustment analysis (time + living area)
   - 7 professional charts generation
   - Excel workbook creation
   - PDF report generation

4. **Render Quarto report:**
   ```bash
   quarto render templates/Evidence_Based_Appraisal_Report.qmd
   ```

#### Method 2: Simple Mode (GUI)

```bash
python python/simple_appraiser_v7_1.py
```

- Tkinter GUI opens
- Select CSV file
- Auto-detects columns
- Generates basic statistics Excel report

#### Method 3: Manual Quarto Only

1. **Edit parameters** in `Evidence_Based_Appraisal_Report.qmd` YAML header
2. **Place CSV** in `data/` folder
3. **Render:**
   ```bash
   quarto render templates/Evidence_Based_Appraisal_Report.qmd --to html
   quarto render templates/Evidence_Based_Appraisal_Report.qmd --to pdf
   ```

## 📊 The 7 Professional Charts

1. **Sale Price Trend** - Linear regression with R², daily/monthly price change
2. **Price Per SF Trend** - Time series with trend line
3. **Sale Price Distribution** - Histogram with mean/median/subject markers
4. **Price Per SF Distribution** - Histogram with statistics
5. **Living Area vs Price Scatter** - Regression equation, marginal $/SF value
6. **Living Area Distribution** - Subject positioning
7. **Monthly Absorption Rate** - Sales volume bar chart

All charts include:
- 300 DPI resolution (publication quality)
- Professional styling (seaborn-v0_8-whitegrid)
- Currency formatting on axes
- Statistical annotations (R², equations, N-count)
- Subject property markers

## 🔧 Configuration

### JSON Configuration File

`config/market_analysis_inputs.json`:
```json
{
  "project_name": "528 S Taper Ave, Compton CA 90220",
  "file_number": "25-060_2025",
  "appraiser_name": "Craig Gilbert",
  "effective_date": "2025-11-01",
  "subject_address": "528 S Taper Ave",
  "subject_gla": "951",
  "subject_bedrooms": "2",
  "subject_bathrooms": "1",
  "csv_path": "2025 Sold data for Stats_Full (30).csv",
  "adjustment_threshold": "15",
  "include_charts": true,
  "create_pdf": true
}
```

### Quarto YAML Parameters

```yaml
params:
  Address: "528 S Taper Ave"
  LivingArea: 951
  Bedrooms: 2
  Bathrooms: 1
  EstimatedValue: 250000
  DataFile: "sales_data.csv"
```

## 📈 Evidence-Based Valuation (EBV)

This methodology, pioneered by Kyle Pacquin, emphasizes:

### Traditional Approach (Sales Comparison)
- Select 3-4 "comparable" sales
- Make subjective adjustments in grid
- Average adjusted values
- **Problem:** Cherry-picking, subjective adjustments

### Evidence-Based Approach (EBV)
- Analyze **entire market population** (all sales)
- Statistical trend quantification (linear regression)
- Transparent data coverage metrics
- Visual analytics for clear communication
- Machine learning validation
- **Result:** Objective, defensible, statistically rigorous

## 🧮 Statistical Methods

- **Linear Regression** - OLS for price trends over time
- **Correlation Analysis** - R² for relationship strength
- **Distribution Analysis** - Histograms, box plots, summary stats
- **Time Series** - Monthly absorption, trend identification
- **Machine Learning** - Random Forest with feature importance

## 🎯 Workflow Architecture

```
┌─────────────────┐
│  HTML Form      │  User fills property details
│  (Browser)      │
└────────┬────────┘
         │ Generates
         ▼
┌─────────────────────────┐
│  market_analysis_       │  All parameters
│  inputs.json            │  (no hardcoded values)
└────────┬────────────────┘
         │ Read by
         ▼
┌─────────────────────────┐
│  Run_Integrated_        │  Orchestrates pipeline:
│  Analysis.py            │  1. Market analysis
└────────┬────────────────┘  2. Adjustments
         │                   3. Charts
         │                   4. Excel
         │                   5. PDF
         ▼
┌─────────────────────────┐
│  validation_info.json   │  Trend results:
│                         │  - R² = 0.93
└────────┬────────────────┘  - Monthly trend: +1.82%
         │                   - Daily change: $152.45
         │                   - Market: INCREASING
         ▼
┌─────────────────────────┐
│  Evidence_Based_        │  Reads JSON configs
│  Appraisal_Report.qmd   │  Generates narrative
└────────┬────────────────┘  with 7 charts
         │
         ▼
┌─────────────────────────┐
│  Final HTML/PDF Report  │  Professional deliverable
└─────────────────────────┘
```

## 📝 Methodologies Integrated

### 1. Bruce Hahn - R Parameterized Reports
- Quarto YAML parameters
- Tidyverse data manipulation
- ggplot2 visualizations
- gt tables

### 2. Kyle Pacquin - Evidence-Based Valuation
- Population-based analysis
- Statistical rigor
- Transparent data coverage
- Visual analytics

### 3. John Fariss - Visual Market Analytics
- Professional chart styling
- Regression annotations
- Subject positioning markers

### 4. Craig Gilbert - Python Automation
- Form-driven configuration
- Automated chart generation
- Multi-format output (Excel, PDF)
- Data validation pipelines

## 🖥️ GUI Components

### Tkinter File Picker (`csv_picker.py`)
```python
# Simple file selection dialog
python python/csv_picker.py
```

### Simple Appraiser GUI (`simple_appraiser_v7_1.py`)
- File selection button
- Auto-column detection
- Statistics computation
- Excel export

### HTML Form (Integrated Mode)
- 7 sections: Subject, Filters, Client, Analysis
- Browser-based (no installation)
- JSON generation on submit

## 📦 Output Files

### Excel Workbook (`create_excel.py`)
- **Summary Report** - Key statistics, trends
- **Statistics by Period** - 0-1mo, 1-2mo, etc.
- **Adjustment Analysis** - Time + Living Area adjustments
- **Raw Data** - All sales with calculated fields

### PDF Report (`create_pdf.py`)
- ReportLab professional formatting
- Charts embedded (300 DPI)
- Tables with proper styling
- Title page with property photo

### Quarto Report (HTML/PDF)
- Narrative Evidence-Based Valuation
- Interactive HTML with TOC
- Print-ready PDF (1-inch margins)
- USPAP certification section

## 🔍 Data Requirements

### MLS CSV Export Columns
Required (flexible names):
- Sale/Close Date
- Sale/Close Price
- Living Area
- Bedrooms
- Bathrooms

Optional (enhance analysis):
- Year Built
- Lot Size
- Garage Spaces
- Days on Market (DOM)
- Street Address

**Auto-detection:** System handles column name variations:
- "Close Date" / "Sale Date" / "CloseDate"
- "Close Price" / "Sale Price" / "ClosePrice"
- "Living Area" / "GLA" / "SqFt"

## 🛠️ Troubleshooting

### Common Issues

**1. R packages not found:**
```r
install.packages("reticulate")
library(reticulate)
py_config()  # Verify Python integration
```

**2. Python not found in R:**
```r
library(reticulate)
use_python("C:/Users/YOUR_USER/AppData/Local/Programs/Python/Python39/python.exe")
```

**3. CSV columns not detected:**
- Check for UTF-8 encoding
- Verify column headers exist
- Try `test_small.csv` first

**4. Charts not rendering:**
```bash
pip install --upgrade matplotlib seaborn scipy
```

## 📜 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Kyle Pacquin** - Evidence-Based Valuation methodology
- **Bruce Hahn** - R parameterized reporting patterns
- **John Fariss** - Visual analytics inspiration
- **Craig Gilbert** - System integration and Python automation

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues:** [Report a bug](https://github.com/YOUR_USERNAME/evidence-based-appraisal-system/issues)
- **Email:** your.email@example.com

## 🎛️ Interactive Dashboard

**NEW:** Streamlit web dashboard for interactive analysis!

```bash
# Launch dashboard
streamlit run dashboard/streamlit_dashboard.py
```

**Features:**
- 📤 Drag-and-drop CSV upload
- 📊 Real-time regression analysis
- 🎚️ Interactive parameter sliders
- 📱 Mobile-responsive design
- 🌐 Cloud deployment ready
- 📥 Download results as CSV

See `dashboard/README.md` for full documentation.

## 🗺️ Roadmap

- [x] Web dashboard (Streamlit) ✅
- [ ] PostgreSQL database integration
- [ ] Automated MLS data pulls
- [ ] Multi-property batch processing
- [ ] Interactive map visualizations (Leaflet)
- [ ] Commercial property support
- [ ] API endpoints for integration

---

**Version:** 1.0.0  
**Last Updated:** November 2025  
**Status:** Production Ready ✅
