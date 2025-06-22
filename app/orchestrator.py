import os
import uuid
import logging
from app.audio_extractor import extract_audio
from app.s3_handler import upload_to_s3
from app.transcriber import start_transcription, get_transcription_result
from app.braille_converter import to_braille

def run_pipeline(video_path, output_file):
    audio_file = f"/tmp/{uuid.uuid4()}.wav"
    try:
        extract_audio(video_path, audio_file)
        s3_uri = upload_to_s3(audio_file, prefix="audio")

        job_name = f"touch-{uuid.uuid4()}"
        start_transcription(job_name, s3_uri)
        transcript = get_transcription_result(job_name)

        braille_text = to_braille(transcript)

        with open(output_file, "w") as f:
            f.write(braille_text)

        logging.info(f"Braille output written to {output_file}")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
            logging.info(f"Cleaned up temp file: {audio_file}")
