#!/bin/bash

echo "🚀 Text Moderator - Quick Fix & Test Script"
echo "==========================================="

cd /Users/evehwang/GitHub/text-moderator-app

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Test the alternative moderator first
echo ""
echo "🧪 Testing Alternative Moderator..."
python alternative_moderator.py

echo ""
echo "🔍 Testing Current App API Connection..."
python simple_test.py

echo ""
echo "==========================================="
echo "✅ Setup and tests complete!"
echo ""
echo "To run the improved app with fallback:"
echo "  python backend/app_with_fallback.py"
echo ""
echo "To run the original app:"
echo "  python backend/app.py"
echo ""
echo "Then visit: http://localhost:8000"
