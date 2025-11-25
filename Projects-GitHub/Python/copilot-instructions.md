# Real Property Market Analysis System — AI Agent Instructions

## System Architecture & Data Flow
This system analyzes real estate market data to produce statistical reports for property appraisals. The workflow is:

1. **User Input**: Data is collected via `market_analysis_form.html` (or `market_analysis_form_NEW.html`), which outputs `market_analysis_inputs.json`.
2. **Main Orchestration**: Run `run_integrated_analysis_v2.3.3.py` to process inputs and sales CSVs (e.g., `2025 Sold data for Stats_Full (30).csv`).
3. **Analysis Pipeline**:
     - Loads and validates form/CSV data
     - Processes sales records and applies adjustments (`adjustment_analysis_v2.3.3.py`)
     - Generates statistics and visualizations
     - Produces reports (PDF via `create_pdf.py`, Excel via `create_excel.py`)

## Key Files & Responsibilities

## Critical Patterns & Conventions
    ```python
    with open('market_analysis_inputs.json', 'r') as f:
            form_data = json.load(f)
            SUBJECT_ADDRESS = form_data.get('address', 'N/A')
            SUBJECT_LIVING_AREA = int(form_data.get('living_area', 0))
    ```

## Developer Workflows

## Integration & Dependencies

## Common Issues & Gotchas

## Example Project Structure
```
market_analysis_v2.3.3/
├── market_analysis_form.html
├── run_integrated_analysis_v2.3.3.py
├── market_analysis_v2.3.3.py
├── adjustment_analysis_v2.3.3.py
├── create_pdf.py
├── create_excel.py
├── *.csv
├── *.bat
└── outputs/
```
 # AI Agent Instructions for market_analysis_v2.3.3

 ## Project Overview

 This is a real property market analysis tool that generates comprehensive Excel workbooks for appraisal analysis. The project focuses on statistical analysis of real estate sales data with time-based adjustments and market trend analysis.

 ## Key Components

 ### Data Flow
 1. Input files (CSV/JSON):
     - `sales_data_processed.csv`: Core sales data with dates
     - `statistics_summary.csv`: Periodic statistical analysis
     - `adjustment_analysis.csv`: Sales adjustments
     - `validation_info.json`: Data validation results
     - `adjustment_summary.json`: Adjustment calculations

 ### Excel Report Structure
 The workbook generation follows a specific structure:
 1. Summary Report sheet:
     - Property information
     - Data coverage analysis
     - Market trend analysis
     - Adjustment analysis
 2. Statistics by Period sheet:
     - Time-based statistical breakdowns
     - Standard metrics (mean, median, std dev)
     - Price and price/SF analysis

 ## Development Patterns

 ### Data Processing
 - Dates are standardized using `pd.to_datetime()`
 - Numeric formatting follows specific patterns:
    - Currency: `$#,##0`
    - Percentages: `+.2f%`
    - Rates/ratios: `0.00`

 ### Excel Styling
 - Standard style definitions:
    ```python
    header_fill = PatternFill(start_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    ```
 - Consistent section formatting with subheaders and spacing

 ## Dependencies
 - Core libraries: pandas, numpy, openpyxl
 - Data files expected in specific locations
 - Python 3.x environment required

 ## Development Workflow
 1. Input data files must be prepared first
 2. Run `create_excel.py` to generate the workbook
 3. Manual review required for "Indicated Value" field

 ## File Structure
 - `create_excel.py`: Main workbook generation script
 - Input files (required):
    ```
    /path/to/sales_data_processed.csv
    /path/to/statistics_summary.csv
    /path/to/adjustment_analysis.csv
    /path/to/validation_info.json
    /path/to/adjustment_summary.json
    ```

 ## Common Tasks
 1. Adding new statistics:
     - Add column to relevant input CSV
     - Update sheet headers and formatting
 2. Modifying styles:
     - Define new style at top of script
     - Apply consistently across sections

 Note: Path configurations currently hardcoded - may need updating per environment.