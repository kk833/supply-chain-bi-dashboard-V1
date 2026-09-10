import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

os.makedirs("charts", exist_ok=True)

m = pd.read_csv("data/sku_metrics.csv")
p = pd.read_csv("data/products.csv")

# ---- Chart 1: Top10 滞销SKU占用资金 ----
slow = m[m["is_slow_moving"] == "Y"].copy()
slow = slow.merge(p[["sku_id", "unit_cost"]], on="sku_id")
slow["frozen_value"] = slow["avg_stock"] * slow["unit_cost"]
slow = slow.sort_values("frozen_value", ascending=False).head(10)

plt.figure(figsize=(10, 5))
plt.bar(slow["sku_id"], slow["frozen_value"], color="crimson")
plt.title("Top 10 Slow-Moving SKUs by Frozen Capital (CNY)")
plt.xlabel("SKU")
plt.ylabel("Frozen Value (CNY)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/chart1_frozen_value.png", dpi=150)
plt.close()

# ---- Chart 2: 正常商品里周转天数Top10 ----
active = m[m["is_slow_moving"] == "N"].copy()
active = active[active["dio_days"].notna()]
top_dio = active.sort_values("dio_days", ascending=False).head(10)

plt.figure(figsize=(10, 5))
plt.bar(top_dio["sku_id"], top_dio["dio_days"], color="orange")
plt.axhline(30, color="green", linestyle="--", label="30-day benchmark")
plt.title("Top 10 Active SKUs by Inventory Turnover Days")
plt.xlabel("SKU")
plt.ylabel("DIO (days)")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("charts/chart2_dio.png", dpi=150)
plt.close()

# ---- Chart 3: 缺货天数Top10 ----
zero = m[m["zero_stock_days"] > 0].sort_values("zero_stock_days", ascending=False).head(10)

plt.figure(figsize=(10, 5))
plt.bar(zero["sku_id"], zero["zero_stock_days"], color="steelblue")
plt.title("Top SKUs by Zero-Stock Days (Last 7 Days)")
plt.xlabel("SKU")
plt.ylabel("Zero-Stock Days")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/chart3_zero_stock.png", dpi=150)
plt.close()

# ---- Chart 4: 滞销资金按品类汇总 ----
slow_all = m[m["is_slow_moving"] == "Y"].copy()
slow_all = slow_all.merge(p[["sku_id", "unit_cost"]], on="sku_id")
slow_all["frozen_value"] = slow_all["avg_stock"] * slow_all["unit_cost"]
cat = slow_all.groupby("category")["frozen_value"].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(cat.index, cat.values, color="purple")
plt.title("Frozen Capital by Category (Slow-Moving)")
plt.xlabel("Category")
plt.ylabel("Frozen Value (CNY)")
plt.tight_layout()
plt.savefig("charts/chart4_category.png", dpi=150)
plt.close()

# ---- 汇总 ----
total_frozen = slow_all["frozen_value"].sum()
print("DONE")
print("Total frozen capital (slow-moving):", round(total_frozen, 0), "CNY")
print("Charts saved to charts/ folder:")
for f in os.listdir("charts"):
    print(" -", f)