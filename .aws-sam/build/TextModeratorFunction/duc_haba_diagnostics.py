"""
Duc Haba API Diagnostics - Class Project Compliance
STRICT REQUIREMENT: Only use duchaba/Friendly_Text_Moderation API
"""

import os
import sys
import traceback
import time
from gradio_client import Client

def load_environment():
    """Load environment variables from .env file"""
    env_path = '/Users/evehwang/GitHub/text-moderator-app/.env'
    if os.path.exists(env_path):
        print("📁 Loading .env file...")
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    print(f"✅ Set {key} = {value[:10]}...")
    else:
        print("❌ .env file not found")

def test_gradio_client_connection():
    """Test connection to Duc Haba's API with detailed diagnostics"""
    print("\n🔍 Testing Duc Haba's Friendly_Text_Moderation API")
    print("=" * 60)
    
    try:
        print("📡 Connecting to duchaba/Friendly_Text_Moderation...")
        client = Client("duchaba/Friendly_Text_Moderation")
        print("✅ Client created successfully!")
        
        # Test the /fetch_toxicity_level endpoint as documented
        print("\n🧪 Testing /fetch_toxicity_level endpoint...")
        print("📝 Using test message: 'Hello!!'")
        print("🎛️ Using safer value: 0.02")
        
        result = client.predict(
            msg="Hello!!",
            safer=0.02,
            api_name="/fetch_toxicity_level"
        )
        
        print("✅ API call successful!")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        
        # Analyze the response structure
        if isinstance(result, (list, tuple)) and len(result) >= 2:
            print("\n📋 Response Analysis:")
            print(f"   [0] Chart Data Type: {type(result[0])}")
            print(f"   [1] JSON Output Type: {type(result[1])}")
            
            # Show first element (chart data)
            if result[0]:
                print(f"   [0] Chart Data: {str(result[0])[:200]}...")
            
            # Show second element (JSON output) 
            if result[1]:
                print(f"   [1] JSON Output: {str(result[1])[:200]}...")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"📋 Full error: {traceback.format_exc()}")
        return False, str(e)

def test_toxic_tweets_endpoint():
    """Test the /fetch_toxic_tweets endpoint"""
    print("\n🔍 Testing /fetch_toxic_tweets endpoint...")
    
    try:
        client = Client("duchaba/Friendly_Text_Moderation")
        
        result = client.predict(
            api_name="/fetch_toxic_tweets"
        )
        
        print("✅ /fetch_toxic_tweets successful!")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ /fetch_toxic_tweets failed: {e}")
        return False, str(e)

def test_different_inputs():
    """Test various inputs to understand the API behavior"""
    print("\n🧪 Testing Different Input Messages...")
    
    test_messages = [
        ("Hello world!", "Simple greeting"),
        ("This is a test message.", "Neutral statement"),
        ("I disagree with this opinion.", "Mild disagreement"),
        ("That's really annoying.", "Slight frustration"),
        ("You're an amazing person!", "Positive message")
    ]
    
    try:
        client = Client("duchaba/Friendly_Text_Moderation")
        
        for msg, description in test_messages:
            print(f"\n📝 Testing: '{msg}' ({description})")
            try:
                result = client.predict(
                    msg=msg,
                    safer=0.02,
                    api_name="/fetch_toxicity_level"
                )
                print(f"   ✅ Success! Response length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
                
                # Quick analysis of JSON output
                if len(result) > 1 and result[1]:
                    json_str = str(result[1])
                    if 'max_value' in json_str:
                        print(f"   📊 Contains toxicity analysis data")
                    else:
                        print(f"   📊 Response: {json_str[:100]}...")
                        
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")
            
            time.sleep(1)  # Be respectful to the API
            
    except Exception as e:
        print(f"❌ Could not create client for input testing: {e}")

def check_space_availability():
    """Check if the Gradio space is available"""
    print("\n🌐 Checking Gradio Space Availability...")
    
    import requests
    
    try:
        # Check the space page
        space_url = "https://huggingface.co/spaces/duchaba/Friendly_Text_Moderation"
        response = requests.get(space_url, timeout=10)
        print(f"📡 Space page status: {response.status_code}")
        
        # Check for common indicators
        if response.status_code == 200:
            content = response.text.lower()
            if 'runtime error' in content:
                print("⚠️ Space may have runtime errors")
            elif 'building' in content:
                print("🔧 Space may be building/updating")
            elif 'sleeping' in content:
                print("😴 Space may be sleeping (needs to wake up)")
            else:
                print("✅ Space appears to be accessible")
        
        # Try to access the actual API endpoint
        api_base = "https://duchaba-friendly-text-moderation.hf.space"
        try:
            api_response = requests.get(f"{api_base}/", timeout=10)
            print(f"📡 API endpoint status: {api_response.status_code}")
        except Exception as e:
            print(f"❌ API endpoint check failed: {e}")
            
    except Exception as e:
        print(f"❌ Space availability check failed: {e}")

def main():
    """Main diagnostic function"""
    print("🎓 Duc Haba API Diagnostics - Class Project")
    print("📋 STRICT COMPLIANCE: Only using duchaba/Friendly_Text_Moderation")
    print("=" * 70)
    
    # Load environment
    load_environment()
    
    # Check Python and package versions
    print(f"\n🐍 Python version: {sys.version}")
    
    try:
        import gradio_client
        print(f"✅ gradio_client version: {gradio_client.__version__}")
    except ImportError as e:
        print(f"❌ gradio_client not found: {e}")
        return
    
    # Check space availability first
    check_space_availability()
    
    # Test the main API
    success, result = test_gradio_client_connection()
    
    if success:
        print("\n🎉 PRIMARY API TEST PASSED!")
        
        # Test additional endpoints
        test_toxic_tweets_endpoint()
        
        # Test various inputs
        test_different_inputs()
        
    else:
        print(f"\n❌ PRIMARY API TEST FAILED: {result}")
        print("\n🔧 Possible solutions:")
        print("   1. Wait a few minutes and try again (space may be starting up)")
        print("   2. Check if the space is temporarily down")
        print("   3. Verify your internet connection")
        print("   4. Try running the Flask app anyway - the space might wake up")
    
    print("\n" + "=" * 70)
    print("✅ Diagnostic complete!")
    
    if success:
        print("🎯 Your app should work! Try running: python backend/app.py")
    else:
        print("⚠️ Fix the connection issues above before running your app")

if __name__ == "__main__":
    main()
