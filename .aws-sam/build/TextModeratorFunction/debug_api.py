#!/usr/bin/env python3
"""
Debug script to test the Duc Haba API connection
"""

import os
import sys
from gradio_client import Client
import requests
import json

def test_gradio_client():
    """Test the Gradio client connection"""
    print("🔍 Testing Gradio Client Connection...")
    
    try:
        # Try to initialize the client
        client = Client("duchaba/Friendly_Text_Moderation")
        print("✅ Successfully connected to duchaba/Friendly_Text_Moderation")
        
        # Test with a simple message
        test_text = "Hello world, this is a test message."
        print(f"📝 Testing with text: '{test_text}'")
        
        result = client.predict(
            msg=test_text,
            safer=0.02,
            api_name="/fetch_toxicity_level"
        )
        
        print("✅ API call successful!")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        print(f"📊 Result: {result}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Error with Gradio client: {e}")
        return False, str(e)

def test_alternative_api():
    """Test alternative API approaches"""
    print("\n🔄 Testing Alternative API Approaches...")
    
    # Try direct HuggingFace Inference API
    try:
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
        if hf_token:
            print(f"🔑 Using HF Token: {hf_token[:10]}...")
            
            # Test with HuggingFace Inference API
            headers = {"Authorization": f"Bearer {hf_token}"}
            api_url = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
            
            response = requests.post(
                api_url, 
                headers=headers, 
                json={"inputs": "Hello world, this is a test."}
            )
            
            print(f"📡 HF API Response Status: {response.status_code}")
            if response.status_code == 200:
                print(f"📊 HF API Response: {response.json()}")
            else:
                print(f"❌ HF API Error: {response.text}")
        else:
            print("❌ No HuggingFace token found")
            
    except Exception as e:
        print(f"❌ Error with HF API: {e}")

def check_environment():
    """Check environment setup"""
    print("\n🔧 Environment Check...")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check required packages
    try:
        import gradio_client
        print(f"✅ gradio_client version: {gradio_client.__version__}")
    except ImportError as e:
        print(f"❌ gradio_client not found: {e}")
    
    try:
        import requests
        print(f"✅ requests version: {requests.__version__}")
    except ImportError as e:
        print(f"❌ requests not found: {e}")
    
    # Check environment variables
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    if hf_token:
        print(f"✅ HUGGINGFACE_TOKEN found: {hf_token[:10]}...")
    else:
        print("❌ HUGGINGFACE_TOKEN not found")

def test_gradio_space_availability():
    """Check if the Gradio space is available"""
    print("\n🌐 Testing Gradio Space Availability...")
    
    try:
        space_url = "https://huggingface.co/spaces/duchaba/Friendly_Text_Moderation"
        response = requests.get(space_url, timeout=10)
        
        print(f"📡 Space URL Response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Gradio space appears to be accessible")
        else:
            print(f"⚠️ Gradio space returned status: {response.status_code}")
            
        # Check if it's running
        api_url = "https://duchaba-friendly-text-moderation.hf.space/"
        try:
            api_response = requests.get(api_url, timeout=10)
            print(f"📡 API URL Response: {api_response.status_code}")
        except Exception as e:
            print(f"❌ API URL error: {e}")
            
    except Exception as e:
        print(f"❌ Error checking space: {e}")

if __name__ == "__main__":
    print("🚀 Text Moderator API Debug Tool\n" + "="*50)
    
    check_environment()
    test_gradio_space_availability()
    test_gradio_client()
    test_alternative_api()
    
    print("\n" + "="*50)
    print("🔧 Debug complete! Check the output above for issues.")
