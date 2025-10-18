#!/bin/sh

DB_DIR="/app/data" 
DB_FILE="${DB_DIR}/app.db" 
export FLASK_APP=code.app:app

mkdir -p "$DB_DIR"

# 1. Check if the database file already exists.
if [ ! -f "$DB_FILE" ]; then
    echo "Database file not found. Running initialization."
    # 2. Run the initialization command
    flask --app code.app init-db
else
    echo "Database file found. Skipping initialization."
fi

# 3. Execute the original CMD (Gunicorn) from Dockerfile, this will replace the CMD.
exec gunicorn --workers 4 --bind 0.0.0.0:5000 code.app:app