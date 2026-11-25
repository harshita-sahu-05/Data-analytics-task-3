# Core KPIs

Five KPIs for the sales dashboard. Values are for all 1,000 orders (1 Jan 2025 - 1 Jan 2026), in INR. They are also shown live on the dashboard and respond to its filters.

| # | KPI | Formula | Business rationale | Current value |
|---|---|---|---|---|
| 1 | Total revenue | `SUM(Total_Sales)` | Size of the business and the base for every share and growth figure. | 139,399,440 (Rs 139.4M) |
| 2 | Orders | `COUNT(Order_ID)` | Demand volume, independent of price. Revenue can fall because orders fell or because order value fell; this separates the two. | 1,000 |
| 3 | Average order value (AOV) | `Total revenue / Orders` (always shown with the median) | How much each order is worth. The median is lower because a minority of large orders pull the average up. | 139,399 (median 108,594) |
| 4 | MoM revenue growth | `(Revenue this month - Revenue last month) / Revenue last month`, full months only | Revenue swings from month to month; this flags dips early. January 2026 is left out because it holds only 5 orders. | Range -19.6% to +36.2%; last full month (Dec) -2.6% |
| 5 | Top-20% revenue concentration | `Revenue of the largest 20% of orders / Total revenue` | Shows dependence on big orders. A high value means losing a few large buyers hurts. | 46.8% |

## Deep-dive metric (not a headline KPI)
**Premium Bulk revenue share** = revenue from orders with unit price at or above the median (Rs 25.4K) and 6-10 units, divided by total revenue. Current value: **52.5%** from 24.2% of orders. See `deep_dive_report.md`.

## KPIs from the brief's examples that were not possible
Conversion rate and churn need website-visit or repeat-customer data. This dataset has neither, and Customer_ID is not a reliable person key (52 IDs show different names, ages or cities), so retention-style KPIs would be misleading.
