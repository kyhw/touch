import boto3
import time
import requests
import logging
from app.config import REGION

transcribe = boto3.client("transcribe", region_name=REGION)

def start_transcription(job_name, s3_uri):
    logging.info(f"Starting transcription job: {job_name}")
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": s3_uri},
        MediaFormat="wav",
        LanguageCode="en-US"
    )

def get_transcription_result(job_name):
    logging.info(f"Polling for transcription job: {job_name}")
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)
    if job_status == 'COMPLETED':
        uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        logging.info("Transcription complete.")
        return requests.get(uri).json()['results']['transcripts'][0]['transcript']
    else:
        raise RuntimeError("Transcription job failed.")
