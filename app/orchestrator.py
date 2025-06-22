import os
import uuid
import logging
from app.audio_extractor import extract_audio
from app.s3_handler import upload_to_s3, cleanup_s3_file
from app.transcriber import start_transcription, get_transcription_result
from app.braille_converter import to_braille
from app.config import validate_config

def run_pipeline(video_path, output_file):
    # Validate configuration first
    validate_config()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    
    # Validate input file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    audio_file = f"/tmp/{uuid.uuid4()}.wav"
    s3_uri = None
    
    try:
        logging.info(f"Starting pipeline for: {video_path}")
        
        # Extract audio
        extract_audio(video_path, audio_file)
        
        # Upload to S3
        s3_uri = upload_to_s3(audio_file, prefix="audio")
        
        # Start transcription
        job_name = f"touch-{uuid.uuid4()}"
        start_transcription(job_name, s3_uri)
        transcript = get_transcription_result(job_name)
        
        if not transcript or not transcript.strip():
            raise ValueError("Transcription resulted in empty text")
        
        # Convert to braille
        braille_text = to_braille(transcript)
        
        # Write output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(braille_text)
        
        logging.info(f"Pipeline completed successfully. Output written to {output_file}")
        return output_file
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise
    finally:
        # Clean up temporary files
        if os.path.exists(audio_file):
            os.remove(audio_file)
            logging.info(f"Cleaned up temp file: {audio_file}")
        
        # Clean up S3 file
        if s3_uri:
            cleanup_s3_file(s3_uri)
