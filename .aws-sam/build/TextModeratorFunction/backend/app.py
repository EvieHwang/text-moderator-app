from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from gradio_client import Client
import os
import logging
from datetime import datetime
import json
import time
from collections import defaultdict
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configure logging to NOT log user inputs for privacy
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis or database)
rate_limit_storage = defaultdict(list)
RATE_LIMIT_REQUESTS = 20  # requests per time window
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Initialize Gradio client for Duc Haba's API
gradio_client = None
api_error_message = None

def initialize_api_client():
    """Initialize the Gradio client with better error handling"""
    global gradio_client, api_error_message
    
    try:
        logger.info("🔗 Attempting to connect to duchaba/Friendly_Text_Moderation...")
        gradio_client = Client("duchaba/Friendly_Text_Moderation")
        logger.info("✅ Successfully connected to Duc Haba's API")
        api_error_message = None
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Failed to connect to Duc Haba's API: {error_msg}")
        api_error_message = error_msg
        gradio_client = None
        return False

def test_api_with_sample():
    """Test the API with a sample message"""
    global gradio_client
    
    if not gradio_client:
        return False, "Client not initialized"
    
    try:
        logger.info("🧪 Testing API with sample message...")
        result = gradio_client.predict(
            msg="Hello world, this is a test.",
            safer=0.02,
            api_name="/fetch_toxicity_level"
        )
        logger.info("✅ API test successful")
        return True, result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ API test failed: {error_msg}")
        return False, error_msg

# Try to initialize the API on startup
initialize_api_client()

def check_rate_limit(client_ip):
    """Check if client has exceeded rate limit"""
    now = time.time()
    
    # Clean old entries
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip] 
        if now - timestamp < RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(now)
    return True

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint with detailed status"""
    global api_error_message
    
    # Test API if client exists
    api_status = "disconnected"
    api_test_result = None
    
    if gradio_client:
        api_status = "connected"
        test_success, test_result = test_api_with_sample()
        if test_success:
            api_status = "working"
            api_test_result = "API test successful"
        else:
            api_status = "error"
            api_test_result = test_result
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_status": api_status,
        "api_connected": gradio_client is not None,
        "api_error": api_error_message,
        "api_test": api_test_result
    })

@app.route('/api/test-connection')
def test_connection():
    """Test the API connection endpoint"""
    global gradio_client
    
    if not gradio_client:
        # Try to reconnect
        success = initialize_api_client()
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to connect to API: {api_error_message}"
            }), 503
    
    # Test with sample
    test_success, test_result = test_api_with_sample()
    
    return jsonify({
        "success": test_success,
        "result": test_result if test_success else None,
        "error": test_result if not test_success else None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text toxicity using Duc Haba's API with enhanced error handling"""
    try:
        # Get client IP for rate limiting
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Check rate limit
        if not check_rate_limit(client_ip):
            return jsonify({
                "error": "Rate limit exceeded. Please wait before making more requests.",
                "retry_after": RATE_LIMIT_WINDOW
            }), 429
        
        # Get request data
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request body"
            }), 400
        
        text_to_analyze = data['text'].strip()
        
        if not text_to_analyze:
            return jsonify({
                "error": "Text cannot be empty"
            }), 400
        
        if len(text_to_analyze) > 5000:  # Rate limiting
            return jsonify({
                "error": "Text too long. Maximum 5000 characters allowed."
            }), 400
        
        # Get safer value from request or use default
        safer_value = data.get('safer', 0.02)
        
        # Check if API client is available
        if not gradio_client:
            # Try to reconnect
            logger.info("🔄 Attempting to reconnect to API...")
            success = initialize_api_client()
            if not success:
                return jsonify({
                    "error": f"Text moderation API is currently unavailable: {api_error_message}",
                    "suggestion": "Please try again in a few minutes or check the service status."
                }), 503
        
        # Log request WITHOUT the actual text content for privacy
        logger.info(f"Analysis request from {client_ip[:10]}*** - text length: {len(text_to_analyze)}")
        
        # Call Duc Haba's API with enhanced error handling
        try:
            logger.info("📡 Making API call...")
            result = gradio_client.predict(
                msg=text_to_analyze,
                safer=safer_value,
                api_name="/fetch_toxicity_level"
            )
            logger.info("✅ API call completed successfully")
            
        except Exception as api_error:
            error_str = str(api_error)
            logger.error(f"API call failed: {error_str}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Handle specific API errors with better messages
            if "rate limit" in error_str.lower():
                return jsonify({
                    "error": "API rate limit reached. Please try again in a few minutes.",
                    "suggestion": "The service is temporarily overwhelmed. Please wait and retry."
                }), 429
            elif "timeout" in error_str.lower():
                return jsonify({
                    "error": "Analysis timed out. Please try with shorter text.",
                    "suggestion": "Try reducing the text length or splitting into smaller chunks."
                }), 408
            elif "connection" in error_str.lower():
                return jsonify({
                    "error": "Connection to analysis service failed.",
                    "suggestion": "The service may be temporarily down. Please try again later."
                }), 503
            elif "not found" in error_str.lower() or "404" in error_str:
                return jsonify({
                    "error": "Analysis service endpoint not found.",
                    "suggestion": "The API may have been updated. Please report this issue."
                }), 503
            else:
                return jsonify({
                    "error": "Analysis service temporarily unavailable.",
                    "details": error_str[:200],  # Limit error details
                    "suggestion": "Please try again later or contact support if the issue persists."
                }), 503
        
        # Parse the results with better error handling
        try:
            chart_data = result[0] if len(result) > 0 else None
            json_output = result[1] if len(result) > 1 else None
            
            # Try to parse JSON output if it's a string
            parsed_json = None
            if json_output:
                try:
                    parsed_json = json.loads(json_output) if isinstance(json_output, str) else json_output
                except json.JSONDecodeError:
                    parsed_json = {"raw_output": json_output, "parse_error": "Could not parse JSON"}
            
            # Log successful analysis WITHOUT content details
            logger.info(f"✅ Analysis completed for {client_ip[:10]}*** - length: {len(text_to_analyze)}")
            
            # Return results WITHOUT storing or logging the original text
            return jsonify({
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "results": {
                    "chart_data": chart_data,
                    "analysis": parsed_json
                },
                "privacy_note": "Your text was analyzed but not stored or logged."
            })
            
        except Exception as parse_error:
            logger.error(f"Error parsing API response: {parse_error}")
            return jsonify({
                "error": "Failed to process analysis results.",
                "suggestion": "The service returned an unexpected response format."
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in analysis endpoint: {traceback.format_exc()}")
        return jsonify({
            "error": "An unexpected error occurred.",
            "suggestion": "Please try again or contact support if the issue persists."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    # Test API connection on startup
    if gradio_client:
        test_success, test_result = test_api_with_sample()
        if test_success:
            logger.info("🎉 API connection test successful - ready to serve requests!")
        else:
            logger.warning(f"⚠️ API connection test failed: {test_result}")
    else:
        logger.warning("⚠️ Starting server without API connection")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
