import pandas as pd
import numpy as np

orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])
products = pd.read_csv("data/products.csv")

# 关键修正：用"所有日期"做底，没销售的天补 0，不能跳过
all_days = pd.DataFrame({"order_date": pd.date_range(
    orders["order_date"].min(), orders["order_date"].max())})

sku_list = pd.DataFrame({"sku_id": products["sku_id"].unique()})

base = all_days.merge(sku_list, how="cross")

daily = orders.groupby(["order_date", "sku_id"])["qty"].sum().reset_index()

full = base.merge(daily, on=["order_date", "sku_id"], how="left")
full["qty"] = full["qty"].fillna(0)

# 日均需求 + 需求波动（标准差）
stats = full.groupby("sku_id")["qty"].agg(["mean", "std"]).reset_index()
stats.columns = ["sku_id", "daily_mean", "daily_std"]
stats["daily_std"] = stats["daily_std"].fillna(0)

stats = stats.merge(products[["sku_id", "lead_time_days", "unit_cost"]], on="sku_id")

# 安全库存 = Z * 波动 * sqrt(提前期)，95% 服务水平 Z=1.65
Z = 1.65
stats["safety_stock"] = np.ceil(Z * stats["daily_std"] * np.sqrt(stats["lead_time_days"]))

# 再订货点 = 日均需求 * 提前期 + 安全库存
stats["reorder_point"] = np.ceil(stats["daily_mean"] * stats["lead_time_days"] + stats["safety_stock"])

# 预测：最近 7 天平均
last7 = full[full["order_date"] >= full["order_date"].max() - pd.Timedelta(days=6)]
ma7 = last7.groupby("sku_id")["qty"].mean().reset_index()
ma7.columns = ["sku_id", "forecast_next"]
stats = stats.merge(ma7, on="sku_id", how="left")
stats["forecast_next"] = stats["forecast_next"].fillna(stats["daily_mean"])

stats = stats.sort_values("reorder_point", ascending=False)
print(stats.head(12).to_string(index=False))
stats.to_csv("data/forecast.csv", index=False)
print("")
print("Saved data/forecast.csv, rows:", len(stats))