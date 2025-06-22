from moviepy.editor import VideoFileClip
import logging
import os

def extract_audio(video_path, audio_path):
    logging.info(f"Extracting audio from {video_path}...")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        clip = VideoFileClip(video_path)
        
        if clip.audio is None:
            raise ValueError("Video file has no audio track")
        
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
        clip.close()
        
        if not os.path.exists(audio_path):
            raise RuntimeError("Audio extraction failed - output file not created")
        
        logging.info(f"Audio extracted successfully to {audio_path}")
        return audio_path
        
    except Exception as e:
        logging.error(f"Audio extraction failed: {e}")
        raise
