#!/bin/bash

echo "🚀 Running Text Moderator API Debug..."
echo "=========================================="

cd /Users/evehwang/GitHub/text-moderator-app

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📁 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found"
fi

# Run the debug script
echo "🔍 Running debug script..."
python debug_api.py

echo "=========================================="
echo "✅ Debug complete!"
