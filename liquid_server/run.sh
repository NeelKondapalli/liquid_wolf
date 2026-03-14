#!/bin/bash

# Liquid Wolf Server - Run Script

echo "Starting Liquid Wolf Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Run the server
echo ""
PORT=${PORT:-8000}
echo "Server starting on http://localhost:$PORT"
echo "Press Ctrl+C to stop"
echo ""

python -m app.main
