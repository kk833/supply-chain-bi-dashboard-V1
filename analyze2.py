import duckdb

con = duckdb.connect()

print("=== R1: 近30天周转天数（死货会显示为 无穷/空）===")
r1 = """
WITH recent_sales AS (
  SELECT sku_id, SUM(qty) AS qty_30d
  FROM 'data/orders.csv'
  WHERE order_date >= DATE '2025-03-01'
  GROUP BY sku_id
),
inv AS (
  SELECT sku_id, AVG(on_hand_qty) AS avg_stock
  FROM 'data/inventory.csv'
  GROUP BY sku_id
)
SELECT p.sku_id,
       p.category,
       COALESCE(r.qty_30d, 0) AS qty_30d,
       ROUND(i.avg_stock, 1) AS avg_stock,
       ROUND(i.avg_stock / NULLIF(COALESCE(r.qty_30d, 0) / 30.0, 0), 1) AS dio_30d
FROM 'data/products.csv' p
LEFT JOIN recent_sales r ON p.sku_id = r.sku_id
LEFT JOIN inv i ON p.sku_id = i.sku_id
ORDER BY dio_30d DESC NULLS FIRST
LIMIT 15
"""
print(con.execute(r1).df())

print()
print("=== R2: 最该补货的SKU（近7天缺货>=2天 且 总销量>50）===")
r2 = """
WITH sales AS (
  SELECT sku_id, SUM(qty) AS total_qty
  FROM 'data/orders.csv'
  GROUP BY sku_id
),
zero AS (
  SELECT sku_id, COUNT(*) FILTER (WHERE on_hand_qty = 0) AS zero_days
  FROM 'data/inventory.csv'
  WHERE snapshot_date >= DATE '2025-03-25'
  GROUP BY sku_id
)
SELECT p.sku_id,
       p.category,
       s.total_qty,
       z.zero_days
FROM 'data/products.csv' p
JOIN sales s ON p.sku_id = s.sku_id
JOIN zero z ON p.sku_id = z.sku_id
WHERE z.zero_days >= 2 AND s.total_qty > 50
ORDER BY z.zero_days DESC, s.total_qty DESC
LIMIT 15
"""
print(con.execute(r2).df())

print()
print("=== R3: 滞销库存占压资金（按金额从高到低）===")
r3 = """
WITH inv AS (
  SELECT sku_id, AVG(on_hand_qty) AS avg_stock
  FROM 'data/inventory.csv'
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
       p.category,
       ROUND(i.avg_stock, 1) AS avg_stock,
       p.unit_cost,
       ROUND(i.avg_stock * p.unit_cost, 0) AS frozen_value
FROM 'data/products.csv' p
JOIN inv i ON p.sku_id = i.sku_id
JOIN slow sl ON p.sku_id = sl.sku_id
ORDER BY frozen_value DESC
LIMIT 15
"""
print(con.execute(r3).df())