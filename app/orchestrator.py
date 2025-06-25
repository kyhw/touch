import os
import uuid
import logging
import time
from app.audio_extractor import extract_audio
from app.s3_handler import upload_to_s3, cleanup_s3_file
from app.transcriber import start_transcription, get_transcription_result
from app.braille_converter import to_braille
from app.config import validate_config

def run_pipeline(video_path, output_file, braille_mode="unicode"):
    """Run the complete video/audio to Braille pipeline with enhanced error handling and progress tracking."""
    start_time = time.time()
    
    # Validate configuration first
    validate_config()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    
    # Validate input file exists and is accessible
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.access(video_path, os.R_OK):
        raise PermissionError(f"Cannot read video file: {video_path}")
    
    # Generate unique temporary file names
    audio_file = f"/tmp/touch_audio_{uuid.uuid4()}.wav"
    s3_uri = None
    job_name = None
    
    try:
        logging.info(f"🚀 Starting Touch pipeline for: {video_path}")
        logging.info(f"📁 Output will be written to: {output_file}")
        
        # Step 1: Extract audio
        logging.info("🎵 Step 1/4: Extracting audio from video/audio file...")
        extract_audio(video_path, audio_file)
        
        # Step 2: Upload to S3
        logging.info("☁️  Step 2/4: Uploading audio to S3...")
        s3_uri = upload_to_s3(audio_file, prefix="audio")
        
        # Step 3: Start transcription
        logging.info("🎤 Step 3/4: Starting transcription...")
        job_name = f"touch-{uuid.uuid4()}"
        start_transcription(job_name, s3_uri)
        transcript = get_transcription_result(job_name)
        
        if not transcript or not transcript.strip():
            raise ValueError("Transcription resulted in empty text")
        
        logging.info(f"📝 Transcription completed. Text length: {len(transcript)} characters")
        
        # Step 4: Convert to braille
        logging.info("🔤 Step 4/4: Converting to Unicode Braille text via Bedrock...")
        braille_text = to_braille(transcript, mode=braille_mode)
        
        if not braille_text or not braille_text.strip():
            logging.warning("Braille conversion returned empty text, using original transcript")
            braille_text = transcript
        
        # Write output with proper encoding
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(braille_text)
        
        elapsed_time = time.time() - start_time
        logging.info(f"✅ Pipeline completed successfully in {elapsed_time:.2f} seconds")
        logging.info(f"📄 Output written to: {output_file}")
        logging.info(f"📊 Final text length: {len(braille_text)} characters")
        
        return output_file
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logging.error(f"❌ Pipeline failed after {elapsed_time:.2f} seconds: {e}")
        raise
    finally:
        # Clean up temporary files
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
                logging.info(f"🧹 Cleaned up temp file: {audio_file}")
            except Exception as e:
                logging.warning(f"Failed to cleanup temp file {audio_file}: {e}")
        
        # Clean up S3 file
        if s3_uri:
            try:
                cleanup_s3_file(s3_uri)
            except Exception as e:
                logging.warning(f"Failed to cleanup S3 file {s3_uri}: {e}")
        
        # Clean up transcription job if it exists
        if job_name:
            try:
                from app.transcriber import transcribe
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                logging.info(f"🧹 Cleaned up transcription job: {job_name}")
            except Exception as e:
                logging.warning(f"Failed to cleanup transcription job {job_name}: {e}")
