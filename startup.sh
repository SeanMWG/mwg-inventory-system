#!/bin/bash

# Apply database migrations
flask db upgrade

# Start Gunicorn server
gunicorn --bind=0.0.0.0:8000 --timeout 120 app:app
