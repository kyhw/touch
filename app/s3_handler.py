import boto3
import logging
import os
import time
from botocore.exceptions import ClientError, NoCredentialsError
from app.config import REGION, BUCKET

s3 = boto3.client("s3", region_name=REGION)

def upload_to_s3(file_path, prefix="audio", max_retries=3):
    """Upload file to S3 with enhanced error handling and retry logic."""
    if not BUCKET:
        raise ValueError("TOUCH_S3_BUCKET environment variable is required")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {file_path}")
    
    filename = os.path.basename(file_path)
    key = f"{prefix}/{filename}"
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise ValueError(f"File is empty: {file_path}")
    
    logging.info(f"☁️  Uploading {file_path} to s3://{BUCKET}/{key}")
    logging.info(f"📊 File size: {file_size / 1024:.1f}KB")
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            
            s3.upload_file(
                file_path, 
                BUCKET, 
                key,
                ExtraArgs={
                    'ContentType': 'audio/wav',
                    'Metadata': {
                        'uploaded-by': 'touch-app',
                        'original-filename': filename
                    }
                }
            )
            
            upload_time = time.time() - start_time
            logging.info(f"✅ Upload completed in {upload_time:.2f}s (attempt {attempt + 1})")
            
            return f"s3://{BUCKET}/{key}"
            
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not found. Please configure your AWS credentials.")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise RuntimeError(f"S3 bucket '{BUCKET}' does not exist or is not accessible")
            elif error_code == 'AccessDenied':
                raise RuntimeError(f"Access denied to S3 bucket '{BUCKET}'. Check your permissions.")
            else:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"S3 upload failed after {max_retries} attempts: {e}")
                logging.warning(f"Upload attempt {attempt + 1} failed, retrying... ({e})")
                time.sleep(2 ** attempt)  # Exponential backoff
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Unexpected error during S3 upload: {e}")
            logging.warning(f"Upload attempt {attempt + 1} failed, retrying... ({e})")
            time.sleep(2 ** attempt)

def cleanup_s3_file(s3_uri, max_retries=3):
    """Clean up S3 file after processing with retry logic."""
    if not s3_uri or not s3_uri.startswith("s3://"):
        logging.warning(f"Invalid S3 URI for cleanup: {s3_uri}")
        return
    
    try:
        bucket = s3_uri.split("/")[2]
        key = "/".join(s3_uri.split("/")[3:])
        
        logging.info(f"🧹 Cleaning up S3 file: s3://{bucket}/{key}")
        
        for attempt in range(max_retries):
            try:
                s3.delete_object(Bucket=bucket, Key=key)
                logging.info(f"✅ S3 file cleaned up successfully: {s3_uri}")
                return
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    logging.info(f"File already deleted: {s3_uri}")
                    return
                elif attempt == max_retries - 1:
                    logging.warning(f"Failed to cleanup S3 file {s3_uri}: {e}")
                    return
                else:
                    logging.warning(f"Cleanup attempt {attempt + 1} failed, retrying... ({e})")
                    time.sleep(1)
                    
    except Exception as e:
        logging.warning(f"Failed to cleanup S3 file {s3_uri}: {e}")

def check_s3_bucket_access():
    """Check if S3 bucket is accessible and writable."""
    if not BUCKET:
        return False, "TOUCH_S3_BUCKET environment variable is not set"
    
    try:
        # Try to list objects (read access)
        s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
        
        # Try to upload a small test file (write access)
        test_key = "touch-test/test-access.txt"
        s3.put_object(
            Bucket=BUCKET,
            Key=test_key,
            Body="test",
            ContentType="text/plain"
        )
        
        # Clean up test file
        s3.delete_object(Bucket=BUCKET, Key=test_key)
        
        return True, "S3 bucket is accessible and writable"
        
    except NoCredentialsError:
        return False, "AWS credentials not found"
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            return False, f"S3 bucket '{BUCKET}' does not exist"
        elif error_code == 'AccessDenied':
            return False, f"Access denied to S3 bucket '{BUCKET}'"
        else:
            return False, f"S3 access error: {e}"
    except Exception as e:
        return False, f"Unexpected error checking S3 access: {e}"
