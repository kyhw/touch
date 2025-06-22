import argparse
import logging
import os
import sys
import time
from app.orchestrator import run_pipeline
from app.youtube_downloader import download_youtube_video
from app.s3_handler import check_s3_bucket_access

def setup_logging(verbose=False):
    """Setup logging with appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    format_string = '[%(asctime)s] %(levelname)s: %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_input(input_path):
    """Validate input file or URL with enhanced checks."""
    if input_path.startswith(("http://", "https://")):
        if "youtube.com" not in input_path and "youtu.be" not in input_path:
            raise ValueError("Only YouTube URLs are supported")
        return True
    else:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if not os.access(input_path, os.R_OK):
            raise PermissionError(f"Cannot read input file: {input_path}")
        
        # Check file size
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            raise ValueError(f"Input file is empty: {input_path}")
        
        # Check if it's a reasonable size (500MB limit)
        max_size = 500 * 1024 * 1024
        if file_size > max_size:
            logging.warning(f"Large file detected ({file_size / 1024 / 1024:.1f}MB). Processing may take longer.")
        
        return False

def check_environment():
    """Check if the environment is properly configured."""
    logging.info("🔍 Checking environment configuration...")
    
    # Check S3 access
    s3_accessible, s3_message = check_s3_bucket_access()
    if not s3_accessible:
        logging.error(f"❌ S3 access issue: {s3_message}")
        return False
    
    logging.info(f"✅ S3 access: {s3_message}")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Touch: Convert spoken video content to Braille-optimized text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py video.mp4
  python cli.py https://www.youtube.com/watch?v=example --output my_output.txt
  python cli.py /path/to/video.mp4 --output output/braille.txt --verbose
        """
    )
    parser.add_argument("input", help="Path to video file or YouTube URL")
    parser.add_argument("--output", default="output.brf", help="Path to output file (default: output.brf)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--check-env", action="store_true", help="Check environment configuration and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        logging.info("🎯 Touch: Video to Braille Converter")
        logging.info("=" * 50)
        
        # Environment check
        if args.check_env:
            if check_environment():
                logging.info("✅ Environment check passed!")
                return 0
            else:
                logging.error("❌ Environment check failed!")
                return 1
        
        # Validate input
        logging.info("🔍 Validating input...")
        is_youtube = validate_input(args.input)
        
        # Process input
        if is_youtube:
            logging.info("📺 Detected YouTube URL. Downloading video...")
            video_path = download_youtube_video(args.input)
            logging.info(f"✅ Video downloaded to: {video_path}")
        else:
            video_path = args.input
            logging.info(f"📁 Using local video file: {video_path}")
        
        # Run the pipeline
        start_time = time.time()
        output_file = run_pipeline(video_path, args.output)
        total_time = time.time() - start_time
        
        logging.info("=" * 50)
        logging.info(f"🎉 Success! Processing completed in {total_time:.2f} seconds")
        logging.info(f"📄 Braille text written to: {output_file}")
        
        # Show file info
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                char_count = len(content)
                word_count = len(content.split())
            
            logging.info(f"📊 Output file stats:")
            logging.info(f"   - File size: {file_size} bytes")
            logging.info(f"   - Characters: {char_count}")
            logging.info(f"   - Words: {word_count}")
        
        return 0
        
    except KeyboardInterrupt:
        logging.info("\n⏹️  Operation cancelled by user")
        return 1
    except FileNotFoundError as e:
        logging.error(f"❌ File not found: {e}")
        return 1
    except PermissionError as e:
        logging.error(f"❌ Permission error: {e}")
        return 1
    except ValueError as e:
        logging.error(f"❌ Invalid input: {e}")
        return 1
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            logging.debug(traceback.format_exc())
        return 1
    finally:
        # Clean up downloaded YouTube video if applicable
        if 'video_path' in locals() and is_youtube:
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    logging.info(f"🧹 Cleaned up downloaded video file: {video_path}")
                except Exception as e:
                    logging.warning(f"Failed to cleanup video file: {e}")

if __name__ == "__main__":
    sys.exit(main())
