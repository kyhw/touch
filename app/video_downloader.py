import yt_dlp
import uuid
import os
import glob

def download_video(url):
    """
    Download audio from a YouTube, Vimeo, or Dailymotion video using yt_dlp.
    Returns the path to the downloaded file.
    """
    output_dir = "/tmp"
    base_name = str(uuid.uuid4())
    base_path = os.path.join(output_dir, base_name)

    ydl_opts = {
        'format': 'bestaudio[ext=webm]/bestaudio/best',
        'outtmpl': base_path + '.%(ext)s',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Glob to find the actual downloaded file regardless of extension
    matches = glob.glob(base_path + ".*")
    if not matches:
        raise FileNotFoundError("Download failed: no file found.")

    final_path = matches[0]
    return final_path
