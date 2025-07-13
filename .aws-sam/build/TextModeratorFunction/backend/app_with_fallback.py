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

# Import our alternative moderator
from alternative_moderator import AlternativeTextModerator

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

# Initialize alternative moderator
hf_token = os.getenv('HUGGINGFACE_TOKEN')
alternative_moderator = AlternativeTextModerator(hf_token)

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
        logger.info("🔄 Will use alternative moderation methods as fallback")
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
    
    # Test alternative moderator
    alt_status = "unknown"
    try:
        alt_success, alt_result = alternative_moderator.analyze_text("test message")
        alt_status = "working" if alt_success else "error"
    except Exception as e:
        alt_status = f"error: {e}"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "primary_api_status": api_status,
        "primary_api_connected": gradio_client is not None,
        "primary_api_error": api_error_message,
        "primary_api_test": api_test_result,
        "alternative_moderator_status": alt_status,
        "fallback_available": True
    })

@app.route('/api/test-connection')
def test_connection():
    """Test both primary and alternative API connections"""
    global gradio_client
    
    results = {
        "primary_api": {"available": False, "working": False, "error": None},
        "alternative_api": {"available": False, "working": False, "error": None},
        "overall_status": "error"
    }
    
    # Test primary API
    if not gradio_client:
        # Try to reconnect
        success = initialize_api_client()
        if not success:
            results["primary_api"]["error"] = api_error_message
        else:
            results["primary_api"]["available"] = True
    else:
        results["primary_api"]["available"] = True
    
    if gradio_client:
        test_success, test_result = test_api_with_sample()
        results["primary_api"]["working"] = test_success
        if not test_success:
            results["primary_api"]["error"] = test_result
    
    # Test alternative API
    try:
        alt_success, alt_result = alternative_moderator.analyze_text("Hello world test")
        results["alternative_api"]["available"] = True
        results["alternative_api"]["working"] = alt_success
        if not alt_success:
            results["alternative_api"]["error"] = alt_result
    except Exception as e:
        results["alternative_api"]["error"] = str(e)
    
    # Determine overall status
    if results["primary_api"]["working"] or results["alternative_api"]["working"]:
        results["overall_status"] = "working"
    elif results["primary_api"]["available"] or results["alternative_api"]["available"]:
        results["overall_status"] = "partial"
    
    return jsonify({
        "success": results["overall_status"] in ["working", "partial"],
        "results": results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text toxicity with primary API and fallback options"""
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
        
        # Log request WITHOUT the actual text content for privacy
        logger.info(f"Analysis request from {client_ip[:10]}*** - text length: {len(text_to_analyze)}")
        
        # Try primary API first (Duc Haba's API)
        primary_success = False
        if gradio_client:
            try:
                logger.info("📡 Trying primary API (Duc Haba)...")
                result = gradio_client.predict(
                    msg=text_to_analyze,
                    safer=safer_value,
                    api_name="/fetch_toxicity_level"
                )
                
                # Parse the results
                chart_data = result[0] if len(result) > 0 else None
                json_output = result[1] if len(result) > 1 else None
                
                # Try to parse JSON output if it's a string
                parsed_json = None
                if json_output:
                    try:
                        parsed_json = json.loads(json_output) if isinstance(json_output, str) else json_output
                    except json.JSONDecodeError:
                        parsed_json = {"raw_output": json_output, "parse_error": "Could not parse JSON"}
                
                logger.info("✅ Primary API successful")
                primary_success = True
                
                return jsonify({
                    "success": True,
                    "method": "primary_api",
                    "timestamp": datetime.now().isoformat(),
                    "results": {
                        "chart_data": chart_data,
                        "analysis": parsed_json
                    },
                    "privacy_note": "Your text was analyzed but not stored or logged."
                })
                
            except Exception as api_error:
                logger.warning(f"Primary API failed: {str(api_error)[:200]}")
                # Continue to fallback
        
        # If primary API failed, try alternative methods
        logger.info("🔄 Using alternative moderation methods...")
        
        try:
            alt_success, alt_result = alternative_moderator.analyze_text(text_to_analyze, safer_value)
            
            if alt_success:
                # Add method info to the analysis
                if 'analysis' in alt_result:
                    alt_result['analysis']['fallback_method'] = True
                
                logger.info(f"✅ Alternative API successful using {alt_result['analysis']['method']}")
                
                return jsonify({
                    "success": True,
                    "method": "alternative_api",
                    "timestamp": datetime.now().isoformat(),
                    "results": alt_result,
                    "privacy_note": "Your text was analyzed but not stored or logged.",
                    "notice": "Using backup analysis method. Results may differ from primary API."
                })
            else:
                logger.error(f"Alternative API also failed: {alt_result}")
                
                return jsonify({
                    "error": "All text analysis methods are currently unavailable.",
                    "suggestion": "Please try again later. Both primary and backup services are having issues.",
                    "details": f"Primary API: {'Failed' if not primary_success else 'N/A'}, Alternative: {alt_result[:100]}"
                }), 503
                
        except Exception as alt_error:
            logger.error(f"Alternative moderator failed: {alt_error}")
            
            return jsonify({
                "error": "Text analysis service is temporarily unavailable.",
                "suggestion": "Please try again in a few minutes.",
                "details": "Both primary and backup analysis methods failed."
            }), 503
        
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
    
    # Test connections on startup
    logger.info("🧪 Testing connections on startup...")
    
    if gradio_client:
        test_success, test_result = test_api_with_sample()
        if test_success:
            logger.info("🎉 Primary API connection test successful!")
        else:
            logger.warning(f"⚠️ Primary API test failed: {test_result}")
    else:
        logger.warning("⚠️ Primary API not available")
    
    # Test alternative moderator
    try:
        alt_success, alt_result = alternative_moderator.analyze_text("Hello world test")
        if alt_success:
            logger.info(f"🎉 Alternative moderator working! Method: {alt_result['analysis']['method']}")
        else:
            logger.warning(f"⚠️ Alternative moderator failed: {alt_result}")
    except Exception as e:
        logger.warning(f"⚠️ Alternative moderator error: {e}")
    
    logger.info("🎯 Server ready to handle requests with fallback capabilities!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
