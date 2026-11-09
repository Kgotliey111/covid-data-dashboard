#!/usr/bin/env python3
"""
visualise_covid.py
------------------
Reads the supplied COVID-19 JSON file and produces a three-panel chart:

  1. Cumulative totals  (confirmed, recovered, active, deaths)
  2. Daily new cases    (bars) + 7-day rolling average (line)
  3. Daily deaths       (bars) + 7-day rolling average (line)

Usage:
    python visualise_covid.py                       # uses defaults below
    python visualise_covid.py data.json out.png     # custom input / output

Requires: pandas, matplotlib   (pip install pandas matplotlib)
"""

import sys

import matplotlib
matplotlib.use("Agg")  # render to a file; no display needed (works headless)
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DEFAULT_INPUT = "covid__1_.json"
DEFAULT_OUTPUT = "covid_dashboard.png"


# --------------------------------------------------------------------------
# 1. LOAD & CLEAN
# --------------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    """Load the JSON file and return a clean, typed DataFrame."""
    # dtype=False stops pandas guessing types, so values like "61 927"
    # stay as strings and we control the conversion ourselves.
    df = pd.read_json(path, dtype=False)

    # Normalise column names: the source has a stray double space
    # in "Daily  deaths" and may have leading/trailing whitespace.
    df.columns = [" ".join(c.split()) for c in df.columns]

    # Dates are formatted like "2020/03/05".
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d")

    # Large numbers use spaces as thousands separators ("61 927"),
    # sometimes non-breaking spaces. Strip ALL whitespace, then convert.
    for col in df.columns.drop("Date"):
        cleaned = (
            df[col].astype(str)
            .str.replace(r"\s+", "", regex=True)       # normal + unicode spaces
            .str.replace("\u00a0", "", regex=False)    # explicit NBSP, to be safe
        )
        df[col] = pd.to_numeric(cleaned, errors="raise")

    return df.sort_values("Date").reset_index(drop=True)


# --------------------------------------------------------------------------
# 2. PLOT
# --------------------------------------------------------------------------
def thousands(x, _pos):
    """Tick formatter: 25000 -> '25,000'."""
    return f"{int(x):,}"


def build_figure(df: pd.DataFrame) -> plt.Figure:
    # 7-day rolling mean smooths day-of-week reporting noise.
    df = df.copy()
    df["cases_7d"] = df["Daily Confirmed Cases"].rolling(7, min_periods=1).mean()
    df["deaths_7d"] = df["Daily deaths"].rolling(7, min_periods=1).mean()

    # One figure, three stacked panels sharing the same x (date) axis.
    fig, (ax1, ax2, ax3) = plt.subplots(
        3, 1, figsize=(12, 13), sharex=True,
        gridspec_kw={"height_ratios": [1.3, 1, 1]},
    )

    # ---- Panel 1: cumulative lines -------------------------------------
    series = [
        ("Total Confirmed Cases", "Confirmed", "#1f77b4"),
        ("Total Recovered",       "Recovered", "#2ca02c"),
        ("Active Cases",          "Active",    "#ff7f0e"),
        ("Total Deaths",          "Deaths",    "#d62728"),
    ]
    for col, label, colour in series:
        ax1.plot(df["Date"], df[col], label=label, color=colour, linewidth=2.2)
        # Label the final value at the right-hand end of each line.
        ax1.annotate(f"{df[col].iloc[-1]:,}",
                     (df["Date"].iloc[-1], df[col].iloc[-1]),
                     xytext=(6, 0), textcoords="offset points",
                     color=colour, fontsize=9, va="center")
    ax1.set_title("Cumulative cases", loc="left", fontweight="bold")
    ax1.set_ylabel("People")
    ax1.legend(loc="upper left", frameon=False)

    # ---- Panel 2: daily cases ------------------------------------------
    ax2.bar(df["Date"], df["Daily Confirmed Cases"],
            color="#9ecae1", label="Daily new cases")
    ax2.plot(df["Date"], df["cases_7d"],
             color="#08519c", linewidth=2.2, label="7-day average")
    ax2.set_title("Daily new confirmed cases", loc="left", fontweight="bold")
    ax2.set_ylabel("Cases per day")
    ax2.legend(loc="upper left", frameon=False)

    # ---- Panel 3: daily deaths -----------------------------------------
    ax3.bar(df["Date"], df["Daily deaths"],
            color="#fcae91", label="Daily deaths")
    ax3.plot(df["Date"], df["deaths_7d"],
             color="#a50f15", linewidth=2.2, label="7-day average")
    ax3.set_title("Daily deaths", loc="left", fontweight="bold")
    ax3.set_ylabel("Deaths per day")
    ax3.legend(loc="upper left", frameon=False)

    # ---- Shared styling -------------------------------------------------
    for ax in (ax1, ax2, ax3):
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(thousands))
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.margins(x=0.01)

    # Extra right-hand room so the end-of-line labels in panel 1 aren't clipped.
    ax1.set_xlim(df["Date"].iloc[0], df["Date"].iloc[-1] + pd.Timedelta(days=6))

    ax3.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")

    start, end = df["Date"].iloc[0], df["Date"].iloc[-1]
    fig.suptitle(
        f"COVID-19 progression, {start:%d %b %Y} \u2013 {end:%d %b %Y}",
        fontsize=16, fontweight="bold", y=0.995,
    )
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# 3. ENTRY POINT
# --------------------------------------------------------------------------
def main() -> None:
    in_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    df = load_data(in_path)
    fig = build_figure(df)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Loaded {len(df)} rows; chart saved to {out_path}")


if __name__ == "__main__":
    main()
