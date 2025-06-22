import boto3
import logging
import os
from app.config import REGION, BUCKET

s3 = boto3.client("s3", region_name=REGION)

def upload_to_s3(file_path, prefix="audio"):
    if not BUCKET:
        raise ValueError("TOUCH_S3_BUCKET environment variable is required")
    filename = os.path.basename(file_path)
    key = f"{prefix}/{filename}"
    logging.info(f"Uploading {file_path} to s3://{BUCKET}/{key}")
    s3.upload_file(file_path, BUCKET, key)
    return f"s3://{BUCKET}/{key}"

def cleanup_s3_file(s3_uri):
    """Clean up S3 file after processing"""
    try:
        if s3_uri.startswith("s3://"):
            bucket = s3_uri.split("/")[2]
            key = "/".join(s3_uri.split("/")[3:])
            s3.delete_object(Bucket=bucket, Key=key)
            logging.info(f"Cleaned up S3 file: {s3_uri}")
    except Exception as e:
        logging.warning(f"Failed to cleanup S3 file {s3_uri}: {e}")
