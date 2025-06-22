import boto3
import logging
import os
from app.config import REGION, BUCKET

s3 = boto3.client("s3", region_name=REGION)

def upload_to_s3(file_path, prefix="audio"):
    if not BUCKET:
        raise ValueError("TOUCH_S3_BUCKET is not set.")
    filename = os.path.basename(file_path)
    key = f"{prefix}/{filename}"
    logging.info(f"Uploading {file_path} to s3://{BUCKET}/{key}")
    s3.upload_file(file_path, BUCKET, key)
    return f"s3://{BUCKET}/{key}"
