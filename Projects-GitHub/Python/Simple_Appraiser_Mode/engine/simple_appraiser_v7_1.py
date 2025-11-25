"""
simple_appraiser_v7_1.py

Simple Appraiser Mode – Version 7.1

Purpose:
- Appraiser selects a CSV of closed sales.
- Script automatically detects Sale Price and Living Area columns.
- Computes basic statistics (Sale Price & optionally Price per SF).
- Output is saved as an Excel file in the same folder as the CSV.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd


# --------- Helper Functions --------- #

def choose_csv() -> str | None:
    """Open a file dialog and return a CSV path, or None if cancelled."""
    root = tk.Tk()
    root.withdraw()
    csv_path = filedialog.askopenfilename(
        title="Select Closed Sales CSV",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    root.destroy()
    return csv_path or None


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Find the first matching column by name (case-insensitive).
    Returns the actual column name in the DataFrame, or None.
    """
    lower_map = {c.lower().strip(): c for c in df.columns}
    for name in candidates:
        key = name.lower().strip()
        if key in lower_map:
            return lower_map[key]
    return None


def compute_stats(df: pd.DataFrame, price_col: str, gla_col: str | None):
    """
    Compute statistics for Sale Price and Price per SF (if GLA exists).
    Returns a dict: { sheet_name: DataFrame }
    """
    results = {}

    # Convert price to numeric
    price_series = pd.to_numeric(df[price_col], errors="coerce")
    price_clean = price_series.dropna()

    if price_clean.empty:
        raise ValueError(f"No valid numeric values in price column '{price_col}'")

    price_stats = price_clean.describe().to_frame(name="Sale Price")
    results["Sale Price Stats"] = price_stats

    # Price per SF
    if gla_col is not None:
        gla_series = pd.to_numeric(df[gla_col], errors="coerce")
        psf = (price_series / gla_series.replace(0, pd.NA)).dropna()

        if not psf.empty:
            psf_stats = psf.describe().to_frame(name="Price per SF")
            results["Price per SF Stats"] = psf_stats

    return results


def save_to_excel(results: dict, csv_path: str) -> str:
    """
    Save each stats table to a separate sheet in an Excel file.
    Returns the full path of the Excel file.
    """
    folder = os.path.dirname(csv_path)
    base = os.path.splitext(os.path.basename(csv_path))[0]
    out_name = f"{base}_simple_stats_v7_1.xlsx"
    out_path = os.path.join(folder, out_name)

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet_name, df_stats in results.items():
            df_stats.to_excel(writer, sheet_name=sheet_name)

    return out_path


# --------- Main Logic --------- #

def main():
    print("=== Simple Appraiser Mode v7.1 ===")

    # Allow passing CSV path on the command line
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        print(f"Using CSV from command line: {csv_path}")
    else:
        print("No CSV path provided – opening file chooser...")
        csv_path = choose_csv()

    if not csv_path:
        print("No file selected. Exiting.")
        return

    csv_path = os.path.abspath(os.path.expanduser(csv_path))
    if not os.path.exists(csv_path):
        messagebox.showerror("Error", f"CSV not found at:\n{csv_path}")
        return

    print(f"CSV selected:\n  {csv_path}")

    # Load CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        messagebox.showerror("Error", f"Could not read CSV:\n{e}")
        return

    if df.empty:
        messagebox.showerror("Error", "CSV loaded but contains no rows.")
        return

    # Try to detect columns
    price_candidates = ["Sale Price", "ClosePrice", "Close Price", "PriceSold"]
    gla_candidates = ["LivingArea", "Living Area", "GLA", "Sqft", "SF Bldg", "Building SF"]

    price_col = find_column(df, price_candidates)
    gla_col = find_column(df, gla_candidates)

    if price_col is None:
        messagebox.showerror(
            "Error",
            "Could not find a price column.\n"
            "Tried: " + ", ".join(price_candidates)
        )
        return

    print(f"Detected price column: {price_col}")
    if gla_col:
        print(f"Detected GLA column: {gla_col}")
    else:
        print("No GLA column found – Price per SF will not be computed.")

    # Compute stats
    try:
        results = compute_stats(df, price_col, gla_col)
    except Exception as e:
        messagebox.showerror("Error", f"Error computing stats:\n{e}")
        return

    # Save results
    try:
        out_path = save_to_excel(results, csv_path)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save Excel output:\n{e}")
        return

    message = (
        "Simple Appraiser Stats Completed.\n\n"
        f"Input CSV:\n{csv_path}\n\n"
        f"Output Excel:\n{out_path}"
    )

    print(message)
    messagebox.showinfo("Finished", message)


if __name__ == "__main__":
    main()
