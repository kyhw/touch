import argparse
import logging
from app.orchestrator import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description="Touch: Convert spoken video to Braille.")
    parser.add_argument("video", help="Path to input video file")
    parser.add_argument("--output", default="output.brf", help="Path to output Braille file")
    args = parser.parse_args()

    run_pipeline(args.video, args.output)

if __name__ == "__main__":
    main()
