# Rebuilding the dashboard in a BI tool (optional)

The dashboard in this repo is a custom interactive web page (`dashboard.html`). The task brief names Tableau, Power BI and Looker Studio as examples of BI tools. If you need the dashboard in one of them, use the file `outputs/orders_with_segments.csv`: it already holds one row per order with the Segment column, so no extra preparation is needed.

## Looker Studio (free, runs in the browser)
1. Upload `orders_with_segments.csv` to Google Sheets, then in Looker Studio choose **Create > Report > Google Sheets**.
2. Set `Order_Date` to type **Date (YYYYMMDD / ISO)** and `Total_Sales` to a number.
3. Add a **Date range control**, and drop-down controls for `City`, `Category`, `Gender`, `Age_Group` and `Segment`.
4. Scorecards (create calculated fields where needed):
   - Total revenue: `SUM(Total_Sales)`
   - Orders: `COUNT(Order_ID)`
   - AOV: `SUM(Total_Sales) / COUNT(Order_ID)`
   - Top-20% concentration: not available as a one-click metric; show it in the report instead, or pre-compute it in Python.
5. Charts: time series of `Total_Sales` by month, split by `Segment` (stacked column); bar charts of revenue by `Category` and by `City`; a table with `Segment`, `COUNT(Order_ID)`, `SUM(Total_Sales)`, and a percent-of-total column.
6. In the chart settings, enable **Cross-filtering** so clicking a bar filters the other charts.
7. Share > **Manage access** > anyone with the link can view; copy the link into your submission.

## Power BI Desktop
1. **Get data > Text/CSV**, choose `orders_with_segments.csv`, set `Order_Date` to Date.
2. DAX measures:
   - `Revenue = SUM(orders[Total_Sales])`
   - `Orders = COUNTROWS(orders)`
   - `AOV = DIVIDE([Revenue], [Orders])`
   - `Segment revenue share = DIVIDE([Revenue], CALCULATE([Revenue], ALL(orders[Segment])))`
3. Add slicers for date, city, category, gender, age group and segment, and cards, a stacked column chart by month and segment, and bar charts.
4. Publishing a live link needs a Power BI account (publish to web).

## Tableau Public
1. Connect to the CSV, drag `Order_Date` (month) to Columns and `SUM(Total_Sales)` to Rows, and colour by `Segment`.
2. Build the same bar charts on new sheets, put them on a dashboard, and add filters; click **Use as Filter** on each chart.
3. Save to Tableau Public to get a shareable link.
