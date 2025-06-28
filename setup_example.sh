#!/bin/bash

# Touch Project - AWS Setup Example
# This script demonstrates how to set up AWS IAM user and configuration

echo "🚀 Touch Project - AWS Setup Example"
echo "====================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️  AWS CLI not configured. Please run 'aws configure' first."
    echo "   You'll need your AWS Access Key ID and Secret Access Key."
    exit 1
fi

echo "✅ AWS CLI is configured"
echo ""

# Generate a unique bucket name
BUCKET_NAME="touch-audio-$(date +%s)"
echo "📦 Will create S3 bucket: $BUCKET_NAME"
echo ""

# Run the automated setup
echo "🔧 Running automated AWS setup..."
python3 setup_aws_iam.py \
    --username touch-app-user \
    --bucket-name "$BUCKET_NAME" \
    --region us-east-1 \
    --output-env

echo ""
echo "📝 Next steps:"
echo "1. Copy the .env content above to a file named '.env' in the project root"
echo "2. Test the setup: python3 cli.py --test-aws"
echo "3. Start converting videos: python3 cli.py video.mp4"
echo ""
echo "�� Setup complete!" 