from moviepy.editor import VideoFileClip
import logging

def extract_audio(video_path, audio_path):
    logging.info(f"Extracting audio from {video_path}...")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path
