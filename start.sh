#!/bin/bash
echo "Starting application on PORT=$PORT"
gunicorn --workers=2 --threads=4 --timeout=120 --bind="0.0.0.0:$PORT" app:app
