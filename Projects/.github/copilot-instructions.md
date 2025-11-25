# Real Estate Market Analysis System - AI Agent Instructions

## Project Overview

This is a **real estate appraisal market analysis system** that processes MLS sales data and generates comprehensive statistical reports (Excel, PDF, charts) for property appraisers. The system consists of two main workflows:

1. **Root-level workflow**: Simple CLI-based report generator (`market_report.py`) with GUI launcher
2. **v1.1.0 workflow**: Form-driven, integrated analysis pipeline for professional appraisal reports

## Critical Architecture Patterns

### Two Separate Systems (Don't Mix!)

- **Root level** (`market_report.py`, `market_report_gui.py`, `core.py`):
  - Standalone CLI tool: `python market_report.py --data comps.csv --output_dir out`
  - Uses `market_config.yaml` for column mapping
  - GUI wrapper in `market_report_gui.py` launches CLI subprocess
  - `core.py` is a placeholder adapter (see TODO comments)

- **market_analysis_v1.1.0/**:
  - **Form-first workflow**: HTML form → JSON config → analysis scripts
  - Orchestrator: `run_integrated_analysis_v2.3.3.py` launches form, waits for JSON, runs pipeline
  - Three-stage pipeline: `market_analysis_v1.1.0.py` → `adjustment_analysis_v1.1.1.py` → `create_excel.py` + `create_pdf.py`

### Data Flow: v1.1.0 Pipeline (Most Important)

```
1. User fills market_analysis_form.html → downloads market_analysis_inputs.json
2. run_integrated_analysis_v2.3.3.py:
   - Opens form in browser
   - Waits for JSON file (checks ~/Downloads)
   - Saves JSON to working directory
3. market_analysis_v1.1.0.py reads JSON + CSV:
   - Loads subject property config (living area, bedrooms, etc.)
   - Processes sales data with time-based filtering
   - Outputs: sales_data_processed.csv, statistics_summary.csv, validation_info.json
4. adjustment_analysis_v1.1.1.py:
   - Reads processed data + validation_info.json for config
   - Calculates time adjustments (market trend) and size adjustments
   - Outputs: adjustment_analysis.csv, adjustment_summary.json
5. create_excel.py + create_pdf.py:
   - Generate final reports from all intermediate CSVs/JSONs
```

**Critical**: Scripts share config via `validation_info.json` (contains subject property, thresholds, date of value). Never hardcode subject address or parameters.

### Configuration Precedence

v1.1.0 scripts use this loading order:
1. CLI argument: `python market_analysis_v1.1.0.py <csv_path>`
2. JSON field: `form_data['csv_path']` or alternate keys like `csv_file_path`
3. Key normalization: Scripts map alternate form keys (e.g., `subject_gla` → `living_area`)

See `market_analysis_v1.1.0.py` lines 48-62 for the `alt_key_map` pattern.

## Developer Workflows

### Running the Simple CLI Workflow

```powershell
# From root directory
python market_report.py --data sample_data.csv --output_dir out
# Or use GUI
python market_report_gui.py
```

Optional flags: `--subject_csv <path>`, `--no-pdf` (skip ReportLab if errors)

### Running the v1.1.0 Integrated Workflow

```powershell
cd market_analysis_v1.1.0
python run_integrated_analysis_v2.3.3.py
# Follow prompts: fill form, save JSON, provide CSV path
```

Or manually:
```powershell
# Step 1: Fill form manually, save JSON to working directory
# Step 2: Run pipeline
python market_analysis_v1.1.0.py "2025 Sold data.csv"
python adjustment_analysis_v1.1.1.py
python create_excel.py
python create_pdf.py
```

### Testing

Minimal test suite in `tests/test_smoke.py`. To add meaningful tests:
```powershell
pytest tests/
```

## Key Conventions & Patterns

### Column Name Detection (market_report.py)

Uses flexible column matching via `detect_columns()` (line ~294):
- Tries common variations: `CloseDate`/`SoldDate`/`Sale Date` → normalized to `sold_date`
- Config override: `market_config.yaml` explicitly maps CSV columns
- Always use normalized names internally (`sold_date`, `sold_price`, `psf`, etc.)

### Date Handling

- **Parse flexibly**: `pd.to_datetime()` with error handling for various formats
- **Time adjustments**: v1.1.0 calculates daily price change from monthly trend: `daily_price_change = monthly_trend_pct / 30.44 * avg_price / 100`
- **Thresholds**: `TIME_ADJUSTMENT_THRESHOLD_DAYS` (default 30) from form JSON

### Encoding Resilience

`read_csv_smart()` function (market_report.py line ~21):
```python
for enc in ("utf-8", "cp1252"):
    try:
        return pd.read_csv(path, encoding=enc, **kwargs)
    except UnicodeDecodeError:
        continue
```
Always use this for CSV reading to handle MLS data encoding issues.

### Excel Styling (create_excel.py)

Consistent style definitions at top:
```python
header_fill = PatternFill(start_color="366092", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=11)
```
Apply to all section headers for professional appearance.

### Chart Generation

- **Matplotlib backend**: `matplotlib.use("Agg")` for headless rendering
- **Subject property markers**: Use `plot_subject_vline()` and `plot_subject_point()` helpers (market_report.py)
- **Heatmaps**: Folium for interactive HTML maps (`build_folium_heatmap()`) - requires lat/lon columns

## Dependencies & Environment

Install from root: `pip install -r requirements.txt`
- Core: pandas, numpy, matplotlib, openpyxl, reportlab
- Optional: folium, branca, contextily, pyproj (for heatmaps)

**Windows PowerShell**: Execution policy may block `.ps1` scripts:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

## Common Gotchas

1. **Hardcoded paths in v1.1.0**: Several scripts have `/home/claude/` paths (create_excel.py, adjustment_analysis.py). These work when run from `market_analysis_v1.1.0/` working directory but fail otherwise. Use relative paths or check working directory.

2. **JSON file location**: `run_integrated_analysis_v2.3.3.py` checks `~/Downloads/` first. If user saves elsewhere, script prompts for path.

3. **Missing validation_info.json**: adjustment_analysis and report generators depend on this. Always run `market_analysis_v1.1.0.py` first to generate it.

4. **Subject property in outputs**: Excel/PDF generators have hardcoded "528 S. Taper Ave" examples. Extract from `validation_info.json['subject_property']` instead.

5. **Decimal precision**: Price/SF adjustments use specific formatting: `+.2f%` for percentages, `$#,##0` for currency in Excel.

## File Structure Reference

```
market_analysis_v2.3.3/
├── market_report.py              # Root CLI tool (1832 lines)
├── market_report_gui.py          # GUI launcher (subprocess wrapper)
├── core.py                       # Adapter stub (TODO: wire to market_report)
├── market_config.yaml            # Column mappings for root workflow
├── requirements.txt              # Dependencies
├── run.ps1                       # Simple PowerShell launcher
├── sample_data.csv               # Example data
├── market_analysis_v1.1.0/       # ⚠️ Separate integrated workflow
│   ├── run_integrated_analysis_v2.3.3.py  # Orchestrator (launches form)
│   ├── market_analysis_form.html.html     # Input form (700 lines)
│   ├── market_analysis_inputs.json        # Config from form
│   ├── market_analysis_v1.1.0.py          # Main analysis (557 lines)
│   ├── adjustment_analysis_v1.1.1.py      # Adjustments (263 lines)
│   ├── create_excel.py                    # Workbook generator (435 lines)
│   ├── create_pdf.py                      # PDF report (395 lines)
│   ├── *.bat                              # Windows launchers
│   └── outputs/                           # Generated reports
└── tests/
    └── test_smoke.py             # Minimal test (expand me!)
```

## When Adding Features

- **New analysis metric**: Add to `statistics_summary.csv` output in `market_analysis_v1.1.0.py`, then update Excel sheet headers in `create_excel.py`
- **New form field**: Add to HTML form, update JSON keys in `alt_key_map` if needed, read in main analysis script
- **New chart**: Follow pattern in `market_report.py` (~line 1600+): create figure, save to output dir, add path to `chart_paths` list for PDF inclusion
- **Column mapping**: Add to `market_config.yaml` (root workflow) or `detect_columns()` function (v1.1.0)

## Repository Context

- **Owner**: HBAppraiser
- **Repo**: market_analysis_v2.3.3
- **Branch**: main
- Project for Craig Gilbert Appraisals (since 1975) - litigation support focus
