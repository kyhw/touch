import argparse
import logging
import os
import sys
from app.orchestrator import run_pipeline
from app.youtube_downloader import download_youtube_video

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

def validate_input(input_path):
    """Validate input file or URL"""
    if input_path.startswith(("http://", "https://")):
        if "youtube.com" not in input_path and "youtu.be" not in input_path:
            raise ValueError("Only YouTube URLs are supported")
        return True
    else:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Touch: Convert spoken video content to Braille-optimized text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py video.mp4
  python cli.py https://www.youtube.com/watch?v=example --output my_output.txt
  python cli.py /path/to/video.mp4 --output output/braille.txt
        """
    )
    parser.add_argument("input", help="Path to video file or YouTube URL")
    parser.add_argument("--output", default="output.brf", help="Path to output file (default: output.brf)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logging.info("Touch: Video to Braille Converter")
        logging.info("=" * 40)
        
        # Validate input
        is_youtube = validate_input(args.input)
        
        # Process input
        if is_youtube:
            logging.info("Detected YouTube URL. Downloading video...")
            video_path = download_youtube_video(args.input)
            logging.info(f"Video downloaded to: {video_path}")
        else:
            video_path = args.input
            logging.info(f"Using local video file: {video_path}")
        
        # Run the pipeline
        output_file = run_pipeline(video_path, args.output)
        
        logging.info("=" * 40)
        logging.info(f"✅ Success! Braille text written to: {output_file}")
        
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Clean up downloaded YouTube video if applicable
        if 'video_path' in locals() and is_youtube:
            if os.path.exists(video_path):
                os.remove(video_path)
                logging.info(f"Cleaned up downloaded video file: {video_path}")

if __name__ == "__main__":
    main()
