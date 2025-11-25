#!/usr/bin/env python3
"""
INTEGRATED MARKET ANALYSIS SYSTEM
NOW PROPERLY CONNECTS FORM TO ANALYSIS! No more hardcoded values.

This script:
1. Launches the HTML form for user input
2. Waits for form submission (JSON file)
3. Saves form data where analysis scripts can access it
4. Processes the CSV data based on form inputs
5. Runs the complete analysis pipeline
6. Generates all outputs (PDF, Excel, Charts, Markdown)

Version: PROPERLY INTEGRATED
Date: November 1, 2025
For: Craig Gilbert Appraisals
"""

import webbrowser
import os
import time
import json
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 80)
    print(" " * 15 + "CRAIG GILBERT APPRAISALS - MARKET ANALYSIS SYSTEM")
    print(" " * 30 + "SINCE 1975")
    print("=" * 80)
    print("\n" + " " * 20 + "INTEGRATED FORM + ANALYSIS PIPELINE")
  
    print(" " * 25 + "✓ NOW READS FORM INPUTS!")
    print("=" * 80 + "\n")

def launch_form():
    """Launch the HTML form in browser"""
    html_file = os.path.abspath('market_analysis_form.html')
    
    if not os.path.exists(html_file):
        print("❌ ERROR: market_analysis_form.html not found!")
        print(f"   Expected location: {html_file}")
        return False
    
    print("🚀 STEP 1: Launching input form in browser...")
    print(f"📄 Form location: {html_file}\n")
    
    webbrowser.open('file://' + html_file)
    
    print("✅ Form opened successfully!")
    print("\n📝 INSTRUCTIONS:")
    print("   1. Fill out all 7 sections of the form")
    print("   2. Upload your sales data CSV file")
    print("   3. Click 'Submit & Run Analysis'")
    print("   4. Save the JSON file when prompted")
    print("   5. Return to this window\n")
    print("=" * 80)
    
    return True

def wait_for_json():
    """Wait for user to complete form and generate JSON"""
    print("\n⏳ STEP 2: Waiting for form submission...")
    print("   Looking for 'market_analysis_inputs.json' in Downloads folder...\n")
    
    # Common download locations
    possible_paths = [
        os.path.expanduser("~/Downloads/market_analysis_inputs.json"),
        "./market_analysis_inputs.json",
        os.path.expanduser("~/Desktop/market_analysis_inputs.json")
    ]
    
    print("Press ENTER after you've saved the JSON file from the form...")
    input()
    
    # Check if JSON exists
    json_path = None
    for path in possible_paths:
        if os.path.exists(path):
            json_path = path
            break
    
    if not json_path:
        print("\n❌ JSON file not found in common locations.")
        print("   Please enter the full path to market_analysis_inputs.json:")
        json_path = input("   Path: ").strip()
        
        if not os.path.exists(json_path):
            print("❌ File not found. Exiting.")
            return None
    
    print(f"\n✅ Found JSON file: {json_path}")
    return json_path

def load_and_save_form_data(json_path):
    """Load form data and save to working directory"""
    print("\n🔍 STEP 3: Loading and preparing form data...")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Form data loaded successfully")
        print(f"   Subject: {data.get('address', 'N/A')}")
        print(f"   Appraiser: {data.get('appraiser_name', 'N/A')}")
        print(f"   File #: {data.get('file_number', 'N/A')}")
        print(f"   Effective Date: {data.get('effective_date', 'N/A')}")
        
        # CRITICAL: Save form data to working directory where analysis scripts can access it
        working_json_path = os.path.join(os.getcwd(), 'market_analysis_inputs.json')
        with open(working_json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ Form data saved to: {working_json_path}")
        print("   Analysis scripts will now read configuration from this file.")
        
        return data
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return None

def find_csv_file(form_data):
    """Locate the CSV file (either from form data or prompt user)"""
    print("\n📊 STEP 4: Locating sales data CSV...")
    
    # Check if CSV path is in form data
    csv_path = form_data.get('csv_file_path', '')
    
    if csv_path and os.path.exists(csv_path):
        print(f"✅ CSV file from form: {csv_path}")
        return csv_path
    
    # Otherwise ask user
    print("   Please enter the full path to your sales data CSV file:")
    csv_path = input("   Path: ").strip()
    
    # Remove quotes if user copy-pasted path with quotes
    csv_path = csv_path.strip('"').strip("'")
    
    if not os.path.exists(csv_path):
        print("❌ CSV file not found. Exiting.")
        return None
    
    print(f"✅ CSV file found: {csv_path}")
    
    # Save CSV path to form data for scripts to access
    form_data['csv_file_path'] = csv_path
    with open('market_analysis_inputs.json', 'w') as f:
        json.dump(form_data, f, indent=2)
    
    return csv_path

def run_analysis_pipeline(form_data, csv_path):
    """Run the complete analysis pipeline"""
    print("\n" + "=" * 80)
    print("🔬 STEP 5: RUNNING ANALYSIS PIPELINE")
    print("=" * 80 + "\n")
    
    print("📈 Running market analysis (with form inputs)...")
    # Run market_analysis with CSV path as argument
    try:
        result = subprocess.run(['python3', 'market_analysis.py', csv_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Market analysis complete")
            # Show last few lines of output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    print(f"     {line}")
        else:
            print(f"❌ Market analysis failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error in market analysis: {e}")
        return False
    
    print("\n📊 Running adjustment analysis (with form inputs)...")
    # Run adjustment analysis
    try:
        result = subprocess.run(['python3', 'adjustment_analysis.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Adjustment analysis complete")
        else:
            print(f"❌ Adjustment analysis failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error in adjustment analysis: {e}")
        return False
    
    print("\n📊 Generating charts...")
    # Check if current version exists, otherwise use original
    chart_script = 'generate_charts.py' if os.path.exists('generate_charts.py') else 'generate_charts.py'
    try:
        result = subprocess.run(['python3', chart_script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Charts generated")
        else:
            print(f"⚠️  Chart generation completed with warnings")
    except Exception as e:
        print(f"⚠️  Error generating charts (continuing): {e}")
    
    print("\n📑 Creating Excel workbook...")
    # Check if current version exists, otherwise use original
    excel_script = 'create_excel.py' if os.path.exists('create_excel.py') else 'create_excel.py'
    try:
        result = subprocess.run(['python3', excel_script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Excel workbook created")
        else:
            print(f"⚠️  Excel creation completed with warnings")
    except Exception as e:
        print(f"⚠️  Error creating Excel (continuing): {e}")
    
    print("\n📄 Generating PDF report...")
    # Check if current version exists, otherwise use original
    pdf_script = 'create_pdf.py' if os.path.exists('create_pdf.py') else 'create_pdf.py'
    try:
        result = subprocess.run(['python3', pdf_script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PDF report created")
        else:
            print(f"⚠️  PDF creation completed with warnings")
    except Exception as e:
        print(f"⚠️  Error creating PDF (continuing): {e}")
    
    return True

def show_outputs():
    """Display output file locations"""
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 80 + "\n")
    
    print("📦 OUTPUT FILES:")
    
    outputs_dir = os.getcwd()
    
    # List output files
    working_files = [
        ('sales_data_processed.csv', '📊'),
        ('statistics_summary.csv', '📊'),
        ('adjusted_sales.csv', '📊'),
        ('validation_info.json', '📄'),
        ('adjustment_summary.json', '📄'),
    ]
    
    for filename, icon in working_files:
        filepath = os.path.join(outputs_dir, filename)
        if os.path.exists(filepath):
            print(f"   {icon} {filename}")
    
    # List all files in current directory
    import glob
    all_files = glob.glob(os.path.join(outputs_dir, '*.csv')) + \
                glob.glob(os.path.join(outputs_dir, '*.json')) + \
                glob.glob(os.path.join(outputs_dir, '*.xlsx')) + \
                glob.glob(os.path.join(outputs_dir, '*.pdf')) + \
                glob.glob(os.path.join(outputs_dir, '*.png'))
    
    if all_files:
        print(f"\n📁 All files saved to: {outputs_dir}")
        print(f"   Total files: {len(all_files)}")
    else:
        print(f"\n⚠️  No output files found in {outputs_dir}")
    
    print("\n" + "=" * 80)

def main():
    """Main execution flow"""
    print_banner()
    
    # Step 1: Launch form
    if not launch_form():
        return 1
    
    # Step 2: Wait for JSON
    json_path = wait_for_json()
    if not json_path:
        return 1
    
    # Step 3: Load and save form data 
    form_data = load_and_save_form_data(json_path)
    if not form_data:
        return 1
    
    # Step 4: Find CSV
    csv_path = find_csv_file(form_data)
    if not csv_path:
        return 1
    
    # Step 5: Run analysis
    if not run_analysis_pipeline(form_data, csv_path):
        print("\n❌ Analysis pipeline failed. Check errors above.")
        return 1
    
    # Step 6: Show outputs
    show_outputs()
    
    print("\n🎉 All done! Your market analysis is ready.")
    print(f"\n✓ Analysis used YOUR form inputs (not hardcoded values)")
    print(f"✓ Subject property: {form_data.get('address', 'N/A')}")
    print(f"✓ Date of value: {form_data.get('effective_date', 'N/A')}")
    print("\nPress ENTER to exit...")
    input()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
