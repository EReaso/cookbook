#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL not set. Exiting."
  exit 1
fi

python - <<EOF
import os
import sys
import time
from urllib.parse import urlparse

db_url = os.environ["DATABASE_URL"]
parsed = urlparse(db_url)

if parsed.scheme not in ("postgres", "postgresql"):
    print(f"Skipping DB check for non-Postgres DB: {parsed.scheme}")
    sys.exit(0)

host = parsed.hostname or "localhost"
port = parsed.port or 5432

print(f"Checking Postgres TCP connectivity at {host}:{port}...")

import socket
for attempt in range(1, 31):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
        sock.close()
        print(f"Postgres is reachable at {host}:{port}")
        sys.exit(0)
    except Exception as e:
        sock.close()
        print(f"Attempt {attempt}/30: {e}")
        time.sleep(2)

print(f"ERROR: Postgres not reachable at {host}:{port} after 30 attempts")
sys.exit(1)
EOF

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:wsgi_app
