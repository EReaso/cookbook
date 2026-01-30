#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL not set. Exiting."
  exit 1
fi

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:wsgi_app
