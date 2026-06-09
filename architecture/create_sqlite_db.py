import sqlite3
import pandas as pd
import os

CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'csv')
DB_PATH = os.path.join(os.path.dirname(__file__), 'fmcg_analytics.db')

print('CSV_DIR=', CSV_DIR)
print('DB_PATH=', DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create tables (SQLite types)
cur.executescript('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    brand TEXT,
    category TEXT,
    sub_category TEXT,
    pack_size_ml INTEGER,
    launch_date TEXT,
    base_price REAL
);

CREATE TABLE IF NOT EXISTS stores (
    store_id INTEGER PRIMARY KEY,
    store_name TEXT,
    region TEXT,
    sub_region TEXT,
    channel TEXT,
    store_format TEXT,
    area_type TEXT,
    market_size TEXT
);

CREATE TABLE IF NOT EXISTS sales_promotions (
    sales_promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT,
    store_id INTEGER,
    product_id INTEGER,
    category TEXT,
    region TEXT,
    channel TEXT,
    promo_active INTEGER,
    promo_type TEXT,
    promo_start_date TEXT,
    promo_end_date TEXT,
    discount_pct REAL,
    units_sold INTEGER,
    unit_price REAL,
    sales_value REAL,
    cost REAL,
    gross_margin REAL,
    stockout INTEGER
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT,
    store_id INTEGER,
    product_id INTEGER,
    opening_qty INTEGER,
    received_qty INTEGER,
    sold_qty INTEGER,
    closing_qty INTEGER,
    shrinkage_qty INTEGER
);
''')
conn.commit()

# Load CSVs
files = {
    'product_master.csv': ('products', None),
    'store_master.csv': ('stores', None),
    'sales_promotions.csv': ('sales_promotions', None),
    'inventory.csv': ('inventory', None),
}

for fname, (table, _) in files.items():
    path = os.path.join(CSV_DIR, fname)
    if not os.path.exists(path):
        print('Missing', path)
        continue
    df = pd.read_csv(path)
    # Normalize column names for SQLite
    df.columns = [c.strip() for c in df.columns]
    print(f'Inserting {len(df)} rows into {table} from {fname}')
    df.to_sql(table, conn, if_exists='append', index=False)

conn.commit()
cur.close()
conn.close()
print('Created SQLite DB at', DB_PATH)
