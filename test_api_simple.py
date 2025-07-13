#!/usr/bin/env python3
"""
Quick test to verify the API works with the exact documentation example
"""

from gradio_client import Client

try:
    print("🔗 Creating client...")
    client = Client("duchaba/Friendly_Text_Moderation")
    
    print("📡 Testing API...")
    result = client.predict(
        msg="Hello!!",
        safer=0.02,
        api_name="/fetch_toxicity_level"
    )
    
    print("✅ Success!")
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if len(result) >= 2:
        print(f"Chart data: {type(result[0])}")
        print(f"JSON output: {result[1]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
