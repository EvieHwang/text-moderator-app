from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from gradio_client import Client
import os
import logging
from datetime import datetime
import json
import time
from collections import defaultdict

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
try:
    gradio_client = Client("duchaba/Friendly_Text_Moderation")
    logger.info("✅ Successfully connected to Duc Haba's API")
except Exception as e:
    logger.error(f"❌ Failed to connect to Duc Haba's API: {e}")
    gradio_client = None

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
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_connected": gradio_client is not None
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text toxicity using Duc Haba's API with rate limiting and privacy protection"""
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
            return jsonify({
                "error": "Text moderation API is currently unavailable. Please try again later."
            }), 503
        
        # Log request WITHOUT the actual text content for privacy
        logger.info(f"Analysis request from {client_ip[:10]}*** - text length: {len(text_to_analyze)}")
        
        # Call Duc Haba's API
        try:
            result = gradio_client.predict(
                msg=text_to_analyze,
                safer=safer_value,
                api_name="/fetch_toxicity_level"
            )
        except Exception as api_error:
            logger.error(f"API call failed: {str(api_error)[:100]}")
            
            # Handle specific API errors
            if "rate limit" in str(api_error).lower():
                return jsonify({
                    "error": "API rate limit reached. Please try again in a few minutes."
                }), 429
            elif "timeout" in str(api_error).lower():
                return jsonify({
                    "error": "Analysis timed out. Please try with shorter text."
                }), 408
            else:
                return jsonify({
                    "error": "Analysis service temporarily unavailable. Please try again later."
                }), 503
        
        # Parse the results
        chart_data = result[0] if len(result) > 0 else None
        json_output = result[1] if len(result) > 1 else None
        
        # Try to parse JSON output if it's a string
        parsed_json = None
        if json_output:
            try:
                parsed_json = json.loads(json_output) if isinstance(json_output, str) else json_output
            except:
                parsed_json = {"raw_output": json_output}
        
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
        
    except Exception as e:
        logger.error(f"❌ Error in analysis endpoint: {str(e)[:100]}")
        return jsonify({
            "error": "An unexpected error occurred. Please try again."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Changed from 5000 to 8000
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
