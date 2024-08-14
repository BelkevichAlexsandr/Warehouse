#!/bin/bash

echo '=== Waiting for DB ==='
sleep 2

echo '=== Preparing DB ==='
alembic upgrade head 2>&1
echo '=== Database migration successful ==='

echo '=== Run APP ==='
exec uvicorn --host=0.0.0.0 --port=8000 --workers=${UVICORN_WORKERS:-5} app.main:app
