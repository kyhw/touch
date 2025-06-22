from dotenv import load_dotenv
import os

load_dotenv()

REGION = os.getenv("AWS_REGION", "ap-northeast-2")
BUCKET = os.getenv("touch-ai-braille")
