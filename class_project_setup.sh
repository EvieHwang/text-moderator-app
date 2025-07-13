#!/bin/bash

echo "🎓 Class Project - Duc Haba API Only"
echo "===================================="
echo "📋 STRICT COMPLIANCE: Only using duchaba/Friendly_Text_Moderation"
echo ""

cd /Users/evehwang/GitHub/text-moderator-app

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install required packages
echo "📥 Installing required packages..."
pip install --upgrade pip
pip install gradio-client flask flask-cors python-dotenv requests

echo ""
echo "🔍 Running Duc Haba API Diagnostics..."
python duc_haba_diagnostics.py

echo ""
echo "===================================="
echo "✅ Diagnostics complete!"
echo ""
echo "🚀 To run your strictly compliant app:"
echo "   python backend/app_duc_haba_only.py"
echo ""
echo "🌐 Then visit: http://localhost:8000"
echo ""
echo "📋 This app ONLY uses Duc Haba's API as required for your class project."
