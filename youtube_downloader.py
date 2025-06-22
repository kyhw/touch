import yt_dlp
import uuid
import os

def download_youtube_video(url):
    output_dir = "/tmp"
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path
