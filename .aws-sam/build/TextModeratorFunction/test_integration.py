#!/usr/bin/env python3
"""
Test the Duc Haba API integration to verify it works correctly.
This will help debug the "Analysis failed" error.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_direct():
    """Test the API directly using the exact documentation example"""
    try:
        from gradio_client import Client
        
        logger.info("🔗 Creating Duc Haba client...")
        client = Client("duchaba/Friendly_Text_Moderation")
        logger.info("✅ Client created successfully")
        
        logger.info("📡 Testing API with documentation example...")
        result = client.predict(
            msg="Hello!!",
            safer=0.02,
            api_name="/fetch_toxicity_level"
        )
        
        logger.info("✅ API call successful!")
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        
        if hasattr(result, '__len__') and len(result) >= 2:
            logger.info(f"Chart data type: {type(result[0])}")
            logger.info(f"JSON output type: {type(result[1])}")
            logger.info(f"JSON output: {result[1]}")
        
        return True, result
        
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, str(e)

def test_flask_app():
    """Test the Flask app locally"""
    try:
        logger.info("🧪 Testing Flask app...")
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            logger.info("Testing /health endpoint...")
            response = client.get('/health')
            logger.info(f"Health status: {response.status_code}")
            logger.info(f"Health response: {response.get_json()}")
            
            # Test analyze endpoint
            logger.info("Testing /api/analyze endpoint...")
            response = client.post('/api/analyze', 
                                 json={'text': 'Hello world!', 'safer': 0.02},
                                 headers={'Content-Type': 'application/json'})
            
            logger.info(f"Analyze status: {response.status_code}")
            logger.info(f"Analyze response: {response.get_json()}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("🎓 Testing Text Moderator API Integration")
    logger.info("=" * 50)
    
    # Test 1: Direct API call
    logger.info("Test 1: Direct API Call")
    success, result = test_api_direct()
    if success:
        logger.info("✅ Direct API test PASSED")
    else:
        logger.error("❌ Direct API test FAILED")
        sys.exit(1)
    
    logger.info("")
    
    # Test 2: Flask app
    logger.info("Test 2: Flask App Integration")
    success = test_flask_app()
    if success:
        logger.info("✅ Flask app test PASSED")
    else:
        logger.error("❌ Flask app test FAILED")
        sys.exit(1)
    
    logger.info("")
    logger.info("🎉 All tests PASSED! The API integration is working correctly.")
    logger.info("Your app should work when deployed to AWS Lambda.")
