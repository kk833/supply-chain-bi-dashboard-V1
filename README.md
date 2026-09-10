\# Supply Chain Inventory Analysis (SKU-level)



An independent data analysis project: analyzing 80 SKUs over 90 days of

orders and inventory to identify slow-moving stock and stock-out risks.



\## Tools

\- Python (pandas, matplotlib)

\- SQL (DuckDB) — window functions, aggregation, joins

\- CSV data pipeline



\## Data

\- `products.csv` — 80 SKUs, category, unit cost/price, lead time

\- `orders.csv` — \~5,600 order rows over 90 days

\- `inventory.csv` — 7,200 daily stock snapshots



\## Metrics Calculated

\- Inventory turnover days (DIO) = avg stock / daily sales (90-day \& 30-day window)

\- Zero-stock days (last 7 days)

\- Slow-moving flag (no sales in last 60 days)

\- Frozen capital = avg stock x unit cost



\## Key Findings

\- Identified 15 slow-moving SKUs, freezing \~127,881 CNY in capital

\- Top frozen SKU: SKU0040 (\~13.7k CNY)

\- 3 high stock-out risk SKUs (high sales but 2-3 zero-stock days in 7 days)

\- Largest frozen capital by category: Baby



\## Recommendations

\- Clearance priority ranking for slow-moving SKUs

\- Raise safety stock for fast-moving but frequently out-of-stock SKUs



\## How to Run

