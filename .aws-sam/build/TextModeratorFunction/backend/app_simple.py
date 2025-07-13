from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
from datetime import datetime
import json
import time
from collections import defaultdict
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate limiting storage
rate_limit_storage = defaultdict(list)
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW = 3600

# Global client variable
gradio_client = None

def get_gradio_client():
    """Get or create Gradio client using the EXACT documentation approach"""
    global gradio_client
    
    if gradio_client is None:
        try:
            # Import here to avoid issues in Lambda cold start
            from gradio_client import Client
            
            logger.info("🔗 Creating Duc Haba client...")
            gradio_client = Client("duchaba/Friendly_Text_Moderation")
            logger.info("✅ Duc Haba client created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create Duc Haba client: {e}")
            gradio_client = None
            raise e
    
    return gradio_client

def call_duc_haba_api(text, safer_value=0.02):
    """Call Duc Haba's API using the EXACT documentation method"""
    try:
        client = get_gradio_client()
        
        # Use the EXACT method from documentation
        result = client.predict(
            msg=text,
            safer=safer_value,
            api_name="/fetch_toxicity_level"
        )
        
        logger.info("✅ API call successful")
        return True, result
        
    except Exception as e:
        logger.error(f"❌ API call failed: {e}")
        # Reset client on failure
        global gradio_client
        gradio_client = None
        return False, str(e)

def check_rate_limit(client_ip):
    """Check if client has exceeded rate limit"""
    now = time.time()
    
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip] 
        if now - timestamp < RATE_LIMIT_WINDOW
    ]
    
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    rate_limit_storage[client_ip].append(now)
    return True

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test API connection
        success, result = call_duc_haba_api("Hello!!")
        
        return jsonify({
            "status": "healthy" if success else "degraded",
            "timestamp": datetime.now().isoformat(),
            "duc_haba_api_status": "working" if success else "error",
            "duc_haba_test": "API test successful" if success else result,
            "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/test-connection')
def test_connection():
    """Test API connection"""
    try:
        success, result = call_duc_haba_api("Hello!!")
        
        return jsonify({
            "success": success,
            "result": "API working correctly" if success else None,
            "error": result if not success else None,
            "timestamp": datetime.now().isoformat(),
            "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text using ONLY Duc Haba's API"""
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
        
        # Log request WITHOUT the actual text content for privacy
        logger.info(f"Analysis request from {client_ip[:10]}*** - text length: {len(text_to_analyze)}")
        
        # Call Duc Haba's API
        logger.info("📡 Calling Duc Haba's API...")
        success, result = call_duc_haba_api(text_to_analyze, safer_value)
        
        if not success:
            return jsonify({
                "error": "Duc Haba's API call failed.",
                "details": result,
                "suggestion": "Please try again. The API may be temporarily busy.",
                "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
            }), 503
        
        # Parse the results
        try:
            chart_data = result[0] if len(result) > 0 else None
            json_output = result[1] if len(result) > 1 else None
            
            # Try to parse JSON output if it's a string
            parsed_json = None
            if json_output:
                try:
                    parsed_json = json.loads(json_output) if isinstance(json_output, str) else json_output
                except json.JSONDecodeError:
                    parsed_json = {
                        "raw_output": json_output,
                        "parse_error": "Could not parse JSON output from Duc Haba's API"
                    }
            
            # Log successful analysis
            logger.info(f"✅ Duc Haba analysis completed for {client_ip[:10]}*** - length: {len(text_to_analyze)}")
            
            # Return results
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
            logger.error(f"Error parsing API response: {parse_error}")
            return jsonify({
                "error": "Failed to process results from Duc Haba's API.",
                "details": str(parse_error),
                "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {traceback.format_exc()}")
        return jsonify({
            "error": "An unexpected error occurred.",
            "suggestion": "Please try again.",
            "compliance_note": "CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🎓 CLASS PROJECT: Text Moderator using ONLY Duc Haba's API")
    logger.info(f"🚀 Starting Flask server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
