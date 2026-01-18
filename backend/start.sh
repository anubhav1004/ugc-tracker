#!/bin/bash
# Start script for Railway deployment

# Install dependencies if needed
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Start uvicorn server
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
