#!/bin/bash

# Clean deployment script for Text Moderator App
# This script will deploy the cleaned-up version to AWS

echo "🧹 Clean Text Moderator Deployment"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "template.yaml" ]; then
    echo "❌ Error: template.yaml not found. Please run this script from the project root."
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ Error: AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if we have the HuggingFace token parameter
echo "🔍 Checking deployment configuration..."

if [ ! -f "samconfig.toml" ]; then
    echo "❌ Error: samconfig.toml not found. Please ensure your SAM configuration is set up."
    exit 1
fi

# Test the API integration locally first (optional)
echo "🧪 Testing API integration (optional - press Enter to skip)..."
read -p "Run local tests? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running integration tests..."
    python3 test_integration.py
    if [ $? -ne 0 ]; then
        echo "❌ Local tests failed. Please fix issues before deploying."
        exit 1
    fi
    echo "✅ Local tests passed!"
fi

# Clean up any previous builds
echo "🧹 Cleaning previous builds..."
rm -rf .aws-sam/build/

# Build the application
echo "🔨 Building SAM application..."
sam build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

echo "✅ Build successful!"

# Deploy the application
echo "🚀 Deploying to AWS..."
sam deploy

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Check the AWS CloudFormation stack for the API Gateway URL"
echo "2. Test the live application using the provided URL"
echo "3. Monitor the CloudWatch logs for any issues"
echo ""
echo "🔧 If you encounter 'Analysis failed' errors:"
echo "1. Check CloudWatch logs for the Lambda function"
echo "2. Verify the HuggingFace token is set correctly"
echo "3. Ensure the Gradio space 'duchaba/Friendly_Text_Moderation' is accessible"
echo ""
echo "✅ Clean deployment complete!"
