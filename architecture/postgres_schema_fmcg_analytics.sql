-- PostgreSQL schema for FMCG AI Analytics Assistant

-- 1. Core tables

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    pack_size_ml INTEGER NOT NULL,
    launch_date DATE,
    base_price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_name TEXT NOT NULL,
    region TEXT NOT NULL,
    sub_region TEXT,
    channel TEXT NOT NULL,
    store_format TEXT NOT NULL,
    area_type TEXT,
    market_size TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sales_promotions (
    sales_promo_id BIGSERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    promo_active BOOLEAN NOT NULL DEFAULT FALSE,
    promo_type TEXT,
    promo_start_date DATE,
    promo_end_date DATE,
    discount_pct NUMERIC(5,2) DEFAULT 0,
    units_sold INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    sales_value NUMERIC(14,2) NOT NULL,
    cost NUMERIC(14,2) NOT NULL,
    gross_margin NUMERIC(14,2) NOT NULL,
    stockout BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES stores (store_id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE TABLE inventory (
    inventory_id BIGSERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    opening_qty INTEGER NOT NULL,
    received_qty INTEGER NOT NULL,
    sold_qty INTEGER NOT NULL,
    closing_qty INTEGER NOT NULL,
    shrinkage_qty INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) REFERENCES stores (store_id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    role TEXT NOT NULL,
    region TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE chat_history (
    chat_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_message TEXT,
    intent TEXT,
    entities JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_chat_user FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE generated_reports (
    report_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    report_name TEXT NOT NULL,
    report_type TEXT,
    parameters JSONB,
    result_summary TEXT,
    report_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_report_user FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- 2. Indexes for analytics and AI querying

CREATE INDEX idx_sales_week_product_store ON sales_promotions (week_start, product_id, store_id);
CREATE INDEX idx_sales_region_week ON sales_promotions (region, week_start);
CREATE INDEX idx_sales_promo_active ON sales_promotions (promo_active);
CREATE INDEX idx_inventory_week_product_store ON inventory (week_start, product_id, store_id);
CREATE INDEX idx_products_category ON products (category);
CREATE INDEX idx_stores_region ON stores (region);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_chat_session ON chat_history (session_id);
CREATE INDEX idx_reports_user ON generated_reports (user_id);

-- 3. Materialized views for common analytics patterns

CREATE MATERIALIZED VIEW mv_promo_performance AS
SELECT
    p.category,
    s.region,
    sp.week_start,
    SUM(sp.sales_value) AS total_sales,
    SUM(sp.units_sold) AS total_units,
    AVG(sp.discount_pct) AS avg_discount,
    SUM(CASE WHEN sp.promo_active THEN sp.sales_value ELSE 0 END) AS promo_sales,
    SUM(CASE WHEN sp.promo_active THEN sp.units_sold ELSE 0 END) AS promo_units
FROM sales_promotions sp
JOIN products p ON sp.product_id = p.product_id
JOIN stores s ON sp.store_id = s.store_id
GROUP BY p.category, s.region, sp.week_start;

CREATE MATERIALIZED VIEW mv_inventory_turn AS
SELECT
    i.store_id,
    i.product_id,
    i.week_start,
    (CASE WHEN (i.opening_qty + i.received_qty) > 0 THEN (i.sold_qty::NUMERIC / ((i.opening_qty + i.received_qty) / 2.0)) ELSE NULL END) AS inventory_turn,
    i.closing_qty
FROM inventory i;

-- 4. Optimization recommendations

-- Use partitioning by week_start for sales_promotions and inventory when data grows large.
-- If queries are often grouped by region, add a denormalized region field to sales_promotions and inventory.
-- Keep product and store master dimension tables small and use foreign keys with referential integrity.
-- Use JSONB fields in chat_history and generated_reports only for metadata and query context, not for primary analytics.
-- Refresh materialized views on a schedule aligned to data ingestion.
-- For high-cardinality time-series metrics, create aggregate tables for monthly, regional, and category rollups.

-- 5. Star schema considerations

-- Fact tables:
--   - sales_promotions (sales + promotion event facts)
--   - inventory (inventory movement facts)
-- Dimension tables:
--   - products
--   - stores
--   - users (analytics users and access context)
--   - time dimension can be added optionally for richer date hierarchies.

-- Example time dimension table for drill-downs and easier analytical filtering:
CREATE TABLE dim_time (
    time_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day INTEGER NOT NULL,
    weekday TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Use the dim_time table to replace week_start in analytical queries if needed.

-- 6. Query optimization notes

-- Recommended queries:
--   - Use explicit joins between fact tables and master dimension tables.
--   - Filter by week_start and region early to leverage indexes.
--   - Avoid SELECT * on large fact tables; project only needed metrics.
--   - Use CTEs or materialized views for repeated multi-step analytics.
--   - For AI-driven SQL generation, validate generated predicates and maintain a whitelist of allowed columns.

-- Ensure RLS policies or view-based access control for users with restricted regional visibility.
