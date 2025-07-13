# Text Moderator App - Clean Version

## Project Structure
```
text-moderator-app/
├── app.py                  # Main Flask application (CLEAN VERSION)
├── lambda_function.py      # AWS Lambda handler
├── template.yaml          # SAM template
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Frontend interface
├── test_integration.py    # API integration tests
└── deploy_clean.sh       # Clean deployment script
```

## What Was Fixed

### 1. **API Integration Issue**
- **Problem**: The `call_duc_haba_api` function had incorrect parameter handling
- **Solution**: Fixed to use exact API documentation format:
```python
result = client.predict(
    msg=text,
    safer=safer_value,
    api_name="/fetch_toxicity_level"
)
```

### 2. **Code Cleanup**
- Removed multiple conflicting backend files (`app_simple.py`, `app_duc_haba_fixed.py`, etc.)
- Created single clean `app.py` with proper error handling
- Updated lambda handler to use the clean app

### 3. **Proper Error Handling**
- Added comprehensive error handling and logging
- Improved user-friendly error messages
- Added API connection retry logic

## Deployment Instructions

### 1. Test Locally (Optional)
```bash
python3 test_integration.py
```

### 2. Deploy to AWS
```bash
chmod +x deploy_clean.sh
./deploy_clean.sh
```

### 3. Manual Deployment (Alternative)
```bash
sam build
sam deploy
```

## Key Changes Made

### API Call Fix
**Before (broken):**
```python
def call_duc_haba_api(text, safer_value=0.02):
    # Had issues with function name and parameter handling
    result = gradio_client.predict(...)  # Wrong format
```

**After (working):**
```python
def call_duc_haba_api(text, safer_value=0.02):
    try:
        client = get_gradio_client()
        result = client.predict(
            msg=text,
            safer=safer_value,
            api_name="/fetch_toxicity_level"
        )
        return True, result
    except Exception as e:
        # Reset client on failure
        global gradio_client
        gradio_client = None
        return False, str(e)
```

### Lambda Handler Fix
**Before:**
```python
from backend.app_simple import app  # Referenced non-existent path
```

**After:**
```python
from app import app  # Clean reference to main app
```

## Troubleshooting

### If "Analysis failed" still occurs:

1. **Check CloudWatch Logs:**
   - Go to AWS CloudWatch
   - Find your Lambda function logs
   - Look for specific error messages

2. **Common Issues:**
   - **Cold Start**: Lambda may timeout on first request - try again
   - **API Timeout**: Duc Haba's Gradio space may be sleeping - wait 30 seconds and retry
   - **Network Issues**: Check if AWS Lambda can access external APIs

3. **Test API Directly:**
   ```bash
   python3 test_integration.py
   ```

4. **Verify Environment Variables:**
   - Ensure `HUGGINGFACE_TOKEN` is set in AWS Lambda (though not required for this specific API)

### Expected API Response Format

The API returns a tuple with 2 elements:
```python
result = [
    {  # Chart data
        "type": "plotly",  # or "altair", "bokeh", "matplotlib"
        "plot": "base64_encoded_image_or_json"
    },
    {  # JSON analysis results
        "max_value": 0.1,
        "max_key": "harassment",
        "is_flagged": false,
        "safer_value": 0.02,
        # ... other analysis data
    }
]
```

## Files Removed (Cleanup)

The following files were causing confusion and have been cleaned up:
- `backend/app_simple.py` (replaced by `app.py`)
- `backend/app_duc_haba_fixed.py`
- `backend/app_duc_haba_only.py`
- `backend/app_with_fallback.py`
- `aws/lambda_function.py` (moved to root)
- `alternative_moderator.py` (not needed for class project)

## Final Notes

- ✅ **Compliance**: Uses ONLY `duchaba/Friendly_Text_Moderation` API as required
- ✅ **Clean Code**: Single source of truth with proper error handling
- ✅ **Fixed Integration**: Correct API parameter format
- ✅ **Better UX**: Improved error messages and user feedback

The app should now work correctly without "Analysis failed" errors. The main issue was the incorrect API parameter format in the original code.
