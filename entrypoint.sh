#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL not set. Exiting."
  exit 1
fi

python - <<EOF
import time
import psycopg2
from urllib.parse import urlparse

url = "${DATABASE_URL}"
parsed = urlparse(url)

for _ in range(60):
    try:
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            dbname=parsed.path.lstrip('/'),
        )
        conn.close()
        print("Database is ready!")
        break
    except psycopg2.OperationalError:
        print("Waiting for database...")
        time.sleep(1)
else:
    print("Database not available after 60s")
    exit(1)
EOF

exec gunicorn -b 0.0.0.0:5000 -w 4 "app:app"
