from moviepy.editor import VideoFileClip
import logging
import os
import tempfile
import shutil
from pydub import AudioSegment

def extract_audio(video_path, audio_path):
    """Extract audio from video or MP3 file with enhanced error handling and performance optimizations."""
    logging.info(f"Extracting audio from {video_path}...")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.access(video_path, os.R_OK):
        raise PermissionError(f"Cannot read video file: {video_path}")
    
    # Check file size to avoid processing extremely large files
    file_size = os.path.getsize(video_path)
    max_size = 500 * 1024 * 1024  # 500MB limit
    if file_size > max_size:
        logging.warning(f"Large video file detected ({file_size / 1024 / 1024:.1f}MB). Processing may take longer.")

    # MP3 support
    if video_path.lower().endswith('.mp3'):
        try:
            logging.info("Detected MP3 file. Converting to WAV format for processing...")
            audio = AudioSegment.from_mp3(video_path)
            # Export as 16kHz, mono, 16-bit PCM WAV
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            audio.export(audio_path, format="wav")
            audio_size = os.path.getsize(audio_path)
            if audio_size == 0:
                raise RuntimeError("Extracted audio file is empty")
            logging.info(f"✅ Audio extracted successfully to {audio_path}")
            logging.info(f"📊 Audio file size: {audio_size / 1024:.1f}KB")
            return audio_path
        except Exception as e:
            logging.error(f"❌ MP3 audio extraction failed: {e}")
            raise
    
    clip = None
    temp_audio = None
    
    try:
        # Load video with optimized settings
        clip = VideoFileClip(video_path, verbose=False)
        
        if clip.audio is None:
            raise ValueError("Video file has no audio track")
        
        # Check video duration
        duration = clip.duration
        if duration > 3600:  # 1 hour limit
            logging.warning(f"Long video detected ({duration/60:.1f} minutes). Processing may take significant time.")
        
        # Extract audio with optimized settings
        logging.info(f"Video duration: {duration:.1f} seconds")
        logging.info(f"Audio extraction in progress...")
        
        # Use temporary file first to avoid corruption
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        # Extract audio with optimized parameters
        clip.audio.write_audiofile(
            temp_audio_path,
            verbose=False,
            fps=16000,  # Standard sample rate for speech
            nbytes=2,   # 16-bit audio
            codec='pcm_s16le'  # Standard PCM codec
        )
        
        # Move to final location
        shutil.move(temp_audio_path, audio_path)
        
        if not os.path.exists(audio_path):
            raise RuntimeError("Audio extraction failed - output file not created")
        
        # Verify the extracted audio file
        audio_size = os.path.getsize(audio_path)
        if audio_size == 0:
            raise RuntimeError("Extracted audio file is empty")
        
        logging.info(f"✅ Audio extracted successfully to {audio_path}")
        logging.info(f"📊 Audio file size: {audio_size / 1024:.1f}KB")
        return audio_path
        
    except Exception as e:
        logging.error(f"❌ Audio extraction failed: {e}")
        # Clean up partial files
        if temp_audio and os.path.exists(temp_audio.name):
            try:
                os.unlink(temp_audio.name)
            except:
                pass
        raise
    finally:
        # Clean up video clip
        if clip:
            try:
                clip.close()
            except Exception as e:
                logging.warning(f"Failed to close video clip: {e}")
