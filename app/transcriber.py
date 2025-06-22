import boto3
import time
import requests
import logging
from app.config import REGION

transcribe = boto3.client("transcribe", region_name=REGION)

def start_transcription(job_name, s3_uri):
    logging.info(f"Starting transcription job: {job_name}")
    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat="wav",
            LanguageCode="en-US"
        )
    except Exception as e:
        logging.error(f"Failed to start transcription job: {e}")
        raise

def get_transcription_result(job_name, timeout_minutes=30):
    logging.info(f"Polling for transcription job: {job_name}")
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while True:
        try:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status == 'COMPLETED':
                uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                logging.info("Transcription completed successfully.")
                response = requests.get(uri)
                response.raise_for_status()
                transcript = response.json()['results']['transcripts'][0]['transcript']
                return transcript
            elif job_status == 'FAILED':
                failure_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown error')
                raise RuntimeError(f"Transcription job failed: {failure_reason}")
            
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Transcription job timed out after {timeout_minutes} minutes")
            
            time.sleep(10)  # Poll every 10 seconds
            
        except requests.RequestException as e:
            logging.error(f"Failed to get transcription result: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during transcription polling: {e}")
            raise
