"""
Simple test using the EXACT documentation example
"""

from gradio_client import Client

def test_exact_documentation_example():
    """Test using the exact example from the documentation"""
    
    print("🔍 Testing EXACT documentation example...")
    print("Code from docs:")
    print('''
from gradio_client import Client

client = Client("duchaba/Friendly_Text_Moderation")
result = client.predict(
    msg="Hello!!",
    safer=0.02,
    api_name="/fetch_toxicity_level"
)
print(result)
    ''')
    
    try:
        client = Client("duchaba/Friendly_Text_Moderation")
        print("✅ Connected to duchaba/Friendly_Text_Moderation")
        
        result = client.predict(
            msg="Hello!!",
            safer=0.02,
            api_name="/fetch_toxicity_level"
        )
        
        print("✅ SUCCESS! Documentation example works perfectly")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        print(f"📊 Result: {result}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"📋 Full error: {str(e)}")
        
        # Check gradio_client version
        try:
            import gradio_client
            print(f"📦 gradio_client version: {gradio_client.__version__}")
        except:
            print("📦 Could not get gradio_client version")
        
        return False, str(e)

if __name__ == "__main__":
    print("🎓 Testing Duc Haba API with EXACT Documentation Example")
    print("=" * 60)
    
    success, result = test_exact_documentation_example()
    
    if success:
        print("\n🎉 The documentation example works perfectly!")
        print("The issue must be in our Flask app, not the API call itself.")
    else:
        print(f"\n❌ Even the documentation example fails: {result}")
        print("This suggests a gradio_client version or environment issue.")
