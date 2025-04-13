#!/bin/sh
# entrypoint.sh

# Install dependencies in the mounted backend volume
poetry install --no-root

# Start Uvicorn server
exec poetry run uvicorn --host 0.0.0.0 --port 8080 --reload backend.main:app
