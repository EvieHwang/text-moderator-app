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

# STRICT COMPLIANCE: Only use Duc Haba's API
# Initialize Gradio client for Duc Haba's API ONLY
gradio_client = None
api_error_message = None
connection_attempts = 0
last_connection_attempt = 0

def initialize_duc_haba_client():
    """Initialize ONLY Duc Haba's API client - Class Project Compliance"""
    global gradio_client, api_error_message, connection_attempts, last_connection_attempt
    
    # Avoid rapid reconnection attempts
    now = time.time()
    if now - last_connection_attempt < 30:  # Wait 30 seconds between attempts
        return False
    
    last_connection_attempt = now
    connection_attempts += 1
    
    try:
        logger.info(f"🔗 Connecting to duchaba/Friendly_Text_Moderation (attempt {connection_attempts})...")
        gradio_client = Client("duchaba/Friendly_Text_Moderation")
        logger.info("✅ Successfully connected to Duc Haba's API")
        api_error_message = None
        connection_attempts = 0  # Reset on success
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Failed to connect to Duc Haba's API: {error_msg}")
        api_error_message = error_msg
        gradio_client = None
        return False

def test_duc_haba_api():
    """Test Duc Haba's API with multiple parameter approaches"""
    global gradio_client
    
    if not gradio_client:
        return False, "Client not initialized"
    
    try:
        logger.info("🧪 Testing Duc Haba's API with multiple approaches...")
        
        # Try approach 1: Positional arguments (most reliable)
        try:
            result = gradio_client.predict(
                "Hello!!",  # First parameter (text)
                0.02,       # Second parameter (safer value)
                api_name="/fetch_toxicity_level"
            )
            logger.info("✅ Duc Haba API test successful (positional args)")
            return True, result
        except Exception as e1:
            logger.warning(f"Positional args failed: {e1}")
        
        # Try approach 2: Named parameters as documented
        try:
            result = gradio_client.predict(
                msg="Hello!!",
                safer=0.02,
                api_name="/fetch_toxicity_level"
            )
            logger.info("✅ Duc Haba API test successful (named args)")
            return True, result
        except Exception as e2:
            logger.warning(f"Named args failed: {e2}")
        
        # Try approach 3: Alternative parameter names
        try:
            result = gradio_client.predict(
                text="Hello!!",
                safer=0.02,
                api_name="/fetch_toxicity_level"
            )
            logger.info("✅ Duc Haba API test successful (alternative names)")
            return True, result
        except Exception as e3:
            logger.warning(f"Alternative names failed: {e3}")
        
        return False, f"All approaches failed: {e1}, {e2}, {e3}"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Duc Haba API test failed: {error_msg}")
        return False, error_msg

def call_duc_haba_api(text, safer_value=0.02):
    """Call Duc Haba's API with multiple fallback approaches"""
    global gradio_client
    
    if not gradio_client:
        return False, "Client not initialized"
    
    # Try approach 1: Positional arguments (most reliable)
    try:
        result = gradio_client.predict(
            text,        # First parameter
            safer_value, # Second parameter
            api_name="/fetch_toxicity_level"
        )
        logger.info("✅ API call successful (positional)")
        return True, result
    except Exception as e1:
        logger.warning(f"Positional call failed: {e1}")
    
    # Try approach 2: Named parameters
    try:
        result = gradio_client.predict(
            msg=text,
            safer=safer_value,
            api_name="/fetch_toxicity_level"
        )
        logger.info("✅ API call successful (named)")
        return True, result
    except Exception as e2:
        logger.warning(f"Named call failed: {e2}")
    
    # Try approach 3: Alternative names
    try:
        result = gradio_client.predict(
            text=text,
            safer=safer_value,
            api_name="/fetch_toxicity_level"
        )
        logger.info("✅ API call successful (alternative)")
        return True, result
    except Exception as e3:
        logger.warning(f"Alternative call failed: {e3}")
    
    return False, f"All approaches failed: {e1}, {e2}, {e3}"

# Try to initialize the API on startup
initialize_duc_haba_client()

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
    """Health check endpoint - Duc Haba API only"""
    global api_error_message, connection_attempts
    
    duc_haba_status = "disconnected"
    duc_haba_test_result = None
    
    if gradio_client:
        duc_haba_status = "connected"
        test_success, test_result = test_duc_haba_api()
        if test_success:
            duc_haba_status = "working"
            duc_haba_test_result = "API test successful"
        else:
            duc_haba_status = "error"
            duc_haba_test_result = test_result
    
    return jsonify({
        "status": "healthy" if duc_haba_status == "working" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "duc_haba_api_status": duc_haba_status,
        "duc_haba_connected": gradio_client is not None,
        "duc_haba_error": api_error_message,
        "duc_haba_test": duc_haba_test_result,
        "connection_attempts": connection_attempts,
        "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
    })

@app.route('/api/test-connection')
def test_connection():
    """Test ONLY Duc Haba's API connection - Class Project Compliance"""
    global gradio_client
    
    if not gradio_client:
        # Try to reconnect to Duc Haba's API
        logger.info("🔄 Attempting to reconnect to Duc Haba's API...")
        success = initialize_duc_haba_client()
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to connect to Duc Haba's API: {api_error_message}",
                "suggestion": "The Gradio space may be sleeping or temporarily down. Try again in a few minutes.",
                "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
            }), 503
    
    # Test with multiple approaches
    test_success, test_result = test_duc_haba_api()
    
    return jsonify({
        "success": test_success,
        "result": "API working correctly" if test_success else None,
        "error": test_result if not test_success else None,
        "timestamp": datetime.now().isoformat(),
        "api_used": "duchaba/Friendly_Text_Moderation",
        "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text using ONLY Duc Haba's API - Class Project Compliance"""
    global gradio_client  # Add this line to access the global variable
    
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
        
        if len(text_to_analyze) > 5000:
            return jsonify({
                "error": "Text too long. Maximum 5000 characters allowed."
            }), 400
        
        # Get safer value from request or use default
        safer_value = data.get('safer', 0.02)
        
        # Ensure we have a connection to Duc Haba's API
        if not gradio_client:
            logger.info("🔄 No connection to Duc Haba's API, attempting to connect...")
            success = initialize_duc_haba_client()
            if not success:
                return jsonify({
                    "error": "Duc Haba's text moderation API is currently unavailable.",
                    "details": api_error_message,
                    "suggestion": "The Gradio space may be starting up or temporarily down. Please try again in a few minutes.",
                    "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
                }), 503
        
        # Log request WITHOUT the actual text content for privacy
        logger.info(f"Analysis request from {client_ip[:10]}*** - text length: {len(text_to_analyze)}")
        
        # Call Duc Haba's API using multiple approaches
        try:
            logger.info("📡 Calling Duc Haba's API with fallback approaches...")
            success, result = call_duc_haba_api(text_to_analyze, safer_value)
            
            if not success:
                # Reset client on failure to force reconnection
                gradio_client = None
                return jsonify({
                    "error": "Duc Haba's API call failed.",
                    "details": result,
                    "suggestion": "Please try again. The API may be temporarily busy.",
                    "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
                }), 503
            
            logger.info("✅ Duc Haba API call completed successfully")
            
        except Exception as api_error:
            error_str = str(api_error)
            logger.error(f"Duc Haba API call failed: {error_str}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Reset client on failure to force reconnection
            gradio_client = None
            
            return jsonify({
                "error": "Duc Haba's text moderation API encountered an error.",
                "details": error_str[:200],
                "suggestion": "Please try again later. If the problem persists, the API may be temporarily down.",
                "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
            }), 503
        
        # Parse the results according to documentation
        try:
            # Expected: tuple of 2 elements
            # [0] Dict(type: Literal['altair', 'bokeh', 'plotly', 'matplotlib'], plot: str)
            # [1] str (JSON output)
            
            chart_data = result[0] if len(result) > 0 else None
            json_output = result[1] if len(result) > 1 else None
            
            # Try to parse JSON output if it's a string
            parsed_json = None
            if json_output:
                try:
                    parsed_json = json.loads(json_output) if isinstance(json_output, str) else json_output
                except json.JSONDecodeError:
                    # If JSON parsing fails, include the raw output
                    parsed_json = {
                        "raw_output": json_output,
                        "parse_error": "Could not parse JSON output from Duc Haba's API"
                    }
            
            # Log successful analysis WITHOUT content details
            logger.info(f"✅ Duc Haba analysis completed for {client_ip[:10]}*** - length: {len(text_to_analyze)}")
            
            # Return results in compliance with class requirements
            return jsonify({
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "api_used": "duchaba/Friendly_Text_Moderation",
                "endpoint_used": "/fetch_toxicity_level",
                "results": {
                    "chart_data": chart_data,
                    "analysis": parsed_json
                },
                "privacy_note": "Your text was analyzed but not stored or logged.",
                "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
            })
            
        except Exception as parse_error:
            logger.error(f"Error parsing Duc Haba API response: {parse_error}")
            return jsonify({
                "error": "Failed to process results from Duc Haba's API.",
                "details": str(parse_error),
                "suggestion": "The API returned an unexpected response format.",
                "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in analysis endpoint: {traceback.format_exc()}")
        return jsonify({
            "error": "An unexpected error occurred.",
            "suggestion": "Please try again or contact support if the issue persists.",
            "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🎓 CLASS PROJECT: Text Moderator using ONLY Duc Haba's API")
    logger.info(f"🚀 Starting Flask server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    # Test Duc Haba API connection on startup
    if gradio_client:
        test_success, test_result = test_duc_haba_api()
        if test_success:
            logger.info("🎉 Duc Haba API connection test successful - ready to serve requests!")
        else:
            logger.warning(f"⚠️ Duc Haba API connection test failed: {test_result}")
            logger.warning("💡 The Gradio space may need to wake up. Try making a request anyway.")
    else:
        logger.warning("⚠️ Starting server without Duc Haba API connection")
        logger.warning("💡 The API will attempt to connect when the first request is made")
    
    logger.info("📋 STRICT COMPLIANCE: Only using duchaba/Friendly_Text_Moderation API")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
