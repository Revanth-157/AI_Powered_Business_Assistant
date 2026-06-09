import csv
import math
import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "csv")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

CATEGORIES = ["Carbonated", "Juice", "Water", "Dairy", "Energy Drinks"]
STORE_FORMATS = ["Hypermarket", "Supermarket", "Convenience", "Discounters"]
REGIONS = ["North", "South", "East", "West"]

WEEKS = 24
START_DATE = datetime.today() - timedelta(days=7 * WEEKS)

PRODUCTS = []
STORES = []
SALES_PROMO_ROWS = []
INVENTORY_ROWS = []

price_base = {
    "Carbonated": 1.5,
    "Juice": 2.2,
    "Water": 1.0,
    "Dairy": 2.5,
    "Energy Drinks": 2.8,
}

promo_types = ["Discount", "Bundle", "Feature", "Loyalty"]

# Product Master
for product_id in range(1, 21):
    category = random.choice(CATEGORIES)
    brand = fake.company().split()[0]
    product_name = f"{brand} {category[:3].upper()} {product_id}"
    pack_size = random.choice([250, 330, 500, 750, 1000])
    price = round(price_base[category] * (1 + random.uniform(-0.1, 0.15)), 2)
    launch_date = START_DATE - timedelta(days=random.randint(30, 365))
    PRODUCTS.append(
        {
            "product_id": product_id,
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "sub_category": f"{category} {random.choice(["Regular", "Premium", "Organic"])}",
            "pack_size_ml": pack_size,
            "launch_date": launch_date.date().isoformat(),
            "base_price": price,
        }
    )

# Store Master
for store_id in range(1, 51):
    region = REGIONS[(store_id - 1) % len(REGIONS)]
    store_format = random.choices(
        population=STORE_FORMATS,
        weights=[0.2, 0.4, 0.25, 0.15],
        k=1,
    )[0]
    name = f"{region[:2].upper()} {store_format[:3].upper()} {store_id}"
    area_type = random.choice(["Urban", "Suburban", "Rural"])
    market_size = random.choice(["Small", "Medium", "Large"])
    STORES.append(
        {
            "store_id": store_id,
            "store_name": name,
            "region": region,
            "sub_region": f"{region} Zone {random.randint(1, 4)}",
            "channel": store_format,
            "store_format": store_format,
            "area_type": area_type,
            "market_size": market_size,
        }
    )

# Seasonal and store behavior factors
region_seasonality = {
    "North": [1.1, 1.05, 1.0, 0.95, 0.9, 0.95, 1.0, 1.05, 1.15, 1.2, 1.25, 1.2],
    "South": [1.0, 1.02, 1.05, 1.1, 1.15, 1.2, 1.18, 1.15, 1.1, 1.05, 1.0, 0.95],
    "East": [0.95, 1.0, 1.05, 1.12, 1.18, 1.22, 1.2, 1.15, 1.1, 1.05, 1.0, 0.97],
    "West": [1.05, 1.1, 1.08, 1.0, 0.95, 0.9, 0.92, 0.96, 1.02, 1.08, 1.12, 1.15],
}

store_format_factor = {
    "Hypermarket": 1.25,
    "Supermarket": 1.0,
    "Convenience": 0.75,
    "Discounters": 0.9,
}

category_popularity = {
    "Carbonated": 1.0,
    "Juice": 1.1,
    "Water": 1.2,
    "Dairy": 0.85,
    "Energy Drinks": 0.95,
}

# create promotion calendar and sales
for week_idx in range(WEEKS):
    week_start = START_DATE + timedelta(days=7 * week_idx)
    week_label = week_start.date().isoformat()
    month_index = week_start.month - 1

    for store in STORES:
        region = store["region"]
        store_factor = store_format_factor[store["store_format"]]
        regional_factor = region_seasonality[region][month_index]

        for product in PRODUCTS:
            category = product["category"]
            base_demand = 20 + category_popularity[category] * 15
            store_scale = store_factor * (1.2 if store["market_size"] == "Large" else 1.0)
            category_season = regional_factor * (1.2 if category == "Water" and month_index in [5, 6, 7] else 1.0)
            trend = 1 + 0.01 * week_idx
            noise = random.normalvariate(0, 5)
            expected_units = max(1, int((base_demand + noise) * store_scale * category_season * trend))

            promotion_active = random.random() < 0.18
            promo_type = None
            promo_discount = 0.0
            promo_lift = 1.0
            promo_start = None
            promo_end = None

            if promotion_active:
                promo_type = random.choice(promo_types)
                promo_discount = round(random.uniform(0.08, 0.28), 2)
                promo_duration = random.choice([1, 2, 3])
                promo_start = week_start.date().isoformat()
                promo_end = (week_start + timedelta(days=7 * (promo_duration - 1))).date().isoformat()
                promo_lift = 1 + promo_discount * random.uniform(0.9, 1.8)
                expected_units = int(expected_units * promo_lift)

            if store["store_format"] == "Convenience" and category == "Dairy":
                expected_units = max(1, int(expected_units * 0.85))
            if store["store_format"] == "Discounters" and category == "Energy Drinks":
                expected_units = max(1, int(expected_units * 0.7))

            stockout = random.random() < 0.03
            sold_units = expected_units if not stockout else max(0, expected_units - random.randint(5, 20))
            opening_qty = max(sold_units + random.randint(5, 20), 10)
            received_qty = max(int(opening_qty * random.uniform(0.7, 1.5)), opening_qty)
            closing_qty = max(opening_qty + received_qty - sold_units, 0)
            if closing_qty == 0 and not stockout:
                stockout = True

            unit_price = round(product["base_price"] * (1 - promo_discount), 2)
            sales_value = round(sold_units * unit_price, 2)
            cost = round(sales_value * random.uniform(0.55, 0.7), 2)
            gross_margin = round(sales_value - cost, 2)

            SALES_PROMO_ROWS.append(
                {
                    "week_start": week_label,
                    "store_id": store["store_id"],
                    "product_id": product["product_id"],
                    "category": category,
                    "region": region,
                    "channel": store["channel"],
                    "promo_active": int(promotion_active),
                    "promo_type": promo_type or "None",
                    "promo_start_date": promo_start,
                    "promo_end_date": promo_end,
                    "discount_pct": promo_discount,
                    "units_sold": sold_units,
                    "unit_price": unit_price,
                    "sales_value": sales_value,
                    "cost": cost,
                    "gross_margin": gross_margin,
                    "stockout": int(stockout),
                }
            )

            INVENTORY_ROWS.append(
                {
                    "week_start": week_label,
                    "store_id": store["store_id"],
                    "product_id": product["product_id"],
                    "opening_qty": opening_qty,
                    "received_qty": received_qty,
                    "sold_qty": sold_units,
                    "closing_qty": closing_qty,
                    "shrinkage_qty": max(0, int(received_qty * random.uniform(0.0, 0.03))),
                }
            )

# Export CSVs
product_df = pd.DataFrame(PRODUCTS)
store_df = pd.DataFrame(STORES)

sales_promo_df = pd.DataFrame(SALES_PROMO_ROWS)
inventory_df = pd.DataFrame(INVENTORY_ROWS)

product_df.to_csv(os.path.join(OUTPUT_DIR, "product_master.csv"), index=False)
store_df.to_csv(os.path.join(OUTPUT_DIR, "store_master.csv"), index=False)
sales_promo_df.to_csv(os.path.join(OUTPUT_DIR, "sales_promotions.csv"), index=False)
inventory_df.to_csv(os.path.join(OUTPUT_DIR, "inventory.csv"), index=False)

print(f"Exported CSV files to {OUTPUT_DIR}")
