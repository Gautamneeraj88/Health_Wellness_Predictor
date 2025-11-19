#!/bin/bash

echo "🔧 Quick Fix for Installation Issues"
echo "===================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check if cmake is needed
if command -v cmake &> /dev/null; then
    echo "✓ CMake found: $(cmake --version | head -n1)"
else
    echo "⚠️  CMake not found (not needed for this version)"
fi

echo ""
echo "📦 Installing minimal dependencies (no cmake required)..."
echo ""

# Create fresh virtual environment
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

echo "🔨 Creating new virtual environment..."
python3 -m venv venv

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Upgrading pip..."
pip install --upgrade pip --quiet

echo "📦 Installing dependencies..."
echo ""

# Install in stages to show progress
echo "1/4 Installing core libraries..."
pip install numpy pandas scikit-learn joblib --quiet

echo "2/4 Installing ML libraries..."
pip install xgboost lightgbm --quiet

echo "3/4 Installing API framework..."
pip install fastapi uvicorn pydantic[email] --quiet

echo "4/4 Installing security & utilities..."
pip install pyjwt bcrypt python-multipart python-dotenv --quiet

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To start the backend:"
echo "   ./start_backend.sh"
echo ""
