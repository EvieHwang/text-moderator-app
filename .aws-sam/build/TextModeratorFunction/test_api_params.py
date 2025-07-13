"""
Quick API parameter test for Duc Haba's API
This will help us figure out the correct parameter names
"""

from gradio_client import Client

def test_api_parameters():
    """Test different parameter combinations to find the right one"""
    
    try:
        client = Client("duchaba/Friendly_Text_Moderation")
        print("✅ Connected to Duc Haba's API")
        
        # Let's inspect the API to see what parameters it expects
        try:
            # Get API info
            api_info = client.view_api()
            print("📋 API Information:")
            print(api_info)
            
        except Exception as e:
            print(f"Could not get API info: {e}")
        
        # Try different parameter names based on common patterns
        test_text = "Hello world"
        
        parameter_combinations = [
            # From documentation
            {"msg": test_text, "safer": 0.02},
            
            # Common alternatives
            {"text": test_text, "safer": 0.02},
            {"message": test_text, "safer": 0.02},
            {"input": test_text, "safer": 0.02},
            {"content": test_text, "safer": 0.02},
            
            # Try positional arguments
            {0: test_text, 1: 0.02},
            
            # Try without parameter names (positional)
            None  # We'll handle this separately
        ]
        
        for i, params in enumerate(parameter_combinations):
            print(f"\n🧪 Test {i+1}: {params}")
            
            try:
                if params is None:
                    # Try positional arguments
                    result = client.predict(
                        test_text,
                        0.02,
                        api_name="/fetch_toxicity_level"
                    )
                else:
                    result = client.predict(
                        **params,
                        api_name="/fetch_toxicity_level"
                    )
                
                print(f"   ✅ SUCCESS! Parameters: {params}")
                print(f"   📊 Result type: {type(result)}")
                print(f"   📊 Result: {str(result)[:200]}...")
                return params  # Return the working parameters
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")
        
        print("\n❌ No parameter combination worked")
        return None
        
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing Duc Haba API Parameters")
    print("=" * 50)
    
    working_params = test_api_parameters()
    
    if working_params:
        print(f"\n🎉 Found working parameters: {working_params}")
    else:
        print("\n❌ Could not find working parameters")
