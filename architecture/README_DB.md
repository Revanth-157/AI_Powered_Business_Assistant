Postgres local setup (Docker)

This project includes a ready-to-run Docker Compose to create a local PostgreSQL instance and initialize the schema.

1) Requirements
- Docker or Docker Desktop installed on your machine

2) Quick start
- Copy `.env.sample` to `.env` and set `POSTGRES_PASSWORD` to your chosen password.

PowerShell commands (run from `architecture` directory):

```powershell
copy .env.sample .env
# edit .env to set POSTGRES_PASSWORD or run:
$env:POSTGRES_PASSWORD = "secretpass"; (Get-Content .env) -replace 'POSTGRES_PASSWORD=.*','POSTGRES_PASSWORD=secretpass' | Set-Content .env
# start DB
docker compose up -d
# wait a few seconds, then check logs
docker compose logs -f db
```

The Compose mounts `postgres-init/001_schema.sql` into `/docker-entrypoint-initdb.d` so Postgres will initialize the schema on first startup.

3) Running the schema against an existing Postgres
If you already have Postgres running and accessible, set `DATABASE_URL` or `PGPASSWORD`/`PGUSER`/`PGHOST`/`PGPORT`/`PGDATABASE` and run:

```powershell
$env:DATABASE_URL = "postgres://postgres:your_password@localhost:5432/postgres"
python .\execute_schema.py
```

4) Import CSV datasets (after DB is up)
Use `psql` (from Docker container) to copy CSVs into tables. Example (PowerShell):

```powershell
# copy CSVs into container
docker cp ..\data\csv\product_master.csv fmcg-postgres:/product_master.csv
# run psql to import
docker compose exec db psql -U postgres -d postgres -c "\copy products(product_id,product_name,brand,category,sub_category,pack_size_ml,launch_date,base_price) FROM '/product_master.csv' WITH CSV HEADER"
```

Repeat for other CSV files, mapping columns correctly.

5) Notes
- If `docker` is not available, install Docker Desktop for Windows.
- If you prefer not to use Docker, provide DB credentials and run `python .\execute_schema.py` from this folder.
