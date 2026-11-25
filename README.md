# Task 3 - Deep-Dive Analysis & Interactive Dashboarding

**Internship:** ApexPlanet Software Pvt. Ltd. - Data Analytics (Task 3)
**Tools:** Python (Pandas, SciPy, Matplotlib), HTML / JavaScript (Chart.js)

## Objective
Define the core KPIs, run a deep-dive analysis on one business area, and build an interactive dashboard.

## Live dashboard
**Link:** [paste your dashboard link here]
You can also open `dashboard.html` from this repo in any browser (it needs internet access to load the Chart.js library). To host it free on GitHub, go to **Settings > Pages**, choose the main branch, and the page will be available at `https://<your-username>.github.io/<repo-name>/dashboard.html`.

## Repository contents

| File / folder | Purpose |
|---|---|
| `kpi_definitions.md` | The 5 core KPIs: formula, rationale, current value |
| `deep_dive_report.md` | **Main report**: segmentation deep-dive, findings, recommendations |
| `dashboard.html` | Interactive dashboard (standalone page) |
| `dashboard_template.html`, `dashboard_artifact.html` | Dashboard source template and the version published as a hosted page |
| `01_kpis_and_segmentation.py` | Computes KPIs, segments, tests and charts |
| `02_build_dashboard.py` | Builds the dashboard pages from the template and the data |
| `outputs/` | Segment tables, KPI table, key findings (JSON), dashboard data, orders with segments |
| `charts/` | Charts used in the report |
| `data/cleaned_sales_data.csv` | Input data from Task 1 |
| `bi_tool_rebuild_guide.md` | Steps to rebuild the dashboard in Looker Studio, Power BI or Tableau |

## 1. Core KPIs
Total revenue, orders, average order value, month-over-month revenue growth and top-20% revenue concentration. Formulas and reasons are in `kpi_definitions.md`.

## 2. Deep-dive: segmentation analysis
Every order is placed in one of four segments from two rules: unit price at or above the median (Premium) or below (Value), and 6-10 units (Bulk) or 1-5 units (Light).

- **Premium Bulk is 24% of orders but 52.5% of revenue**, and holds all 19 high-value orders.
- Value Light is 26% of orders but only 7.6% of revenue.
- Premium Bulk stays at 48-55% of revenue in every quarter, and it explains about 94% of the Q2-to-Q3 revenue drop.
- Age, gender, city and category do not identify Premium Bulk buyers (all chi-square p-values above 0.09), so offers should be triggered from the basket, not the customer profile.

Cohort and funnel analysis were not possible: 895 of 947 Customer_IDs appear once and the data has no visit or checkout steps (details in the report).

## 3. Interactive dashboard
- Filters: month range, city, category, gender, age group, segment, and a reset button.
- Click a segment card, or a category or city bar, to filter everything else.
- KPI tiles, segment comparison, monthly revenue stacked by segment, segment mix per category, and revenue by category and city.
- Works in light and dark mode and on a phone.

## How to run
```
pip install pandas numpy scipy matplotlib
python 01_kpis_and_segmentation.py
python 02_build_dashboard.py
```
Then open `dashboard.html`.

## Limitations
The data looks simulated, so findings demonstrate the method. There is no cost, margin or reliable customer key, so profitability and retention cannot be analysed. See section 7 of the report.
