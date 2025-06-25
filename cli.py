import argparse
import logging
import os
import sys
import time
from app.orchestrator import run_pipeline
from app.youtube_downloader import download_video
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
    """Validate input file or URL with enhanced checks. Supports video files, MP3 files, and YouTube/Vimeo/Dailymotion URLs."""
    if input_path.startswith(("http://", "https://")):
        # Accept YouTube, Vimeo, and Dailymotion URLs
        valid_domains = ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com", "dai.ly"]
        if not any(domain in input_path for domain in valid_domains):
            raise ValueError("Only YouTube, Vimeo, and Dailymotion URLs are supported")
        return "online_video"
    elif input_path.lower().endswith(".mp3"):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if not os.access(input_path, os.R_OK):
            raise PermissionError(f"Cannot read input file: {input_path}")
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            raise ValueError(f"Input file is empty: {input_path}")
        max_size = 500 * 1024 * 1024
        if file_size > max_size:
            logging.warning(f"Large file detected ({file_size / 1024 / 1024:.1f}MB). Processing may take longer.")
        return "mp3"
    else:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if not os.access(input_path, os.R_OK):
            raise PermissionError(f"Cannot read input file: {input_path}")
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            raise ValueError(f"Input file is empty: {input_path}")
        max_size = 500 * 1024 * 1024
        if file_size > max_size:
            logging.warning(f"Large file detected ({file_size / 1024 / 1024:.1f}MB). Processing may take longer.")
        return "video"

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
        description="Touch: Convert spoken video and MP3 content to literal Unicode Braille or Braille-optimized text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py video.mp4
  python cli.py audio.mp3
  python cli.py 'https://www.youtube.com/watch?v=example' --output my_output.txt
  python cli.py "https://vimeo.com/123456789" --output my_output.txt
  python cli.py 'https://www.dailymotion.com/video/x7xyz' --output my_output.txt
  python cli.py /path/to/video.mp4 --output output/braille.txt --braille-mode unicode

Note: Always wrap video URLs in single or double quotes to avoid shell issues.
      By default, output is literal Unicode Braille (U+2800–U+28FF). Use --braille-mode optimized for plain text.
        """
    )
    parser.add_argument("input", help="Path to video file, MP3 file, or YouTube/Vimeo/Dailymotion URL (wrap URLs in quotes)")
    parser.add_argument("--output", default="output.brf", help="Path to output file (default: output.brf, always placed in output/ directory unless a directory is specified)")
    parser.add_argument("--braille-mode", choices=["unicode", "optimized"], default="unicode", help="Braille output mode: 'unicode' for literal Unicode Braille (default), 'optimized' for Braille-optimized plain text")
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
        input_type = validate_input(args.input)
        
        # Process input
        if input_type == "online_video":
            logging.info("📺 Detected online video URL. Downloading video...")
            video_path = download_video(args.input)
            logging.info(f"✅ Video downloaded to: {video_path}")
        elif input_type == "mp3":
            video_path = args.input
            logging.info(f"🎵 Using local MP3 file: {video_path}")
        else:
            video_path = args.input
            logging.info(f"📁 Using local video file: {video_path}")

        # Force output to output/ directory unless a directory is specified
        output_path = args.output
        output_dir = os.path.dirname(output_path)
        if not output_dir:
            output_path = os.path.join("output", output_path)
            output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Run the pipeline
        start_time = time.time()
        output_file = run_pipeline(video_path, output_path, braille_mode=args.braille_mode)
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
        # Clean up downloaded video if applicable
        if 'video_path' in locals() and input_type == "online_video":
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    logging.info(f"🧹 Cleaned up downloaded video file: {video_path}")
                except Exception as e:
                    logging.warning(f"Failed to cleanup video file: {e}")

if __name__ == "__main__":
    sys.exit(main())
