#!/bin/bash

echo "🏥 Starting Health & Wellness Predictor Backend..."
echo "=================================================="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""

# Kill any existing process on port 8000
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the backend
echo "🚀 Starting FastAPI backend on http://localhost:8000..."
echo ""
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
