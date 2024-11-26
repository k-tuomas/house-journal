#!/bin/sh
set -e

echo "Starting entrypoint script..."

# Run the database migration and populate scripts
flask db init && echo "db init done"
flask db migrate && echo "db migrate done"
flask db upgrade && echo "db upgrade done"
python populate_db.py && echo "populate db done"

exec flask run --host=0.0.0.0 --port=5000 --debug
