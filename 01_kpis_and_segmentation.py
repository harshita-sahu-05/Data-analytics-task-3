"""Task 3 - Step 1: core KPIs + deep-dive segmentation analysis.

Deep-dive topic: Segmentation analysis with business rules.
Every order is placed in one of four segments from two order-level facts:
  price level    : Unit_Price at/above vs below the median unit price
  basket size    : Quantity 6-10 ("Bulk") vs 1-5 ("Light")

Input : data/cleaned_sales_data.csv  (output of Task 1)
Output: outputs/*.csv, outputs/key_findings.json, outputs/dashboard_data.json, charts/*.png
Run   : python 01_kpis_and_segmentation.py
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
BASE = Path(__file__).parent
OUT, CH = BASE / "outputs", BASE / "charts"
OUT.mkdir(exist_ok=True)
CH.mkdir(exist_ok=True)

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "axes.axisbelow": True, "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left"})

df = pd.read_csv(BASE / "data" / "cleaned_sales_data.csv", parse_dates=["Order_Date"])
F = {}   # findings

# ============================================================ 1. CORE KPIs
full = df[df.Order_Date < "2026-01-01"]                       # Jan 2026 holds only 5 orders (partial month)
monthly = full.groupby(full.Order_Date.dt.to_period("M")).Total_Sales.sum()
mom = monthly.pct_change().dropna() * 100
k = int(round(len(df) * 0.2))
top20 = df.nlargest(k, "Total_Sales").Total_Sales.sum() / df.Total_Sales.sum() * 100

kpis = pd.DataFrame([
    ("Total revenue", "SUM(Total_Sales)", "Size of the business; base for every share and growth figure.",
     f"{df.Total_Sales.sum():,.0f}"),
    ("Orders", "COUNT(Order_ID)", "Demand volume, independent of price.", f"{len(df):,}"),
    ("Average order value (AOV)", "Total revenue / Orders (report the median too)",
     "Shows how much each order is worth; the median is lower because big orders skew the average.",
     f"{df.Total_Sales.mean():,.0f} (median {df.Total_Sales.median():,.0f})"),
    ("MoM revenue growth", "(Revenue this month - Revenue last month) / Revenue last month, full months only",
     "Revenue swings a lot month to month; this flags dips early.",
     f"{mom.min():.1f}% to +{mom.max():.1f}% (last full month Dec: {mom.iloc[-1]:+.1f}%)"),
    ("Top-20% revenue concentration", "Revenue of the largest 20% of orders / Total revenue",
     "Measures dependence on big orders; high values mean losing a few buyers hurts.", f"{top20:.1f}%"),
], columns=["KPI", "Formula", "Business rationale", "Current value (INR)"])
kpis.to_csv(OUT / "kpi_definitions.csv", index=False)
F["kpi"] = dict(revenue=float(df.Total_Sales.sum()), orders=len(df), aov=float(df.Total_Sales.mean()),
                median_order=float(df.Total_Sales.median()), top20_conc=float(top20),
                mom_min=float(mom.min()), mom_max=float(mom.max()), mom_last=float(mom.iloc[-1]))

# ============================================================ 2. SEGMENTATION (business rules)
price_cut = float(df.Unit_Price.median())
qty_cut = 6                                                    # 6-10 units = bulk
df["Price_Level"] = np.where(df.Unit_Price >= price_cut, "Premium", "Value")
df["Basket"] = np.where(df.Quantity >= qty_cut, "Bulk", "Light")
df["Segment"] = df.Price_Level + " " + df.Basket
SEGS = ["Premium Bulk", "Premium Light", "Value Bulk", "Value Light"]
F["cuts"] = dict(price_cut=price_cut, qty_cut=qty_cut)

seg = df.groupby("Segment").agg(orders=("Order_ID", "count"), revenue=("Total_Sales", "sum"),
                                aov=("Total_Sales", "mean"), median_order=("Total_Sales", "median"),
                                units=("Quantity", "sum"), avg_price=("Unit_Price", "mean"),
                                avg_age=("Age", "mean")).reindex(SEGS)
seg["order_share_pct"] = seg.orders / seg.orders.sum() * 100
seg["revenue_share_pct"] = seg.revenue / seg.revenue.sum() * 100
seg["revenue_per_order_index"] = seg.revenue_share_pct / seg.order_share_pct          # 1.0 = average
seg.round(2).to_csv(OUT / "segment_summary.csv")
F["segments"] = seg.round(2).to_dict("index")

# stability over time: share of revenue by segment per quarter (full months)
full = df[df.Order_Date < "2026-01-01"].copy()
full["Quarter"] = full.Order_Date.dt.to_period("Q").astype(str)
qshare = (full.pivot_table(index="Quarter", columns="Segment", values="Total_Sales", aggfunc="sum")[SEGS]
          .pipe(lambda t: t.div(t.sum(axis=1), axis=0) * 100)).round(1)
qshare.to_csv(OUT / "segment_revenue_share_by_quarter.csv")
qrev = full.pivot_table(index="Quarter", columns="Segment", values="Total_Sales", aggfunc="sum")[SEGS] / 1e6
qrev.round(2).to_csv(OUT / "segment_revenue_by_quarter_M.csv")
chg = (qrev.loc["2025Q3"] - qrev.loc["2025Q2"]).round(2)
F["q2_to_q3_change_M"] = dict(per_segment=chg.to_dict(), total=round(float(chg.sum()), 2),
                              premium_bulk_share_of_change=round(float(chg["Premium Bulk"] / chg.sum() * 100), 1))
F["segment_revenue_by_quarter_M"] = qrev.round(2).to_dict("index")
F["segment_quarter_share"] = qshare.to_dict("index")

# who are the segments? profile against customer / product attributes
real = df[~df.Age_Imputed]
known = df[df.City != "Unknown"]
prof = {}
for name, data, col in [("Category", df, "Category"), ("City", known, "City"), ("Age group", real, "Age_Group"),
                        ("Gender", df, "Gender")]:
    ct = pd.crosstab(data[col], data.Segment)[SEGS]
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
    prof[name] = dict(chi2=round(float(chi2), 1), dof=int(dof), p=round(float(p), 3), cramers_v=round(float(v), 3))
    (ct.div(ct.sum(axis=0), axis=1) * 100).round(1).to_csv(OUT / f"segment_profile_by_{col.lower()}.csv")
F["profile_tests"] = prof

# segment x category revenue (for the dashboard's heat table)
sc = df.pivot_table(index="Segment", columns="Category", values="Total_Sales", aggfunc="sum").reindex(SEGS)
sc.round(0).to_csv(OUT / "segment_x_category_revenue.csv")

# Premium Bulk deep-dive numbers
pb = df[df.Segment == "Premium Bulk"]
F["premium_bulk"] = dict(
    orders=len(pb), order_share=float(len(pb) / len(df) * 100),
    revenue_share=float(pb.Total_Sales.sum() / df.Total_Sales.sum() * 100),
    aov=float(pb.Total_Sales.mean()), high_value_orders=int(pb.Is_High_Value_Order.sum()),
    share_of_high_value=float(pb.Is_High_Value_Order.sum() / df.Is_High_Value_Order.sum() * 100),
    top_category=pb.groupby("Category").Total_Sales.sum().idxmax(),
    top_category_pct=float(pb.groupby("Category").Total_Sales.sum().max() / pb.Total_Sales.sum() * 100))
vb = df[df.Segment == "Value Light"]
F["value_light"] = dict(orders=len(vb), order_share=float(len(vb) / len(df) * 100),
                        revenue_share=float(vb.Total_Sales.sum() / df.Total_Sales.sum() * 100), aov=float(vb.Total_Sales.mean()))

# what-if: how fragile is revenue to the Premium Bulk segment?
F["what_if"] = dict(revenue_without_pb_pct=float(100 - F["premium_bulk"]["revenue_share"]),
                    revenue_if_pb_down_10pct=float(-0.10 * F["premium_bulk"]["revenue_share"]))

# is Premium Bulk volume steady month to month? (orders per month)
pbm = pb[pb.Order_Date < "2026-01-01"].groupby(pb.Order_Date.dt.to_period("M")).size()
F["premium_bulk_orders_per_month"] = dict(min=int(pbm.min()), max=int(pbm.max()), mean=round(float(pbm.mean()), 1))

# does segment structure differ by category / city in revenue share terms (heat table values)
F["segment_by_category_share"] = (sc.div(sc.sum(axis=0), axis=1) * 100).round(1).to_dict()

# ============================================================ 3. CHARTS
cols = {"Premium Bulk": BLUE, "Premium Light": "#9cc3f0", "Value Bulk": ORANGE, "Value Light": "#f5b79d"}

fig, ax = plt.subplots(figsize=(8.2, 4.3))
x = np.arange(len(SEGS))
w = 0.36
b1 = ax.bar(x - w / 2, seg.order_share_pct, w, color="#9a9992", label="Share of orders")
b2 = ax.bar(x + w / 2, seg.revenue_share_pct, w, color=BLUE, label="Share of revenue")
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.8, f"{r.get_height():.0f}%", ha="center", fontsize=9, color=INK2)
ax.set_xticks(x)
ax.set_xticklabels(SEGS)
ax.set_ylabel("% of total")
ax.set_ylim(0, max(seg.revenue_share_pct.max(), seg.order_share_pct.max()) * 1.18)
ax.grid(axis="x", visible=False)
ax.legend(frameon=False)
ax.set_title("Segments: share of orders vs share of revenue")
fig.savefig(CH / "01_segment_orders_vs_revenue.png", dpi=160, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(7.4, 5))
for s in SEGS:
    d = df[df.Segment == s]
    ax.scatter(d.Unit_Price, d.Quantity + np.random.default_rng(1).uniform(-.18, .18, len(d)), s=12, alpha=.55,
               color=cols[s], edgecolor="none", label=s)
ax.axvline(price_cut, color=INK, lw=1, ls="--")
ax.axhline(qty_cut - 0.5, color=INK, lw=1, ls="--")
ax.set_xlabel("Unit price (INR)")
ax.set_ylabel("Units per order (jittered)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v / 1e3:.0f}K"))
ax.set_title("How the four segments split the orders")
ax.legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, -0.12))
fig.savefig(CH / "02_segment_map.png", dpi=160, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4))
bottom = np.zeros(len(qshare))
for s in SEGS:
    ax.bar(qshare.index, qshare[s], bottom=bottom, color=cols[s], label=s, width=0.6, edgecolor=SURFACE, linewidth=1.5)
    for i, v in enumerate(qshare[s]):
        ax.text(i, bottom[i] + v / 2, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                color="white" if s in ("Premium Bulk", "Value Bulk") else INK)
    bottom += qshare[s].values
ax.set_ylabel("% of quarter revenue")
ax.grid(axis="x", visible=False)
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
ax.set_title("Revenue mix by segment, per quarter")
fig.savefig(CH / "03_segment_share_by_quarter.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# ============================================================ 4. DASHBOARD DATA (compact, dictionary-coded)
df["AgeGroupDash"] = np.where(df.Age_Imputed, "Unknown", df.Age_Group)
months = [p.strftime("%Y-%m") for p in pd.period_range("2025-01", "2026-01", freq="M")]
dims = {
    "months": months,
    "categories": sorted(df.Category.unique()),
    "products": sorted(df.Product.unique()),
    "cities": sorted(df.City.unique(), key=lambda c: (c == "Unknown", c)),
    "genders": sorted(df.Gender.unique()),
    "ageGroups": ["18-24", "25-34", "35-44", "45-54", "55+", "Unknown"],
    "segments": SEGS,
}
idx = lambda key, col: df[col].map({v: i for i, v in enumerate(dims[key])}).astype(int)
rows = pd.DataFrame({
    "m": df.Order_Date.dt.strftime("%Y-%m").map({v: i for i, v in enumerate(months)}).astype(int),
    "c": idx("categories", "Category"), "p": idx("products", "Product"), "ci": idx("cities", "City"),
    "g": idx("genders", "Gender"), "a": idx("ageGroups", "AgeGroupDash"), "q": df.Quantity.astype(int),
    "pr": df.Unit_Price.round(2), "s": df.Total_Sales.round(2), "sg": idx("segments", "Segment"),
}).values.tolist()
payload = dict(dims=dims, cols=["m", "c", "p", "ci", "g", "a", "q", "pr", "s", "sg"], rows=rows,
               cuts=dict(price=round(price_cut, 2), qty=qty_cut))
(OUT / "dashboard_data.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
df[["Order_ID", "Order_Date", "Category", "Product", "City", "Gender", "AgeGroupDash", "Age_Imputed", "Quantity", "Unit_Price",
    "Total_Sales", "Price_Level", "Basket", "Segment"]].rename(columns={"AgeGroupDash": "Age_Group"}).to_csv(
    OUT / "orders_with_segments.csv", index=False)

(OUT / "key_findings.json").write_text(json.dumps(F, indent=2, default=str), encoding="utf-8")

print(kpis.to_string(index=False))
print(seg.round(1).to_string())
print(qshare.to_string())
print(json.dumps(F["profile_tests"], indent=1))
print(json.dumps(F["premium_bulk"], indent=1), json.dumps(F["value_light"]), F["premium_bulk_orders_per_month"], F["cuts"])
print(sc.round(0).to_string())
print("payload kB:", round((OUT / "dashboard_data.json").stat().st_size / 1024, 1))
