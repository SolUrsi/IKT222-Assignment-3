#!/bin/sh

DB_FILE="/app/data/app.db"

# 1. Check if the database file already exists.
if [ ! -f "$DB_FILE" ]; then
    echo "Database file not found. Running initialization."
    # 2. Run the initialization command
    flask --app code.app init-db
else
    echo "Database file found. Skipping initialization."
fi

# 3. Execute the original CMD (Gunicorn) from Dockerfile, this will replace the CMD.
exec gunicorn --bind 0.0.0.0:5000 code.app:app