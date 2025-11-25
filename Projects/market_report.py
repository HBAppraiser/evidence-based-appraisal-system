#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Market Report Generator (Python) - Full Final Script
# =============================================================================

import argparse, os, sys, json, math, zipfile
from datetime import datetime
from typing import Optional, List, Tuple

missing_libs = []

try:
    import pandas as pd
except ImportError as e:
    missing_libs.append(("pandas", str(e)))
    raise SystemExit("pandas is required. Install it with: pip install pandas")


def read_csv_smart(path, **kwargs):
    for enc in ("utf-8", "cp1252"):
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding="latin1", errors="replace", **kwargs)


try:
    import numpy as np
except Exception as e:
    np = None
    missing_libs.append(("numpy", str(e)))

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
except Exception as e:
    plt = None
    missing_libs.append(("matplotlib", str(e)))

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    reportlab_ok = True
except Exception as e:
    reportlab_ok = False
    missing_libs.append(("reportlab", str(e)))

try:
    import openpyxl

    openpyxl_ok = True
except Exception as e:
    openpyxl_ok = False
    missing_libs.append(("openpyxl", str(e)))

try:
    import folium
    from folium.plugins import HeatMap
    import branca.colormap as bcm

    folium_ok = True
except Exception:
    folium_ok = False

try:
    import contextily as cx
    import pyproj

    contextily_ok = True
except Exception:
    contextily_ok = False

    from datetime import datetime
from typing import Optional, List, Tuple


# --- Text/encoding helpers ---
import unicodedata
import pandas as pd


def plot_subject_vline(ax, xval: float | None, label="Subject"):
    if xval is None:
        return
    ax.axvline(xval, linestyle="--", linewidth=2.5)
    ymax = ax.get_ylim()[1]
    ax.text(
        xval,
        ymax * 0.95,
        f"{label}: {xval:,.0f}",
        rotation=90,
        va="top",
        ha="right",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8),
    )


def normalize_label(s):
    """Make any label/title ASCII-safe so it won't show as â€” â€œ â€ â€™ on Windows."""
    if s is None:
        return s
    s = str(s)
    s = unicodedata.normalize("NFKC", s)
    return (
        s.replace("\u2018", "'")  # ‘
        .replace("\u2019", "'")  # ’
        .replace("\u2013", "-")  # –
        .replace("\u2014", "-")  # —
        .replace("\u201c", '"')  # “
        .replace("\u201d", '"')  # ”
        .replace("\u00a0", " ")  # NBSP
    )


def demojibake(s):
    """Fix text that was UTF-8 bytes mis-read as cp1252 (shows up as â€” etc.)."""
    try:
        return str(s).encode("latin1").decode("utf-8")
    except Exception:
        return s


def read_csv_smart(path, **kwargs):
    """Read CSV with best-guess encoding, then clean all string columns once."""
    for enc in ("utf-8", "cp1252"):
        try:
            df = read_csv_smart(...)(path, encoding=enc, **kwargs)
            break
        except UnicodeDecodeError:
            continue
    else:
        df = read_csv_smart(...)(path, encoding="latin1", errors="replace", **kwargs)

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].map(lambda x: normalize_label(demojibake(x)))
    return df


# Wrappers to sanitize titles/labels
def set_title(ax, text):
    set_title(normalize_label(text))


def set_xlabel(ax, text):
    set_xlabel(normalize_label(text))


def set_ylabel(ax, text):
    set_ylabel(normalize_label(text))


# ---- Subject utilities ----
def _get_subject_value(df, colname):
    if df is None or not len(df):
        return None
    if colname not in df.columns:
        return None
    val = df.iloc[0][colname]
    try:
        v = float(val)
        # clean obvious NaNs/Infs
        if v != v or v in (float("inf"), float("-inf")):
            return None
        return v
    except Exception:
        return None


def subject_from_csv(path: str | None, detect_columns_fn) -> dict:
    """Load subject CSV (single-row) and return a dict of values using auto-detected columns."""
    if not path:
        return {}
    sdf = read_csv_smart(path)
    smap = detect_columns(sdf)  # reuse your existing detector
    return {
        "living": _get_subject_value(sdf, smap.get("living") or "living"),
        "psf": _get_subject_value(sdf, smap.get("psf") or "psf"),
        "price": _get_subject_value(sdf, smap.get("price") or "price"),
        "year_built": _get_subject_value(sdf, smap.get("year_built") or "year_built"),
        "lat": _get_subject_value(sdf, smap.get("lat") or "lat"),
        "lon": _get_subject_value(sdf, smap.get("lon") or "lon"),
    }


def plot_subject_vline(ax, xval: float | None, label="Subject"):
    """Overlay a dashed vertical line + label if value exists."""
    if xval is None:
        return
    ax.axvline(xval, linestyle="--", linewidth=2.5)
    ymax = ax.get_ylim()[1]
    ax.text(
        xval,
        ymax * 0.95,
        f"{label}: {xval:,.0f}",
        rotation=90,
        va="top",
        ha="right",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8),
    )


def plot_subject_point(ax, xval: float | None, yval: float | None, label="Subject"):
    """Overlay a star marker at (x,y) if both exist."""
    if xval is None or yval is None:
        return
    ax.scatter([xval], [yval], s=180, marker="*", zorder=5)
    ax.annotate(
        label,
        (xval, yval),
        xytext=(8, 8),
        textcoords="offset points",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8),
    )


def set_labels(ax, **kwargs):
    """Drop-in replacement for ax.set(...). Cleans all string labels."""
    for k, v in list(kwargs.items()):
        if isinstance(v, str):
            kwargs[k] = normalize_label(v)
    return ax.set(**kwargs)


# Optional: plain minus signs
import matplotlib as mpl

mpl.rcParams["axes.unicode_minus"] = False
# --- end helpers ---


def set_labels(ax, **kwargs):
    """Drop-in replacement for ax.set(...). Cleans all string labels."""
    for k, v in list(kwargs.items()):
        if isinstance(v, str):
            kwargs[k] = normalize_label(v)
    return ax.set(**kwargs)


def normalize_label(s): ...


# (rest of helper code here)


def currency_fmt(x) -> str:
    if x is None:
        return ""
    try:
        v = float(x)
        if abs(v) < 1:
            return f"${v:,.2f}"
        return f"${v:,.0f}"
    except Exception:
        return str(x)


def slope_fmt(val, unit: str) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
    except Exception:
        return ""
    if abs(v) < 0.01:
        return "≈ Flat"
    if abs(v) < 1:
        return f"{v:+.2f} {unit}"
    return f"{currency_fmt(v)} {unit}"


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def find_first_column(df: "Any", candidates: List[str]) -> Optional[str]:
    if df is None or df.empty:
        return None
    lower = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def detect_columns(df) -> dict:
    m = {}
    m["date"] = find_first_column(
        df, ["CloseDate", "Sold Date", "SoldDate", "Close Date", "DateSold", "COE"]
    )
    m["price"] = find_first_column(
        df,
        ["ClosePrice", "Sale Price", "Sold Price", "PriceSold", "SoldPrice", "Price"],
    )
    m["psf"] = find_first_column(
        df, ["PricePerSquareFoot", "Price PSF", "PSF", "Price/SF", "Price Per SF"]
    )
    m["status"] = find_first_column(df, ["Standard Status", "Status", "StandardStatus"])
    m["listing_id"] = find_first_column(
        df, ["Listing ID", "ListingID", "MLS#", "MLSNumber", "MLS", "MLS ID"]
    )
    m["address"] = find_first_column(
        df, ["Property Address", "Full Address", "Address", "Street Address"]
    )
    m["lat"] = find_first_column(df, ["Latitude", "Lat"])
    m["lon"] = find_first_column(df, ["Longitude", "Lon", "Lng"])
    m["living"] = find_first_column(
        df, ["Living Area", "Sq Ft", "SqFt", "LivingArea", "GLA", "Gross Living Area"]
    )
    m["year_built"] = find_first_column(
        df, ["Year Built", "YrBuilt", "Built Year", "YearBuilt"]
    )
    m["lot"] = find_first_column(
        df,
        [
            "Lot Size",
            "LotSize",
            "Lot Sq Ft",
            "LotSqFt",
            "Lot Area",
            "LotSizeSquareFeet",
        ],
    )
    m["zip"] = find_first_column(df, ["ZIP", "ZipCode", "Postal Code", "PostalCode"])
    m["bed"] = find_first_column(df, ["Bedrooms", "Beds", "BR", "Bed"])
    return m


def norm_status(val) -> str:
    if not isinstance(val, str):
        return ""
    v = val.strip().lower()
    if v in ["a", "active", "act"]:
        return "Active"
    if v in ["p", "pend", "pending", "u", "under contract", "under-contract", "uc"]:
        return "Pending"
    if v in ["c", "closed", "sold", "s"]:
        return "Closed"
    if v == "subject":
        return "Subject"
    return val.title()


def identify_subject(df: pd.DataFrame, mapping: dict) -> Optional[int]:
    cand_idx = []
    for col in [mapping.get("status"), mapping.get("listing_id")]:
        if col and col in df.columns:
            mask = df[col].astype(str).str.strip().str.upper() == "SUBJECT"
            cand_idx.extend(df.index[mask].tolist())
    for col in df.columns:
        if col.lower() == "issubject":
            hits = df.index[
                df[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["1", "true", "yes", "y"])
            ].tolist()
            cand_idx.extend(hits)
    try:
        mask_any = (
            df.astype(str)
            .apply(lambda s: s.str.strip().str.upper() == "SUBJECT")
            .any(axis=1)
        )
        cand_idx.extend(df.index[mask_any].tolist())
    except Exception:
        pass
    cand_idx = list(dict.fromkeys(cand_idx))
    return cand_idx[0] if cand_idx else None


from typing import Any


def fit_linear_xy(x: Any, y: Any) -> Tuple[Optional[float], Optional[float]]:
    if x is None or y is None or len(x) < 2:
        return None, None
    import numpy as np

    A = np.vstack([x, np.ones(len(x))]).T
    try:
        slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
        return slope, intercept
    except Exception:
        return None, None


def best_poly_xy(x, y, degrees=(2, 3, 4)) -> Tuple[Optional[Any], Optional[int]]:
    if x is None or y is None or len(x) < 5:
        return None, None
    import numpy as np

    best = (None, -1e9, None)
    n = len(x)
    for d in degrees:
        try:
            p = np.poly1d(np.polyfit(x, y, d))
            yhat = p(x)
            ss_res = np.sum((y - yhat) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot != 0 else -1e9
            adj_r2 = 1 - (1 - r2) * (n - 1) / (n - d - 1) if (n - d - 1) > 0 else r2
            if adj_r2 > best[1]:
                best = (p, adj_r2, d)
        except Exception:
            continue
    return best[0], best[2]


def days_from_min(dates: "pd.Series"):
    base = dates.min()
    return (dates - base).dt.days.values


def months_from_min(dates: pd.Series):
    return days_from_min(dates) / 30.4375


def percent_per_month_from_logfit(x_months, y):
    import numpy as np, math

    y = np.asarray(y, dtype=float)
    mask = y > 0
    x = np.asarray(x_months)[mask]
    ly = np.log(y[mask])
    if len(x) < 2:
        return None
    A = np.vstack([x, np.ones(len(x))]).T
    b, a = np.linalg.lstsq(A, ly, rcond=None)[0]
    return (math.exp(b) - 1) * 100.0


from math import radians, sin, cos, asin, sqrt


def haversine_miles(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


def save_fig(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return path


def trend_chart(
    df,
    date_col,
    value_col,
    out_png,
    title,
    unit_label="day",
    subject_date=None,
    subject_val=None,
):
    import numpy as np, pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    d = df[[date_col, value_col]].dropna().copy()
    if d.empty:
        return None
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna().sort_values(date_col)
    x_days = days_from_min(d[date_col])
    x_months = months_from_min(d[date_col])
    y = d[value_col].astype(float).values
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(d[date_col].values, y, s=20, label="Sales")
    handles, labels = [], []
    slope, intercept = fit_linear_xy(x_days, y)
    if slope is not None:
        ax.plot(d[date_col].values, slope * x_days + intercept, color="black", lw=3)
        (line_lin,) = ax.plot([], [], color="black", lw=3, label="Linear fit")
        handles.append(line_lin)
        labels.append("Linear fit")
        ax.text(
            0.01,
            0.97,
            f"Slope ≈ {slope_fmt(slope, '/'+unit_label)}",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.6),
        )
    p, deg = best_poly_xy(x_days, y, degrees=(2, 3, 4))
    if p is not None:
        order = np.argsort(x_days)
        ax.plot(
            d[date_col].values[order],
            p(x_days[order]),
            linestyle="--",
            color="darkred",
            lw=3,
        )
        (line_poly,) = ax.plot(
            [], [], color="darkred", ls="--", lw=3, label=f"Poly deg {deg}"
        )
        handles.append(line_poly)
        labels.append(f"Poly deg {deg}")
    pct = percent_per_month_from_logfit(x_months, y)
    if pct is not None:
        ax.text(
            0.01,
            0.90,
            f"Log trend ≈ {pct:+.2f}%/month",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.6),
        )
    if subject_date is not None and subject_val is not None:
        ax.axvline(subject_date, color="red", lw=2, label="Subject")
        ax.scatter([subject_date], [subject_val], s=60, color="red", zorder=5)
    ax.set_ylim(bottom=0, top=max(y) * 1.2)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: currency_fmt(v)))
    set_title(ax, title)
    if handles:
        ax.legend(
            handles,
            labels,
            loc="upper right",
            frameon=True,
            facecolor="white",
            framealpha=0.85,
        )
    for lab in ax.get_xticklabels():
        lab.set_rotation(45)
        lab.set_ha("right")

        # plot_subject_vline(ax, subject.get("living") if subject else None, label="Subject")
        return save_fig(fig, out_png)


def scatter_with_fit(
    df,
    x_col,
    y_col,
    out_png,
    title,
    slope_unit="per unit",
    subject_x=None,
    subject_y=None,
):
    import numpy as np, pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    d = df[[x_col, y_col]].dropna().copy()
    if d.empty:
        return None
    x = d[x_col].astype(float).values
    y = d[y_col].astype(float).values
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y, s=20, label="Sales")
    handles, labels = [], []
    slope, intercept = fit_linear_xy(x, y)
    if slope is not None:
        xx = np.linspace(min(x), max(x), 100)
        ax.plot(xx, slope * xx + intercept, color="black", lw=3)
        (line_lin,) = ax.plot([], [], color="black", lw=3, label="Linear fit")
        handles.append(line_lin)
        labels.append("Linear fit")
        ax.text(
            0.01,
            0.97,
            f"Slope ≈ {slope_fmt(slope, slope_unit)}",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.6),
        )
    p, deg = best_poly_xy(x, y, degrees=(2, 3, 4))
    if p is not None:
        order = np.argsort(x)
        ax.plot(x[order], p(x[order]), linestyle="--", color="darkred", lw=3)
        (line_poly,) = ax.plot(
            [], [], color="darkred", ls="--", lw=3, label=f"Poly deg {deg}"
        )
        handles.append(line_poly)
        labels.append(f"Poly deg {deg}")
    if subject_x is not None and subject_y is not None:
        ax.scatter(
            [subject_x], [subject_y], s=150, color="black", zorder=5, label="Subject"
        )
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: currency_fmt(v)))
    set_title(ax, title)
    if handles:
        ax.legend(
            handles,
            labels,
            loc="upper right",
            frameon=True,
            facecolor="white",
            framealpha=0.85,
        )
    return save_fig(fig, out_png)


def histogram_with_subject(
    df, col, out_png, title, subject_val=None, is_currency=False, bins=20
):
    import pandas as pd, numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    n, bins_edges, patches = ax.hist(
        s, bins=bins, edgecolor="black", linewidth=1, alpha=0.8, color="#7A7A7A"
    )
    for i, (patch, count) in enumerate(zip(patches, n)):
        height = patch.get_height()
        if height > 0:
            ax.text(
                patch.get_x() + patch.get_width() / 2,
                height + max(n) * 0.01,
                f"{int(count)}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    # Overlay subject line if provided
    plot_subject_vline(
        ax, subject_val if subject_val is not None else None, label="Subject"
    )
    mean_v, med_v = s.mean(), s.median()
    is_year_data = not is_currency and s.min() >= 1800 and s.max() <= 2100

    def format_value(val):
        if is_currency:
            return currency_fmt(val)
        elif is_year_data:
            return f"{val:.0f}"
        else:
            return f"{val:,.0f}"

    ax.axvline(mean_v, color="black", lw=3, label="Mean")
    ax.text(
        mean_v,
        max(n) * 0.9,
        f"Mean: {format_value(mean_v)}",
        rotation=90,
        va="top",
        ha="right",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )
    ax.axvline(med_v, color="darkred", lw=3, ls="--", label="Median")
    ax.text(
        med_v,
        max(n) * 0.9,
        f"Median: {format_value(med_v)}",
        rotation=90,
        va="top",
        ha="left",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )
    if subject_val is not None:
        ax.axvline(subject_val, color="darkgreen", lw=3, label="Subject")
        ax.text(
            subject_val,
            max(n) * 0.8,
            f"Subject: {format_value(subject_val)}",
            rotation=90,
            va="top",
            ha="center",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8),
        )
    if is_currency:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: currency_fmt(v)))
    set_title(ax, title)
    ax.legend(frameon=True, facecolor="white", framealpha=0.85)
    # Subject overlay (if provided)
    if subject_val is not None and subject_val != "":
        try:
            v = float(subject_val)
            plot_subject_vline(ax, v, label="Subject")
        except Exception:
            pass
    return save_fig(fig, out_png)


def normalize_yn_series(s):
    y_vals = {"Y", "YES", "TRUE", "1", "T"}
    n_vals = {"N", "NO", "FALSE", "0", "F"}
    return (
        s.astype(str)
        .str.strip()
        .str.upper()
        .map(lambda v: "Y" if v in y_vals else ("N" if v in n_vals else None))
    )


def histogram_binary_counts(df, col, out_png, title):
    import pandas as pd, numpy as np
    import matplotlib.pyplot as plt

    if col not in df.columns:
        return None
    s = normalize_yn_series(df[col]).dropna()
    if s.empty:
        return None
    counts = s.value_counts().reindex(["Y", "N"]).fillna(0).astype(int)
    total = int(counts.sum())
    perc = (counts / total * 100).round(1) if total > 0 else counts * 0
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(["Y", "N"], counts.values, edgecolor="black", linewidth=1)
    for i, b in enumerate(bars):
        h = b.get_height()
        label = f"N={int(h)} ({perc.values[i]:.1f}%)" if total > 0 else "N=0 (0.0%)"
        ax.text(
            b.get_x() + b.get_width() / 2,
            h,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
        )
    set_ylabel("Count")
    set_title(ax, title)
    return save_fig(fig, out_png)


def histogram_view_with_stats(df, view_col, price_col, out_png, title):
    import pandas as pd, numpy as np
    import matplotlib.pyplot as plt

    if view_col not in df.columns:
        return None
    view = normalize_yn_series(df[view_col])
    price = (
        pd.to_numeric(df[price_col], errors="coerce")
        if price_col in df.columns
        else None
    )
    dd = pd.DataFrame({"__view": view, "__price": price})
    dd = dd.dropna(subset=["__view"])
    if price_col in df.columns:
        dd = dd.dropna(subset=["__price"])
    if dd.empty:
        return None
    counts = dd["__view"].value_counts().reindex(["Y", "N"]).fillna(0).astype(int)
    total = int(counts.sum())
    perc = (counts / total * 100).round(1) if total > 0 else counts * 0
    med = (
        dd.groupby("__view")["__price"].median().reindex(["Y", "N"])
        if price_col in df.columns
        else pd.Series([None, None], index=["Y", "N"])
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(["Y", "N"], counts.values, edgecolor="black", linewidth=1)
    for i, b in enumerate(bars):
        h = b.get_height()
        label1 = f"N={int(h)} ({perc.values[i]:.1f}%)" if total > 0 else "N=0 (0.0%)"
        ax.text(
            b.get_x() + b.get_width() / 2,
            h,
            label1,
            ha="center",
            va="bottom",
            fontsize=10,
        )
        if pd.notna(med.iloc[i]):
            ax.text(
                b.get_x() + b.get_width() / 2,
                h * 1.03 + 0.03 * max(1, h),
                f"Median Price: {currency_fmt(med.iloc[i])}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="black",
            )
    set_ylabel("Count")
    set_title(ax, title)
    return save_fig(fig, out_png)


def build_folium_heatmap(
    df,
    lat_col,
    lon_col,
    out_html,
    weight_col=None,
    center=None,
    zoom_start=12,
    radius=14,
    blur=22,
    min_opacity=0.2,
    title="Heatmap",
):
    try:
        import folium
        from folium.plugins import HeatMap
        import branca.colormap as bcm
    except Exception:
        return None
    import pandas as pd, numpy as np

    d = df.copy()
    d["__lat"] = pd.to_numeric(d[lat_col], errors="coerce")
    d["__lon"] = pd.to_numeric(d[lon_col], errors="coerce")
    if weight_col and weight_col in d.columns:
        d["__w"] = pd.to_numeric(d[weight_col], errors="coerce")
    else:
        d["__w"] = 1.0
    d = d.dropna(subset=["__lat", "__lon", "__w"])
    if d.empty:
        return None
    if center is None:
        center = (d["__lat"].mean(), d["__lon"].mean())
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        control_scale=True,
        tiles="CartoDB Positron",
    )
    heat_data = d[["__lat", "__lon", "__w"]].values.tolist()
    HeatMap(
        heat_data, radius=radius, blur=blur, min_opacity=min_opacity, max_zoom=18
    ).add_to(m)
    try:
        vmin, vmax = float(d["__w"].min()), float(d["__w"].max())
        cm = bcm.linear.YlOrRd_09.scale(vmin, vmax)
        cm.caption = f"{title}" + (f" (weight: {weight_col})" if weight_col else "")
        cm.add_to(m)
    except Exception:
        pass
    m.save(out_html)
    return out_html


def static_hexbin_heat(
    df, lat_col, lon_col, out_png, title="Comps Spatial Density (hexbin)", gridsize=45
):
    import pandas as pd
    import matplotlib.pyplot as plt

    d = df.copy()
    d["__lat"] = pd.to_numeric(d[lat_col], errors="coerce")
    d["__lon"] = pd.to_numeric(d[lon_col], errors="coerce")
    d = d.dropna(subset=["__lat", "__lon"])
    if d.empty:
        return None
    try:
        import contextily as cx, pyproj

        proj = pyproj.Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
        x, y = proj.transform(d["__lon"].values, d["__lat"].values)

        fig, ax = plt.subplots(figsize=(9, 7))
        hb = ax.hexbin(x, y, gridsize=gridsize, cmap="YlOrRd", bins="log")
        cb = fig.colorbar(hb, ax=ax)
        cb.set_label("log10(count)")

        set_xlabel(ax, "Longitude")
        set_ylabel(ax, "Latitude")
        set_title(ax, title, fontsize=14, fontweight="bold")

        ax.set_axis_off()
        return save_fig(fig, out_png)

    except Exception:
        fig, ax = plt.subplots(figsize=(9, 7))
        hb = ax.hexbin(
            d["__lon"], d["__lat"], gridsize=gridsize, cmap="YlOrRd", bins="log"
        )
        cb = fig.colorbar(hb, ax=ax)
        cb.set_label("log10(count)")

        set_xlabel(ax, "Longitude")
        set_ylabel(ax, "Latitude")
        set_title(ax, title)

        return save_fig(fig, out_png)


def static_scatter_map(
    df,
    lat_col,
    lon_col,
    out_png,
    title="Market Data Map",
    subject_lat=None,
    subject_lon=None,
    basemap_type="street",
    status_col=None,
):
    import pandas as pd
    import matplotlib.pyplot as plt

    d = df.copy()
    d["__lat"] = pd.to_numeric(d[lat_col], errors="coerce")
    d["__lon"] = pd.to_numeric(d[lon_col], errors="coerce")
    d = d.dropna(subset=["__lat", "__lon"])
    if d.empty:
        return None
    if status_col and status_col in d.columns:
        d["__status"] = d[status_col].apply(norm_status)
    else:
        d["__status"] = "Unknown"
    has_subject = subject_lat is not None and subject_lon is not None
    fig, ax = plt.subplots(figsize=(12, 9))
    for status in d["__status"].unique():
        mask = d["__status"] == status
        if not mask.any():
            continue
        if status == "Closed":
            color, label = "red", "Sold Properties"
        elif status == "Active":
            color, label = "blue", "Active Listings"
        elif status == "Pending":
            color, label = "orange", "Pending Sales"
        else:
            color, label = "gray", "Other Properties"
        ax.scatter(
            d["__lon"][mask],
            d["__lat"][mask],
            s=25,
            c=color,
            alpha=0.7,
            label=label,
            edgecolors="white",
            linewidth=0.5,
        )
    if has_subject:
        ax.scatter(
            [subject_lon],
            [subject_lat],
            s=150,
            c="black",
            label="Subject Property",
            zorder=10,
            edgecolors="white",
            linewidth=2,
        )
    set_xlabel("Longitude")
    set_ylabel("Latitude")
    set_title(ax, title, fontsize=14, fontweight="bold")
    ax.legend(
        loc="upper right",
        frameon=True,
        facecolor="white",
        framealpha=0.9,
        edgecolor="black",
        fontsize=10,
        title="Property Types",
        title_fontsize=11,
    )
    return save_fig(fig, out_png)


def detect_pool_column(df):
    candidates = [
        "Pool",
        "PrivatePool",
        "Private Pool",
        "Pool Private",
        "HasPool",
        "PoolYN",
        "Pool YN",
        "PoolYesNo",
        "PoolFlag",
    ]
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


def detect_view_column(df):
    candidates = [
        "View",
        "ViewYN",
        "View YN",
        "HasView",
        "PrivateView",
        "View_YesNo",
        "ViewYesNo",
        "ViewFlag",
    ]
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


def compute_absorption(df, date_col, status_col):
    import pandas as pd

    dd = df.copy()
    dd["__date"] = (
        pd.to_datetime(dd[date_col], errors="coerce")
        if date_col and date_col in dd.columns
        else pd.NaT
    )
    dd["__status"] = (
        dd[status_col].apply(norm_status)
        if status_col and status_col in dd.columns
        else ""
    )
    asof = (
        dd["__date"].max()
        if "__date" in dd and not dd["__date"].isnull().all()
        else pd.Timestamp.today()
    )
    rows = []
    for m in [3, 6, 9, 12]:
        start = asof - pd.DateOffset(months=m)
        closed = dd[
            (dd["__status"] == "Closed")
            & (dd["__date"] >= start)
            & (dd["__date"] <= asof)
        ]
        avg_pm = len(closed) / (m if m > 0 else 1)
        rows.append({"WindowMonths": m, "AvgMonthlyClosed": avg_pm})
    absorp = pd.DataFrame(rows)
    actives = int((dd["__status"] == "Active").sum())
    absorp["MOI"] = absorp["AvgMonthlyClosed"].apply(
        lambda v: (actives / v) if v > 0 else float("inf")
    )
    return absorp, actives, asof


def absorption_chart(absorp_df, out_png):
    import matplotlib.pyplot as plt

    if absorp_df is None or absorp_df.empty:
        return None
    fig, ax1 = plt.subplots(figsize=(10, 6))
    bars = ax1.bar(
        absorp_df["WindowMonths"].astype(str),
        absorp_df["AvgMonthlyClosed"],
        color="lightgray",
        label="Avg Monthly Closed",
    )
    for b in bars:
        h = b.get_height()
        ax1.text(
            b.get_x() + b.get_width() / 2,
            h,
            f"{h:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax1.set_ylabel("Avg Monthly Closed Sales")
    ax2 = ax1.twinx()
    ax2.plot(
        absorp_df["WindowMonths"].astype(str),
        absorp_df["MOI"],
        marker="o",
        lw=2,
        color="red",
        label="MOI",
    )
    ax2.set_ylabel("Months of Inventory")
    lines, labels = [], []
    for ax in (ax1, ax2):
        h, l = ax.get_legend_handles_labels()
        lines += h
        labels += l
    ax1.legend(
        lines,
        labels,
        loc="upper right",
        frameon=True,
        facecolor="white",
        framealpha=0.85,
    )
    fig.suptitle("Absorption & Months of Inventory")
    return save_fig(fig, out_png)


def write_excel(
    out_xlsx,
    df_all,
    summary_df=None,
    absorp_df=None,
    nearest_df=None,
    narrative_lines=None,
):
    try:
        import pandas as pd, openpyxl
    except Exception:
        return None
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as xw:
        df_all.to_excel(xw, index=False, sheet_name="Data")
        if summary_df is not None:
            summary_df.to_excel(xw, index=True, sheet_name="SummaryStats")
        if absorp_df is not None:
            absorp_df.to_excel(xw, index=False, sheet_name="Absorption_Inventory")
        if nearest_df is not None:
            nearest_df.to_excel(xw, index=False, sheet_name="NearestComps")
        if narrative_lines is not None:
            pd.DataFrame({"Narrative": narrative_lines}).to_excel(
                xw, index=False, sheet_name="Narrative"
            )
    return out_xlsx


def build_pdf(out_pdf, image_paths, narrative_lines=None):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
    except Exception:
        return None
    c = canvas.Canvas(out_pdf, pagesize=letter)
    W, H = letter
    if narrative_lines:
        c.setFont("Times-Roman", 12)
        y = H - 72
        for line in narrative_lines:
            c.drawString(72, y, (line or "")[:110])
            y -= 16
            if y < 72:
                c.showPage()
                y = H - 72
        c.showPage()
    for p in image_paths:
        try:
            if os.path.exists(p):
                img = ImageReader(p)
                iw, ih = img.getSize()
                scale = min((W - 72) / iw, (H - 72) / ih)
                w = iw * scale
                h = ih * scale
                x = (W - w) / 2
                y = (H - h) / 2
                c.drawImage(img, x, y, width=w, height=h)
                c.showPage()
        except Exception:
            continue
    c.save()
    return out_pdf


def boxplot_with_quartiles_and_subject(
    df,
    value_col,
    group_col,
    out_png,
    title,
    subject_val=None,
    top_k=5,
    is_currency=True,
):
    import pandas as pd, numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    d = df[[group_col, value_col]].dropna().copy()
    if d.empty:
        return None
    if top_k:
        keep = d[group_col].value_counts().head(top_k).index
        d = d[d[group_col].isin(keep)]
    groups = [g for g, _ in d.groupby(group_col)]
    data = [grp[value_col].values for _, grp in d.groupby(group_col)]
    vals = pd.to_numeric(d[value_col], errors="coerce").dropna().values
    if len(vals) == 0:
        return None
    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    fig, ax = plt.subplots(figsize=(10, 7))
    bp = ax.boxplot(data, labels=groups, patch_artist=True)
    for box in bp["boxes"]:
        box.set(facecolor="lightblue", alpha=0.6)
    for med in bp["medians"]:
        med.set(color="darkred", lw=2)
    if subject_val is not None:
        ax.axhline(subject_val, color="black", lw=2, label="Subject")
    xmin, xmax = 0.5, len(groups) + 0.5
    ax.hlines(q25, xmin, xmax, colors="gray", linestyles=":", lw=1.5)
    ax.hlines(q50, xmin, xmax, colors="darkred", linestyles="--", lw=2.5)
    ax.hlines(q75, xmin, xmax, colors="gray", linestyles=":", lw=1.5)
    ax.set_xlim(0.4, len(groups) + 0.9)
    x_text = len(groups) + 0.6
    ax.text(
        x_text,
        q25,
        f"25th: {currency_fmt(q25)}",
        va="center",
        ha="left",
        fontsize=9,
        color="black",
        weight="bold",
    )
    ax.text(
        x_text,
        q50,
        f"50th: {currency_fmt(q50)}",
        va="center",
        ha="left",
        fontsize=9,
        color="darkred",
        weight="bold",
    )
    ax.text(
        x_text,
        q75,
        f"75th: {currency_fmt(q75)}",
        va="center",
        ha="left",
        fontsize=9,
        color="black",
        weight="bold",
    )
    if is_currency:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: currency_fmt(v)))
    set_title(ax, title)
    ax.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.85)
    for lab in ax.get_xticklabels():
        lab.set_rotation(45)
        lab.set_ha("right")
    return save_fig(fig, out_png)


def main():
    ap = argparse.ArgumentParser(description="Market Report Generator (Python)")
    ap.add_argument("--data", required=True, help="Path to comps CSV")
    ap.add_argument("--output_dir", default="market_outputs", help="Output directory")
    ap.add_argument("--subject_csv", default=None, help="Optional one-row subject CSV")
    ap.add_argument("--sold_date_column", default=None)
    ap.add_argument("--sold_price_column", default=None)
    ap.add_argument("--psf_column", default=None)
    ap.add_argument("--status_column", default=None)
    ap.add_argument("--listingid_column", default=None)
    ap.add_argument("--address_column", default=None)
    ap.add_argument("--living_area_column", default=None)
    ap.add_argument("--year_built_column", default=None)
    ap.add_argument("--lot_size_column", default=None)
    ap.add_argument("--zip_column", default=None)
    ap.add_argument("--bedrooms_column", default=None)
    ap.add_argument("--lat_column", default=None)
    ap.add_argument("--lon_column", default=None)
    args = ap.parse_args()

    print("Market Report Generator (Python)")
    print("=" * 60)
    if missing_libs:
        print("Note: Some libraries may be missing:")
        for name, err in missing_libs:
            print(f" - {name}: {err}")
        print("")

    outdir = ensure_dir(args.output_dir)
    charts_dir = ensure_dir(os.path.join(outdir, "charts"))

    if pd is None:
        print("pandas not available; cannot proceed.")
        sys.exit(2)
    print(f"Loading data: {args.data}")
    df = read_csv_smart(args.data)

    print(f"Loaded records: {len(df)}")

    # Detect columns mapping before using it
    mapping = detect_columns(df)

    if args.sold_date_column:
        mapping["date"] = args.sold_date_column
    if args.sold_price_column:
        mapping["price"] = args.sold_price_column
    if args.psf_column:
        mapping["psf"] = args.psf_column
    if args.status_column:
        mapping["status"] = args.status_column
    if args.listingid_column:
        mapping["listing_id"] = args.listingid_column
    if args.address_column:
        mapping["address"] = args.address_column
    if args.living_area_column:
        mapping["living"] = args.living_area_column
    if args.year_built_column:
        mapping["year_built"] = args.year_built_column
    if args.lot_size_column:
        mapping["lot"] = args.lot_size_column
    if args.zip_column:
        mapping["zip"] = args.zip_column
    if args.bedrooms_column:
        mapping["bed"] = args.bedrooms_column
    if args.lat_column:
        mapping["lat"] = args.lat_column
    if args.lon_column:
        mapping["lon"] = args.lon_column


# Build subject values once (OK if None)
subject = subject_from_csv(args.subject_csv, detect_columns)
print("SUBJECT:", subject)  # temporary debug

if mapping["status"] and mapping["status"] in df.columns:
    df["__Status"] = df[mapping["status"]].apply(norm_status)
else:
    df["__Status"] = ""

subj_idx = identify_subject(df, mapping)
subject_row = df.iloc[subj_idx] if subj_idx is not None else None

# --- SUBJECT: read values from the single subject row safely ---
subj_vals = {
    "date": None,
    "price": None,
    "psf": None,
    "living": None,
    "year": None,
    "lot": None,
    "zip": None,
}

if subject_row is not None:
    # subject_row is a pandas Series (one row); its columns are in subject_row.index
    cols = set(map(str, subject_row.index))

    def _has(colname: str | None) -> bool:
        return bool(colname) and str(colname) in cols

    def _num(colname: str | None):
        if not _has(colname):
            return None
        return pd.to_numeric(subject_row.get(colname), errors="coerce")

    def _text(colname: str | None):
        if not _has(colname):
            return None
        v = subject_row.get(colname)
        return None if pd.isna(v) else str(v)

    # mapping[...] should contain the detected column names
    subj_vals["date"] = (
        pd.to_datetime(subject_row.get(mapping.get("date")), errors="coerce")
        if _has(mapping.get("date"))
        else None
    )
    subj_vals["price"] = _num(mapping.get("price"))
    subj_vals["psf"] = _num(mapping.get("psf"))
    subj_vals["living"] = _num(mapping.get("living"))
    subj_vals["year"] = _num(mapping.get("year_built"))
    subj_vals["lot"] = _num(mapping.get("lot"))
    subj_vals["zip"] = _text(mapping.get("zip"))

print("SUBJECT VALUES:", subj_vals)  # debug line so you can see what was found
if mapping["date"]:
    df[mapping["date"]] = pd.to_datetime(df[mapping["date"]], errors="coerce")
    price_col = mapping["price"]
    psf_col = mapping["psf"]
    comps = df.drop(index=[subj_idx]) if subj_idx is not None else df
    asof = (
        df[mapping["date"]].max()
        if mapping["date"] and mapping["date"] in df.columns
        else pd.Timestamp.today()
    )

    print(f"As-of date: {asof.date() if hasattr(asof, 'date') else asof}")
    print(f"Comps used (excluding Subject if any): {len(comps)}")

    chart_paths = []

    if mapping["date"] and price_col and price_col in comps.columns:
        p = trend_chart(
            comps,
            mapping["date"],
            price_col,
            os.path.join(charts_dir, "trend_price.png"),
            "Sale Price Trend — All Data",
            unit_label="day",
            subject_date=subj_vals["date"],
            subject_val=subj_vals["price"],
        )
        if p:
            chart_paths.append(p)

    if (
        mapping["living"]
        and price_col
        and mapping["living"] in comps.columns
        and price_col in comps.columns
    ):
        p = scatter_with_fit(
            comps,
            mapping["living"],
            price_col,
            os.path.join(charts_dir, "scatter_living_price.png"),
            "Living Area vs Sale Price",
            slope_unit="per SF",
            subject_x=subj_vals["living"],
            subject_y=subj_vals["price"],
        )
        if p:
            chart_paths.append(p)

    if price_col and price_col in comps.columns:
        p = histogram_with_subject(
            comps,
            price_col,
            os.path.join(charts_dir, "hist_price.png"),
            "Histogram — Sale Price",
            subject_val=subj_vals.get("price"),
            is_currency=True,
            bins=20,
        )
        if p:
            chart_paths.append(p)
    if psf_col and psf_col in comps.columns:
        p = histogram_with_subject(
            comps,
            psf_col,
            os.path.join(charts_dir, "hist_psf.png"),
            "Histogram — Price/SF",
            subject_val=subj_vals.get("psf"),
            is_currency=True,
            bins=20,
        )
        if p:
            chart_paths.append(p)
    if mapping.get("living") and mapping["living"] in comps.columns:
        p = histogram_with_subject(
            comps,
            mapping["living"],
            os.path.join(charts_dir, "hist_living.png"),
            "Histogram — Living Area (SF)",
            subject_val=subj_vals.get("living"),
            is_currency=False,
            bins=20,
        )
        if p:
            chart_paths.append(p)
    if mapping.get("lot") and mapping["lot"] in comps.columns:
        p = histogram_with_subject(
            comps,
            mapping["lot"],
            os.path.join(charts_dir, "hist_lot.png"),
            "Histogram — Lot Size (SF)",
            subject_val=subj_vals.get("lot"),
            is_currency=False,
            bins=20,
        )
        if p:
            chart_paths.append(p)
    if mapping.get("year_built") and mapping["year_built"] in comps.columns:
        p = histogram_with_subject(
            comps,
            mapping["year_built"],
            os.path.join(charts_dir, "hist_yearbuilt.png"),
            "Histogram — Year Built",
            subject_val=subj_vals.get("year"),
            is_currency=False,
            bins=20,
        )
        if p:
            chart_paths.append(p)

    if (
        psf_col
        and mapping["zip"]
        and psf_col in comps.columns
        and mapping["zip"] in comps.columns
    ):
        p = boxplot_with_quartiles_and_subject(
            comps,
            psf_col,
            mapping["zip"],
            os.path.join(charts_dir, "box_psf_by_zip.png"),
            "Price/SF by ZIP (Top 5)",
            subject_val=subj_vals.get("psf"),
            top_k=5,
            is_currency=True,
        )
        if p:
            chart_paths.append(p)

    year_bins_col = None
    if mapping.get("year_built") and mapping["year_built"] in comps.columns:
        try:
            yr = __import__("pandas").to_numeric(
                comps[mapping["year_built"]], errors="coerce"
            )
            if yr.notna().any():
                lo = int((yr.min() // 20) * 20)
                hi = int((yr.max() // 20) * 20 + 20)
                bins = list(range(lo, hi + 1, 20))
                labels = [f"{bins[i]}–{bins[i+1]-1}" for i in range(len(bins) - 1)]
                comps["__YearBin"] = __import__("pandas").cut(
                    yr, bins=bins, labels=labels, include_lowest=True
                )
                year_bins_col = "__YearBin"
        except Exception:
            pass
    if psf_col and year_bins_col and psf_col in comps.columns:
        p = boxplot_with_quartiles_and_subject(
            comps.dropna(subset=[year_bins_col, psf_col]),
            psf_col,
            year_bins_col,
            os.path.join(charts_dir, "box_psf_by_yearbin.png"),
            "Price/SF by Year-Built (20-yr bins)",
            subject_val=subj_vals.get("psf"),
            top_k=None,
            is_currency=True,
        )
        if p:
            chart_paths.append(p)
    if (
        price_col
        and mapping.get("bed")
        and mapping["bed"] in comps.columns
        and price_col in comps.columns
    ):
        p = boxplot_with_quartiles_and_subject(
            comps.dropna(subset=[mapping["bed"], price_col]),
            price_col,
            mapping["bed"],
            os.path.join(charts_dir, "box_price_by_bed.png"),
            "Sale Price by Bedrooms",
            subject_val=subj_vals.get("price"),
            top_k=None,
            is_currency=True,
        )
        if p:
            chart_paths.append(p)

    pool_col = detect_pool_column(df)
    if pool_col:
        p = histogram_binary_counts(
            df,
            pool_col,
            os.path.join(charts_dir, "hist_private_pool_YN.png"),
            "Private Pool — Y vs N (Count & %)",
        )
        if p:
            chart_paths.append(p)
    view_col = detect_view_column(df)
    if view_col and price_col and price_col in df.columns:
        p = histogram_view_with_stats(
            df,
            view_col,
            price_col,
            os.path.join(charts_dir, "hist_view_YN_counts_pct_median.png"),
            "View — Y vs N (Counts, %, Median Sale Price)",
        )
        if p:
            chart_paths.append(p)

    absorp_df, actives_used, _asof = compute_absorption(
        df, mapping["date"], mapping["status"]
    )
    if absorp_df is not None:
        p = absorption_chart(absorp_df, os.path.join(charts_dir, "absorption_moi.png"))
        if p:
            chart_paths.append(p)

    subj_lat, subj_lon = None, None
    if subject_row is not None and mapping.get("lat") and mapping.get("lon"):
        try:
            subj_lat = float(subject_row.get(mapping["lat"]))
            subj_lon = float(subject_row.get(mapping["lon"]))
        except Exception:
            pass
    distance_df = None
    if (
        subj_lat is not None
        and subj_lon is not None
        and mapping.get("lat")
        and mapping.get("lon")
    ):
        dd = comps.copy()
        dd["__lat"] = __import__("pandas").to_numeric(
            dd.get(mapping["lat"]), errors="coerce"
        )
        dd["__lon"] = __import__("pandas").to_numeric(
            dd.get(mapping["lon"]), errors="coerce"
        )
        dd = dd.dropna(subset=["__lat", "__lon"])
        if not dd.empty:
            dd["DistanceMiles"] = dd.apply(
                lambda r: haversine_miles(subj_lat, subj_lon, r["__lat"], r["__lon"]),
                axis=1,
            )
            distance_df = dd
    if distance_df is not None and price_col in distance_df.columns:
        p = scatter_with_fit(
            distance_df.dropna(subset=["DistanceMiles", price_col]),
            "DistanceMiles",
            price_col,
            os.path.join(charts_dir, "price_vs_distance.png"),
            "Price vs Distance (miles)",
            slope_unit="per mile",
            subject_x=None,
            subject_y=None,
        )
        if p:
            chart_paths.append(p)
    if distance_df is not None and psf_col in distance_df.columns:
        p = scatter_with_fit(
            distance_df.dropna(subset=["DistanceMiles", psf_col]),
            "DistanceMiles",
            psf_col,
            os.path.join(charts_dir, "psf_vs_distance.png"),
            "Price/SF vs Distance (miles)",
            slope_unit="per mile",
            subject_x=None,
            subject_y=None,
        )
        if p:
            chart_paths.append(p)

    center = None
    if subject_row is not None and mapping.get("lat") and mapping.get("lon"):
        try:
            center = (
                float(subject_row[mapping["lat"]]),
                float(subject_row[mapping["lon"]]),
            )
        except Exception:
            center = None

    if mapping.get("lat") and mapping.get("lon"):
        hm_density = os.path.join(outdir, "heatmap_density.html")
        build_folium_heatmap(
            comps,
            mapping["lat"],
            mapping["lon"],
            hm_density,
            weight_col=None,
            center=center,
            zoom_start=12,
            radius=14,
            blur=22,
            title="Comps Density Heatmap",
        )
    if (
        mapping.get("lat")
        and mapping.get("lon")
        and psf_col
        and psf_col in comps.columns
    ):
        hm_psf = os.path.join(outdir, "heatmap_psf_weighted.html")
        build_folium_heatmap(
            comps.dropna(subset=[psf_col]),
            mapping["lat"],
            mapping["lon"],
            hm_psf,
            weight_col=psf_col,
            center=center,
            zoom_start=12,
            radius=16,
            blur=24,
            title="PSF-Weighted Heatmap",
        )
    if (
        mapping.get("lat")
        and mapping.get("lon")
        and price_col
        and price_col in comps.columns
    ):
        hm_price = os.path.join(outdir, "heatmap_price_weighted.html")
        build_folium_heatmap(
            comps.dropna(subset=[price_col]),
            mapping["lat"],
            mapping["lon"],
            hm_price,
            weight_col=price_col,
            center=center,
            zoom_start=12,
            radius=16,
            blur=24,
            title="Price-Weighted Heatmap",
        )

    if mapping.get("lat") and mapping.get("lon"):
        hex_png = os.path.join(charts_dir, "hexbin_density.png")
        p = static_hexbin_heat(
            comps,
            mapping["lat"],
            mapping["lon"],
            hex_png,
            title="Comps Spatial Density (hexbin)",
            gridsize=45,
        )
        if p:
            chart_paths.append(p)

    street_png = os.path.join(charts_dir, "map_market_data_street.png")
    subj_lat2 = (
        float(subject_row[mapping["lat"]])
        if subject_row is not None and mapping["lat"] in subject_row
        else None
    )
    subj_lon2 = (
        float(subject_row[mapping["lon"]])
        if subject_row is not None and mapping["lon"] in subject_row
        else None
    )
    p = static_scatter_map(
        comps,
        mapping["lat"],
        mapping["lon"],
        street_png,
        title="Market Data Map - Street View",
        subject_lat=subj_lat2,
        subject_lon=subj_lon2,
        basemap_type="street",
        status_col="__Status",
    )
    if p:
        chart_paths.append(p)

    aerial_png = os.path.join(charts_dir, "map_market_data_aerial.png")
    p = static_scatter_map(
        comps,
        mapping["lat"],
        mapping["lon"],
        aerial_png,
        title="Market Data Map - Aerial View",
        subject_lat=subj_lat2,
        subject_lon=subj_lon2,
        basemap_type="aerial",
        status_col="__Status",
    )
    if p:
        chart_paths.append(p)

    print(f"Charts generated: {len(chart_paths)}")

    def simple_summary(series):
        s = __import__("pandas").to_numeric(series, errors="coerce").dropna()
        if s.empty:
            return None
        return __import__("pandas").Series(
            {
                "Min": s.min(),
                "Max": s.max(),
                "Mean": s.mean(),
                "Median": s.median(),
                "Std": s.std(ddof=1),
                "Count": int(s.count()),
            }
        )

    sum_items = []
    for name, col in [
        ("Sale Price", price_col),
        ("Price/SF", psf_col),
        ("Living Area (SF)", mapping["living"]),
        ("Lot Size (SF)", mapping["lot"]),
        ("Year Built", mapping["year_built"]),
    ]:
        if col and col in comps.columns:
            res = simple_summary(comps[col])
            if res is not None:
                res.name = name
                sum_items.append(res)
    summary_df = __import__("pandas").DataFrame(sum_items) if sum_items else None

    narrative = []
    narrative.append(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    narrative.append(f"Records (incl. Subject): {len(df):,}")
    narrative.append(f"As-of date: {asof.date() if hasattr(asof, 'date') else asof}")
    if "absorp_df" in locals() and absorp_df is not None:
        try:
            parts = []
            for _, r in absorp_df.iterrows():
                moi_val = r.MOI if math.isfinite(r.MOI) else float("inf")
                parts.append(f"{int(r.WindowMonths)}m={moi_val:.2f}")
            line = "MOI by window: " + ", ".join(parts)
            narrative.append(line)
        except Exception:
            pass

    xlsx_path = os.path.join(outdir, "market_results.xlsx")
    pdf_path = os.path.join(outdir, "market_report.pdf")
    write_excel(
        xlsx_path,
        df_all=df,
        summary_df=summary_df,
        absorp_df=absorp_df,
        nearest_df=None,
        narrative_lines=narrative,
    )
    build_pdf(pdf_path, image_paths=chart_paths, narrative_lines=narrative)

    zip_path = os.path.join(outdir, "market_package.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for pth in chart_paths:
            if pth and os.path.exists(pth):
                z.write(pth, arcname=os.path.join("charts", os.path.basename(pth)))
        if os.path.exists(xlsx_path):
            z.write(xlsx_path, arcname=os.path.basename(xlsx_path))
        if os.path.exists(pdf_path):
            z.write(pdf_path, arcname=os.path.basename(pdf_path))

    print("")
    print("=" * 60)
    print("COMPLETED SUCCESSFULLY")
    print(f"Output directory:   {outdir}")
    print(f"Charts generated:   {len(chart_paths)}")
    print(f"Excel file:         {xlsx_path}")
    print(f"PDF report:         {pdf_path}")
    print(f"ZIP package:        {zip_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
