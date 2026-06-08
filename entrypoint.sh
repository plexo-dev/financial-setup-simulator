#!/bin/sh
set -e
if [ -d /app/static/bi_cache ]; then
    find /app/static/bi_cache -type d -exec chmod u+rwx {} + 2>/dev/null || true
    find /app/static/bi_cache -type f -exec chmod u+rw {} + 2>/dev/null || true
fi
exec gunicorn -c gunicorn.conf.py app:app
