#!/usr/bin/env python3
"""
AWS IAM Setup Script for Touch Project

This script automatically creates an IAM user with the necessary permissions
for the Touch video/audio to Braille converter project.

Usage:
    python setup_aws_iam.py --username touch-app-user --bucket-name my-touch-bucket
"""

import boto3
import argparse
import json
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def create_iam_user(iam_client, username):
    """Create IAM user if it doesn't exist."""
    try:
        response = iam_client.create_user(UserName=username)
        print(f"✅ Created IAM user: {username}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"ℹ️  IAM user '{username}' already exists")
            return True
        else:
            print(f"❌ Failed to create IAM user: {e}")
            return False

def create_s3_bucket(s3_client, bucket_name, region):
    """Create S3 bucket if it doesn't exist."""
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"ℹ️  S3 bucket '{bucket_name}' already exists")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Bucket doesn't exist, create it
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ Created S3 bucket: {bucket_name}")
                return True
            except ClientError as create_error:
                print(f"❌ Failed to create S3 bucket: {create_error}")
                return False
        else:
            print(f"❌ Error checking S3 bucket: {e}")
            return False

def create_custom_policy(iam_client, policy_name, bucket_name):
    """Create custom IAM policy with least-privilege permissions."""
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                    "s3:PutObjectAcl"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "transcribe:StartTranscriptionJob",
                    "transcribe:GetTranscriptionJob",
                    "transcribe:DeleteTranscriptionJob",
                    "transcribe:ListTranscriptionJobs"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            }
        ]
    }
    
    try:
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description=f"Custom policy for Touch project - S3 bucket: {bucket_name}"
        )
        print(f"✅ Created custom policy: {policy_name}")
        return response['Policy']['Arn']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            # Policy exists, get its ARN
            try:
                response = iam_client.get_policy(PolicyArn=f"arn:aws:iam::{iam_client.get_user()['User']['Arn'].split(':')[4]}:policy/{policy_name}")
                print(f"ℹ️  Custom policy '{policy_name}' already exists")
                return response['Policy']['Arn']
            except ClientError:
                print(f"❌ Failed to get existing policy ARN: {e}")
                return None
        else:
            print(f"❌ Failed to create custom policy: {e}")
            return None

def attach_managed_policies(iam_client, username):
    """Attach AWS managed policies to the user."""
    managed_policies = [
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess",
        "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    ]
    
    attached_policies = []
    for policy_arn in managed_policies:
        try:
            iam_client.attach_user_policy(
                UserName=username,
                PolicyArn=policy_arn
            )
            policy_name = policy_arn.split('/')[-1]
            print(f"✅ Attached policy: {policy_name}")
            attached_policies.append(policy_arn)
        except ClientError as e:
            print(f"❌ Failed to attach policy {policy_arn}: {e}")
    
    return attached_policies

def create_access_key(iam_client, username):
    """Create access key for the IAM user."""
    try:
        response = iam_client.create_access_key(UserName=username)
        access_key = response['AccessKey']
        print(f"✅ Created access key: {access_key['AccessKeyId']}")
        return access_key
    except ClientError as e:
        print(f"❌ Failed to create access key: {e}")
        return None

def generate_env_file(access_key, bucket_name, region):
    """Generate .env file content."""
    env_content = f"""# AWS Configuration
AWS_ACCESS_KEY_ID={access_key['AccessKeyId']}
AWS_SECRET_ACCESS_KEY={access_key['SecretAccessKey']}
AWS_REGION={region}

# S3 Configuration
TOUCH_S3_BUCKET={bucket_name}
"""
    return env_content

def main():
    parser = argparse.ArgumentParser(description='Setup AWS IAM user for Touch project')
    parser.add_argument('--username', default='touch-app-user', 
                       help='IAM username (default: touch-app-user)')
    parser.add_argument('--bucket-name', required=True,
                       help='S3 bucket name for audio files')
    parser.add_argument('--region', default='us-east-1',
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--use-custom-policy', action='store_true',
                       help='Use custom policy instead of managed policies')
    parser.add_argument('--output-env', action='store_true',
                       help='Output .env file content to console')
    
    args = parser.parse_args()
    
    # Initialize AWS clients
    try:
        iam_client = boto3.client('iam')
        s3_client = boto3.client('s3', region_name=args.region)
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure your AWS credentials first.")
        print("   You can use: aws configure")
        sys.exit(1)
    
    print("🚀 Setting up AWS IAM user for Touch project...")
    print(f"   Username: {args.username}")
    print(f"   S3 Bucket: {args.bucket_name}")
    print(f"   Region: {args.region}")
    print()
    
    # Step 1: Create IAM user
    if not create_iam_user(iam_client, args.username):
        sys.exit(1)
    
    # Step 2: Create S3 bucket
    if not create_s3_bucket(s3_client, args.bucket_name, args.region):
        sys.exit(1)
    
    # Step 3: Attach policies
    if args.use_custom_policy:
        policy_name = f"{args.username}-touch-policy"
        policy_arn = create_custom_policy(iam_client, policy_name, args.bucket_name)
        if policy_arn:
            try:
                iam_client.attach_user_policy(
                    UserName=args.username,
                    PolicyArn=policy_arn
                )
                print(f"✅ Attached custom policy: {policy_name}")
            except ClientError as e:
                print(f"❌ Failed to attach custom policy: {e}")
                sys.exit(1)
    else:
        print("📋 Attaching AWS managed policies...")
        attach_managed_policies(iam_client, args.username)
    
    # Step 4: Create access key
    access_key = create_access_key(iam_client, args.username)
    if not access_key:
        sys.exit(1)
    
    # Step 5: Generate .env content
    env_content = generate_env_file(access_key, args.bucket_name, args.region)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Create a .env file in your project root with the following content:")
    print()
    
    if args.output_env:
        print(env_content)
    else:
        print("   (Use --output-env to see the content)")
    
    print("2. Test the setup:")
    print(f"   python cli.py --test-aws")
    print()
    print("3. Start converting videos:")
    print(f"   python cli.py video.mp4")
    print()
    print("⚠️  Security Notes:")
    print("- Keep your access keys secure and never commit them to version control")
    print("- Consider using IAM roles instead of access keys for production")
    print("- Rotate access keys regularly")
    print("- Monitor usage through AWS CloudTrail")

if __name__ == "__main__":
    main() 