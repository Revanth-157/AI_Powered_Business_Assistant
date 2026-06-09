import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

schema_path = os.path.join(os.path.dirname(__file__), 'postgres_schema_fmcg_analytics.sql')
print('schema_path=', schema_path)

conn = None
 
# Try DATABASE_URL (DSN) first if provided
database_url = os.environ.get('DATABASE_URL') or os.environ.get('PGCONN')
if database_url:
    try:
        print('Trying DATABASE_URL/PGCONN')
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print('Connected via DATABASE_URL')
    except Exception as e:
        print('DATABASE_URL connect failed:', e)
        conn = None

# Build connection parameter sets and include password if present
password = os.environ.get('PGPASSWORD')
params_list = [
    {'dbname': 'postgres', 'user': 'postgres', 'host': 'localhost', 'port': 5432},
    {
        'dbname': os.environ.get('PGDATABASE', 'postgres'),
        'user': os.environ.get('PGUSER', 'postgres'),
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': int(os.environ.get('PGPORT', 5432)),
    },
]
for params in params_list:
    if password:
        params['password'] = password
    try:
        print('Trying connection with', {k: v for k, v in params.items() if k != 'password'})
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print('Connected successfully')
        break
    except Exception as e:
        print('Connection failed:', e)
        conn = None

if conn is None:
    print('\nCould not connect to PostgreSQL with the attempted parameters.')
    print('Options:')
    print(" - Export environment variables: PGPASSWORD, PGUSER, PGHOST, PGPORT, PGDATABASE")
    print(" - Set DATABASE_URL (example: postgres://user:pass@host:5432/dbname)")
    print(" - Ensure the Postgres server is running and reachable")
    raise SystemExit('Connection failed')

cur = conn.cursor()
with open(schema_path, 'r', encoding='utf-8') as f:
    sql_text = f.read()

try:
    cur.execute(sql_text)
    print('Schema executed successfully')
except Exception as e:
    print('Execution failed:', e)
    conn.rollback()
finally:
    cur.close()
    conn.close()
