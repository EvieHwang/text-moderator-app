import json
import os
import sys
from io import StringIO

def lambda_handler(event, context):
    """AWS Lambda handler function - Class Project Compliant (Duc Haba Only)"""
    try:
        # Set up environment for Lambda
        import os
        if 'LAMBDA_TASK_ROOT' in os.environ:
            # We're running in Lambda
            print(f"Lambda environment detected. HF Token present: {'HUGGINGFACE_TOKEN' in os.environ}")
        
        # Import the clean Flask app
        from app import app
        
        # Handle API Gateway events
        if 'httpMethod' in event:
            # Simple WSGI adapter for Lambda
            method = event['httpMethod']
            path = event.get('path', '/')
            headers = event.get('headers', {})
            query_params = event.get('queryStringParameters') or {}
            body = event.get('body', '')
            
            # Create a test client for the Flask app
            with app.test_client() as client:
                # Handle query parameters
                query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()]) if query_params else ''
                
                # Make the request to Flask
                if method == 'GET':
                    response = client.get(path, query_string=query_string, headers=headers)
                elif method == 'POST':
                    content_type = headers.get('content-type', 'application/json')
                    if 'application/json' in content_type:
                        response = client.post(path, json=json.loads(body) if body else {}, headers=headers)
                    else:
                        response = client.post(path, data=body, headers=headers)
                else:
                    response = client.open(path, method=method, data=body, headers=headers)
                
                # Convert Flask response to Lambda response
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': response.content_type,
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                    },
                    'body': response.get_data(as_text=True)
                }
        
        # If not an HTTP event, return error
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid event type'})
        }
        
    except ImportError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Import error: {str(e)}', 'compliance_note': 'CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}', 'compliance_note': 'CLASS PROJECT: Only using duchaba/Friendly_Text_Moderation API'})
        }
