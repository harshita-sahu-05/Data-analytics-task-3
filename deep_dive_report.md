# Deep-Dive Report: Segmentation Analysis

**Dataset:** `cleaned_sales_data.csv` from Task 1 (1,000 orders, 1 Jan 2025 - 1 Jan 2026)
**Method:** Segmentation by business rules, with Python (Pandas, SciPy) and an interactive dashboard
**All figures are in INR.** K = thousand, M = million.

## 1. Business question
Task 2 showed that order value depends only on price and quantity, and that the top 20% of orders carry 47% of revenue. This deep-dive asks: **which kinds of orders drive the revenue, how stable are they, and who are the buyers?**

## 2. Why segmentation, and why by business rules
- **Cohort and retention analysis was not possible.** 895 of the 947 distinct Customer_IDs appear only once, and the 52 IDs that repeat (105 orders) show different names, ages, genders or cities on different orders, so they are not reliable people. There is too little repeat behaviour to build a retention curve.
- **Funnel analysis was not possible.** There is no visit, cart or checkout data.
- **Segmentation works at order level**, so it needs no customer identity. Business rules were used instead of clustering because price and quantity are almost uniform and independent; a clustering algorithm would split them into arbitrary slices, while two business rules give segments a manager can explain.

## 3. Segment definitions
Each order is placed in one of four segments using two rules:

| | **Bulk** (6-10 units) | **Light** (1-5 units) |
|---|---|---|
| **Premium** (unit price at or above the median, Rs 25,399) | Premium Bulk | Premium Light |
| **Value** (unit price below the median) | Value Bulk | Value Light |

## 4. Results

![Segments](charts/01_segment_orders_vs_revenue.png)

| Segment | Orders | % of orders | Revenue (M) | % of revenue | Avg order value | Revenue per order vs average |
|---|---|---|---|---|---|---|
| **Premium Bulk** | 242 | 24.2% | 73.2 | **52.5%** | 302,346 | 2.2x |
| Premium Light | 258 | 25.8% | 29.5 | 21.1% | 114,176 | 0.8x |
| Value Bulk | 239 | 23.9% | 26.1 | 18.7% | 109,272 | 0.8x |
| Value Light | 261 | 26.1% | 10.7 | 7.6% | 40,836 | 0.3x |

**Findings**
1. **One segment, half the revenue.** Premium Bulk is a quarter of the orders but 52.5% of revenue. Each of its orders is worth about 2.2 times the average. All 19 high-value orders from Task 2 sit in this segment.
2. **Value Light is a quarter of the orders but 7.6% of revenue.** Its average order is Rs 40.8K, about a seventh of a Premium Bulk order. Cost-to-serve is not in the data, so whether these orders are profitable is unknown.
3. **Both rules matter together.** High price alone (Premium Light) or high quantity alone (Value Bulk) gives about 110-115K per order, 0.8 times the average. Only the combination reaches 302K.

![Map](charts/02_segment_map.png)

### 4.1 Is the pattern stable over time?

![By quarter](charts/03_segment_share_by_quarter.png)

| Quarter | Premium Bulk revenue (M) | Share of quarter revenue |
|---|---|---|
| Q1 | 17.9 | 51.5% |
| Q2 | 20.0 | 55.4% |
| Q3 | 14.6 | 48.2% |
| Q4 | 20.4 | 54.4% |

- Premium Bulk stays between 48% and 55% of revenue every quarter, so the finding is not a one-quarter fluke.
- **The Q3 dip comes almost entirely from this segment.** Total revenue fell Rs 5.74M from Q2 to Q3, and Premium Bulk fell Rs 5.37M of that (93.6%). The other three segments barely moved. Premium Bulk gets only about 60 orders per quarter (13 to 25 per month), so a handful of orders can swing a quarter. Treat this as a lead to check against next quarter's data.

### 4.2 Who are the Premium Bulk buyers?

Chi-square tests of segment against customer and product attributes:

| Attribute | Chi-square | p-value | Cramer's V | Reading |
|---|---|---|---|---|
| Category | 13.9 (12 dof) | 0.31 | 0.07 | no association |
| City | 16.1 (21 dof) | 0.77 | 0.07 | no association |
| Age group | 18.8 (12 dof) | 0.093 | 0.08 | not significant at 5% (borderline) |
| Gender | 1.6 (3 dof) | 0.66 | 0.04 | no association |

- Premium Bulk revenue is spread across every category, with the same Electronics lead as the company overall (36% of its revenue vs 36.4% overall). It is 59% of Grocery revenue and 46% of Fashion revenue; Fashion has more Premium Light orders (29%).
- **Demographics do not identify these buyers.** The segment is defined by what happens in the order, so it can only be spotted at order time (basket size and item price), not through age, gender, city or category.

### 4.3 How exposed is the business?
If Premium Bulk revenue fell by 10%, total revenue would fall by about 5.2%. Without this segment, revenue would be 47.5% of today's.

## 5. Recommendations
1. **Protect the Premium Bulk segment.** Watch its orders weekly (the normal range is 13-25 per month), keep high-price items in stock, and offer large buyers bundle or volume terms.
2. **Find out what happened to Premium Bulk in Aug-Sep.** It explains almost the whole Q3 dip. Check stock-outs, pricing and lost large buyers before the next quarter.
3. **Move Value Light buyers up.** Suggest a second unit or a bundle at checkout to lift single low-price orders towards the Value Bulk level (about 109K per order).
4. **Do not look for these buyers through demographics.** Trigger offers from the basket (price and quantity) instead.
5. **Add cost-to-serve and customer data** (margin per order, a reliable customer key). Without them, profitability and retention questions stay unanswered.

## 6. Interactive dashboard
`dashboard.html` (also published as a hosted page) lets viewers:
- filter by month range, city, category, gender, age group or segment;
- click a segment card, or a category or city bar, to filter everything else;
- see the five KPIs update with the filters;
- compare orders share and revenue share per segment, monthly revenue split by segment, and the segment mix inside each category.

The dashboard computes everything in the browser from `outputs/dashboard_data.json`, using the same rules as this report. At the start it shows 52.5% for Premium Bulk, matching the table above.

## 7. Limitations
- The data looks simulated (flat distributions, prices from about 150 to 50,000 for every product), so the segment results demonstrate the method more than they describe a real business.
- The median split on price and the 6-unit split on quantity are reasonable but not the only choices; different cut points would change the percentages, though not the idea that the combination matters.
- Age-group results exclude 20 orders whose age was filled in during Task 1; 13 orders have an unknown city.
- Filters that leave fewer than 30 orders give unstable percentages; the dashboard warns when that happens.
