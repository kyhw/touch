from dotenv import load_dotenv
import os

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET = os.getenv("TOUCH_S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Validate required environment variables
def validate_config():
    if not BUCKET:
        raise ValueError("TOUCH_S3_BUCKET environment variable is required")
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")
