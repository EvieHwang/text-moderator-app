"""
Simple test to debug the Text Moderator API issue
"""

import os
import sys
import traceback

# Add the current directory to Python path
sys.path.insert(0, '/Users/evehwang/GitHub/text-moderator-app')

def test_imports():
    """Test if all required packages are available"""
    print("🔍 Testing imports...")
    
    try:
        from gradio_client import Client
        print("✅ gradio_client imported successfully")
    except ImportError as e:
        print(f"❌ gradio_client import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    return True

def test_api_connection():
    """Test the specific API connection"""
    print("\n🔍 Testing API connection...")
    
    try:
        from gradio_client import Client
        
        print("📡 Connecting to duchaba/Friendly_Text_Moderation...")
        client = Client("duchaba/Friendly_Text_Moderation")
        print("✅ Client created successfully")
        
        # Try to get the API info
        print("📊 Testing API call...")
        test_text = "This is a simple test message."
        
        result = client.predict(
            msg=test_text,
            safer=0.02,
            api_name="/fetch_toxicity_level"
        )
        
        print(f"✅ API call successful!")
        print(f"📋 Result type: {type(result)}")
        print(f"📋 Result: {result}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print(f"📋 Full error: {traceback.format_exc()}")
        return False, str(e)

def test_environment():
    """Check environment variables"""
    print("\n🔍 Checking environment...")
    
    # Load .env file if exists
    env_path = '/Users/evehwang/GitHub/text-moderator-app/.env'
    if os.path.exists(env_path):
        print("📁 Loading .env file...")
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    print(f"✅ Set {key} = {value[:10]}...")
    
    # Check HuggingFace token
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    if hf_token:
        print(f"✅ HUGGINGFACE_TOKEN found: {hf_token[:10]}...")
    else:
        print("❌ HUGGINGFACE_TOKEN not found")

if __name__ == "__main__":
    print("🚀 Text Moderator Debug Test")
    print("=" * 40)
    
    test_environment()
    
    if test_imports():
        success, result = test_api_connection()
        if success:
            print("\n🎉 All tests passed! The API is working.")
        else:
            print(f"\n❌ API test failed: {result}")
    else:
        print("\n❌ Import tests failed")
    
    print("=" * 40)
    print("✅ Debug test complete")
