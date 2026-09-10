import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

np.random.seed(42)

os.makedirs("data", exist_ok=True)

n_sku = 80
categories = ["Appliances", "Food", "Beauty", "Baby", "Digital", "Home"]

products = pd.DataFrame({
    "sku_id": [f"SKU{i:04d}" for i in range(1, n_sku + 1)],
    "sku_name": [f"Product_{i:04d}" for i in range(1, n_sku + 1)],
    "category": np.random.choice(categories, n_sku),
    "unit_cost": np.round(np.random.uniform(10, 300, n_sku), 2),
    "unit_price": np.round(np.random.uniform(40, 800, n_sku), 2),
    "lead_time_days": np.random.randint(3, 30, n_sku),
})

sku_price = dict(zip(products["sku_id"], products["unit_price"]))

slow_ids = set(np.random.choice(products["sku_id"], size=15, replace=False))

order_rows = []
start = date(2025, 1, 1)
for day_idx in range(90):
    d = start + timedelta(days=day_idx)
    for sku_id in products["sku_id"]:
        if sku_id in slow_ids and day_idx >= 30:
            continue
        lam = np.random.uniform(0.5, 6.0)
        qty = np.random.poisson(lam)
        if qty > 0:
            order_rows.append({
                "order_id": f"ORD{len(order_rows) + 1:06d}",
                "order_date": d.isoformat(),
                "sku_id": sku_id,
                "qty": qty,
                "unit_price": sku_price[sku_id],
            })

orders = pd.DataFrame(order_rows)

inv_rows = []
for day_idx in range(90):
    d = start + timedelta(days=day_idx)
    for sku_id in products["sku_id"]:
        base = np.random.randint(5, 120)
        if np.random.rand() < 0.04:
            on_hand = 0
        else:
            on_hand = max(0, base + np.random.randint(-15, 15))
        inv_rows.append({
            "snapshot_date": d.isoformat(),
            "sku_id": sku_id,
            "on_hand_qty": on_hand,
            "warehouse": np.random.choice(["WH_A", "WH_B", "WH_C"]),
        })

inventory = pd.DataFrame(inv_rows)

products.to_csv("data/products.csv", index=False)
orders.to_csv("data/orders.csv", index=False)
inventory.to_csv("data/inventory.csv", index=False)

print("DONE")
print("products.csv rows:", len(products))
print("orders.csv rows:", len(orders))
print("inventory.csv rows:", len(inventory))