import boto3
import time
import requests
import logging
from app.config import REGION

transcribe = boto3.client("transcribe", region_name=REGION)

def start_transcription(job_name, s3_uri):
    """
    Start an AWS Transcribe job for the given S3 URI.
    Uses minimal settings for single-speaker, single-alternative transcription.
    """
    logging.info(f"Starting transcription job: {job_name}")
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat="wav",
            LanguageCode="en-US",
            Settings={
                "ShowSpeakerLabels": False,
                "ShowAlternatives": False
            }
        )
        job_status = response['TranscriptionJob']['TranscriptionJobStatus']
        if job_status == 'FAILED':
            failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
            raise RuntimeError(f"Transcription job failed immediately: {failure_reason}")
        logging.info(f"✅ Transcription job started successfully: {job_name}")
        return response
    except Exception as e:
        logging.error(f"❌ Failed to start transcription job: {e}")
        raise

def get_transcription_result(job_name, timeout_minutes=30, poll_interval=10):
    """Get transcription result with enhanced polling and error handling."""
    logging.info(f"Polling for transcription job: {job_name}")
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    # Track polling attempts for better logging
    poll_count = 0
    
    while True:
        poll_count += 1
        elapsed = time.time() - start_time
        
        try:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status == 'COMPLETED':
                uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                logging.info(f"✅ Transcription completed successfully after {elapsed:.1f} seconds")
                
                # Download transcript with retry logic
                transcript = _download_transcript_with_retry(uri)
                return transcript
                
            elif job_status == 'FAILED':
                failure_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown error')
                raise RuntimeError(f"Transcription job failed: {failure_reason}")
            
            elif job_status == 'IN_PROGRESS':
                if poll_count % 6 == 0:  # Log every minute
                    logging.info(f"⏳ Transcription in progress... ({elapsed:.0f}s elapsed)")
            
            # Check timeout
            if elapsed > timeout_seconds:
                raise TimeoutError(f"Transcription job timed out after {timeout_minutes} minutes")
            
            time.sleep(poll_interval)
            
        except requests.RequestException as e:
            logging.error(f"❌ Network error during transcription polling: {e}")
            if elapsed > timeout_seconds:
                raise
            time.sleep(poll_interval * 2)  # Longer delay on network errors
            
        except Exception as e:
            logging.error(f"❌ Unexpected error during transcription polling: {e}")
            raise

def _download_transcript_with_retry(uri, max_retries=3):
    """Download transcript with retry logic for network resilience."""
    for attempt in range(max_retries):
        try:
            response = requests.get(uri, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            transcript = data['results']['transcripts'][0]['transcript']
            
            if not transcript or not transcript.strip():
                raise ValueError("Transcript is empty")
            
            logging.info(f"📝 Downloaded transcript successfully (attempt {attempt + 1})")
            return transcript
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to download transcript after {max_retries} attempts: {e}")
            logging.warning(f"Download attempt {attempt + 1} failed, retrying... ({e})")
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid transcript format: {e}")

def cleanup_transcription_job(job_name):
    """Clean up transcription job to avoid clutter."""
    try:
        transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        logging.info(f"🧹 Cleaned up transcription job: {job_name}")
    except Exception as e:
        logging.warning(f"Failed to cleanup transcription job {job_name}: {e}")
