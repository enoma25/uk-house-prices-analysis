"""UK house prices since 1953: nominal vs inflation-adjusted (real) prices.

Data (public, open licence):
  - Nationwide house price series via github.com/datasets/house-prices-uk
  - UK CPI annual price index via github.com/datasets/cpi-uk

Questions
  1. How far have prices risen since 1953 in nominal terms and after inflation?
  2. Which decades saw the strongest and weakest real growth?
  3. Which property type grew fastest over the period it was tracked?
  4. When were the sharpest real-terms falls?
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE = "https://raw.githubusercontent.com/datasets"
HOUSE_URL = f"{BASE}/house-prices-uk/main/data/data.csv"
CPI_URL = f"{BASE}/cpi-uk/main/data/cpi-uk-annual.csv"
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load quarterly house prices and annual CPI, return one row per year."""
    house = pd.read_csv(HOUSE_URL, parse_dates=["Date"])
    cpi = pd.read_csv(CPI_URL).rename(columns={"Price Index": "cpi"})

    house["Year"] = house["Date"].dt.year
    price_cols = ["Price (All)", "Price (New)", "Price (Modern)", "Price (Older)"]
    annual = house.groupby("Year")[price_cols].mean().reset_index()
    annual.columns = ["Year", "all", "new", "modern", "older"]

    df = annual.merge(cpi, on="Year", how="left")
    # Express every price in latest-year money using CPI
    latest_cpi = df.loc[df["Year"] == df["Year"].max(), "cpi"].iloc[0]
    for col in ["all", "new", "modern", "older"]:
        df[f"{col}_real"] = df[col] * latest_cpi / df["cpi"]
    return df


def cagr(start: float, end: float, years: int) -> float:
    return (end / start) ** (1 / years) - 1


def summarise(df: pd.DataFrame) -> None:
    first, last = df.iloc[0], df.iloc[-1]
    years = int(last["Year"] - first["Year"])

    print(f"Period: {int(first['Year'])} to {int(last['Year'])} ({years} years)")
    print(f"Average price: £{first['all']:,.0f} -> £{last['all']:,.0f} "
          f"({last['all'] / first['all']:.0f}x nominal)")
    print(f"In {int(last['Year'])} money: £{first['all_real']:,.0f} -> £{last['all_real']:,.0f} "
          f"({last['all_real'] / first['all_real']:.1f}x real)")
    print(f"Real growth: {cagr(first['all_real'], last['all_real'], years):.2%} a year\n")

    # Real growth by decade
    df = df.copy()
    df["decade"] = (df["Year"] // 10) * 10
    rows = []
    for decade, grp in df.groupby("decade"):
        if len(grp) < 8:  # skip partial decades
            continue
        g = cagr(grp["all_real"].iloc[0], grp["all_real"].iloc[-1], len(grp) - 1)
        rows.append({"decade": f"{decade}s", "real_cagr_pct": round(g * 100, 2)})
    decades = pd.DataFrame(rows)
    print("Real price growth by decade (CAGR %):")
    print(decades.to_string(index=False), "\n")
    decades.to_csv(OUT / "real_growth_by_decade.csv", index=False)

    # Property types over the period where all three series have data
    common = df.dropna(subset=["new", "modern", "older"])
    y0, y1 = int(common["Year"].iloc[0]), int(common["Year"].iloc[-1])
    print(f"Growth by property type, nominal, {y0}-{y1} (same period for all):")
    for col in ["new", "modern", "older"]:
        mult = common[col].iloc[-1] / common[col].iloc[0]
        print(f"  {col:>6}: {mult:.0f}x ({cagr(common[col].iloc[0], common[col].iloc[-1], y1 - y0):.2%} a year)")
    print()

    # Sharpest real-terms falls year on year
    df["real_change_pct"] = df["all_real"].pct_change() * 100
    worst = df.nsmallest(5, "real_change_pct")[["Year", "real_change_pct"]]
    worst["real_change_pct"] = worst["real_change_pct"].round(1)
    print("Five sharpest real-terms annual falls:")
    print(worst.to_string(index=False))
    worst.to_csv(OUT / "worst_real_falls.csv", index=False)


def charts(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df["Year"], df["all"], label="Nominal price")
    ax.plot(df["Year"], df["all_real"], label=f"Real price ({int(df['Year'].max())} money)")
    ax.set_title("UK average house price: nominal vs inflation-adjusted")
    ax.set_ylabel("£")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "nominal_vs_real.png", dpi=150)
    plt.close(fig)

    decades = pd.read_csv(OUT / "real_growth_by_decade.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colours = ["#c0392b" if v < 0.5 else "#2e6da4" for v in decades["real_cagr_pct"]]
    ax.bar(decades["decade"], decades["real_cagr_pct"], color=colours)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Real UK house price growth by decade (% a year)")
    ax.set_ylabel("% a year, after inflation")
    fig.tight_layout()
    fig.savefig(OUT / "real_growth_by_decade.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    data = load_data()
    data.to_csv(OUT / "annual_house_prices.csv", index=False)
    summarise(data)
    charts(data)
