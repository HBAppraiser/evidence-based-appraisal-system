"""
CSV File Picker Utility
Reusable module for selecting CSV files from anywhere on your computer
Just import and use: csv_path = get_csv_path()
"""
import os
import sys

def get_csv_path(form_data=None, title="Select CSV File"):
    """
    Get a CSV file path - opens GUI picker automatically if no path provided
    
    Usage:
        from csv_picker import get_csv_path
        csv_path = get_csv_path()
    
    Returns:
        Absolute path to selected CSV file
    """
    if form_data is None:
        form_data = {}
    
    csv_path = None
    
    # Check command line argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        csv_path = str(sys.argv[1]).strip()
    
    # Check form_data dictionary
    if not csv_path:
        for key in ("csv_path", "csv", "sales_csv", "data_file"):
            val = form_data.get(key, "")
            if isinstance(val, str) and val.strip():
                csv_path = val.strip()
                break
    
    # Open GUI file picker (automatic)
    if not csv_path:
        print("\n" + "=" * 80)
        print("Opening file browser to select CSV...")
        print("=" * 80)
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.update()
            
            csv_path = filedialog.askopenfilename(
                title=title,
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            root.destroy()
            
            if not csv_path:
                print("\n❌ No file selected. Exiting.")
                sys.exit(0)
                
            print(f"✓ Selected: {csv_path}\n")
            
        except Exception as e:
            print(f"\n❌ Error opening file browser: {e}")
            sys.exit(1)
    
    # Validate path
    csv_path = os.path.abspath(os.path.expanduser(csv_path))
    
    if not os.path.exists(csv_path):
        print(f"\n❌ File not found: {csv_path}")
        sys.exit(1)
    
    return csv_path


def get_output_dir(csv_path):
    """
    Get output directory (same folder as CSV file)
    
    Usage:
        output_dir = get_output_dir(csv_path)
    """
    output_dir = os.path.dirname(csv_path)
    return output_dir if output_dir else os.getcwd()
