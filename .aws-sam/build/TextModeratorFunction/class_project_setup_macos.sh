#!/bin/bash

echo "🎓 Class Project - Duc Haba API Only (macOS Fixed)"
echo "================================================="
echo "📋 STRICT COMPLIANCE: Only using duchaba/Friendly_Text_Moderation"
echo ""

cd /Users/evehwang/GitHub/text-moderator-app

# Check which Python command works
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Using python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Using python"
else
    echo "❌ No Python found! Please install Python 3"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # After activation, try to use python directly
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
        echo "✅ Virtual environment activated, using python"
    fi
else
    echo "❌ Virtual environment not found. Creating one..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    PYTHON_CMD="python"
fi

# Install required packages
echo "📥 Installing required packages..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install gradio-client flask flask-cors python-dotenv requests

echo ""
echo "🔍 Running Duc Haba API Diagnostics..."
$PYTHON_CMD duc_haba_diagnostics.py

echo ""
echo "================================================="
echo "✅ Setup complete!"
echo ""
echo "🚀 To run your strictly compliant app:"
echo "   $PYTHON_CMD backend/app_duc_haba_only.py"
echo ""
echo "🌐 Then visit: http://localhost:8000"
echo ""
echo "📋 This app ONLY uses Duc Haba's API as required for your class project."
