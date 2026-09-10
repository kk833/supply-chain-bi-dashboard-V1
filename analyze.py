import duckdb

con = duckdb.connect()

print("=== Q1: Top 10 SKUs by inventory turnover days (DIO) ===")
q1 = """
WITH sales AS (
  SELECT sku_id, SUM(qty) AS total_qty
  FROM 'data/orders.csv'
  WHERE order_date >= DATE '2025-01-01'
  GROUP BY sku_id
),
inv AS (
  SELECT sku_id, AVG(on_hand_qty) AS avg_stock
  FROM 'data/inventory.csv'
  GROUP BY sku_id
)
SELECT s.sku_id,
       s.total_qty,
       ROUND(i.avg_stock, 1) AS avg_stock,
       ROUND(i.avg_stock / (s.total_qty / 90.0), 1) AS dio_days
FROM sales s
JOIN inv i ON s.sku_id = i.sku_id
ORDER BY dio_days DESC
LIMIT 10
"""
print(con.execute(q1).df())

print()
print("=== Q2: SKUs with zero stock days in last 7 days ===")
q2 = """
SELECT sku_id,
       COUNT(*) FILTER (WHERE on_hand_qty = 0) AS zero_stock_days
FROM 'data/inventory.csv'
WHERE snapshot_date >= DATE '2025-03-25'
GROUP BY sku_id
HAVING COUNT(*) FILTER (WHERE on_hand_qty = 0) > 0
ORDER BY zero_stock_days DESC
LIMIT 10
"""
print(con.execute(q2).df())

print()
print("=== Q3: Slow-moving SKUs (no sales in last 60 days) ===")
q3 = """
SELECT p.sku_id, p.sku_name, p.category
FROM 'data/products.csv' p
LEFT JOIN 'data/orders.csv' o
  ON p.sku_id = o.sku_id AND o.order_date >= DATE '2025-01-31'
WHERE o.sku_id IS NULL
ORDER BY p.sku_id
LIMIT 20
"""
print(con.execute(q3).df())

print()
print("=== FINAL: building data/sku_metrics.csv ===")
final = """
WITH sales AS (
  SELECT sku_id, SUM(qty) AS total_qty
  FROM 'data/orders.csv'
  WHERE order_date >= DATE '2025-01-01'
  GROUP BY sku_id
),
inv AS (
  SELECT sku_id, AVG(on_hand_qty) AS avg_stock
  FROM 'data/inventory.csv'
  GROUP BY sku_id
),
zero AS (
  SELECT sku_id, COUNT(*) FILTER (WHERE on_hand_qty = 0) AS zero_stock_days
  FROM 'data/inventory.csv'
  WHERE snapshot_date >= DATE '2025-03-25'
  GROUP BY sku_id
),
slow AS (
  SELECT p.sku_id, 1 AS is_slow
  FROM 'data/products.csv' p
  LEFT JOIN 'data/orders.csv' o
    ON p.sku_id = o.sku_id AND o.order_date >= DATE '2025-01-31'
  WHERE o.sku_id IS NULL
)
SELECT p.sku_id,
       p.sku_name,
       p.category,
       COALESCE(s.total_qty, 0) AS total_qty_90d,
       ROUND(COALESCE(s.total_qty, 0) / 90.0, 2) AS daily_avg_qty,
       ROUND(i.avg_stock, 1) AS avg_stock,
       ROUND(i.avg_stock / NULLIF(COALESCE(s.total_qty, 0) / 90.0, 0), 1) AS dio_days,
       COALESCE(z.zero_stock_days, 0) AS zero_stock_days,
       CASE WHEN sl.is_slow = 1 THEN 'Y' ELSE 'N' END AS is_slow_moving
FROM 'data/products.csv' p
LEFT JOIN sales s ON p.sku_id = s.sku_id
LEFT JOIN inv i ON p.sku_id = i.sku_id
LEFT JOIN zero z ON p.sku_id = z.sku_id
LEFT JOIN slow sl ON p.sku_id = sl.sku_id
ORDER BY dio_days DESC NULLS LAST
"""
df = con.execute(final).df()
df.to_csv("data/sku_metrics.csv", index=False)
print(df.head(10))
print()
print("Saved data/sku_metrics.csv, rows:", len(df))