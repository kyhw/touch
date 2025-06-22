import argparse
import logging
import os
from app.orchestrator import run_pipeline
from app.youtube_downloader import download_youtube_video

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description="Touch: Convert spoken video to Braille.")
    parser.add_argument("input", help="Path to video file or YouTube URL")
    parser.add_argument("--output", default="output.brf", help="Path to output Braille file")
    args = parser.parse_args()

    try:
        # Check if input is a URL
        if args.input.startswith("http://") or args.input.startswith("https://"):
            logging.info("Detected YouTube URL. Downloading video...")
            video_path = download_youtube_video(args.input)
        else:
            video_path = args.input

        # Run the full pipeline
        run_pipeline(video_path, args.output)

    finally:
        # Clean up downloaded YouTube video if applicable
        if 'video_path' in locals() and args.input.startswith("http"):
            if os.path.exists(video_path):
                os.remove(video_path)
                logging.info(f"Cleaned up downloaded video file: {video_path}")

if __name__ == "__main__":
    main()
