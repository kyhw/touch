#!/usr/bin/env python3
"""
Test script to validate Touch setup and dependencies
"""

import sys
import importlib
import subprocess
import os

def test_imports():
    """Test if all required modules can be imported"""
    modules = [
        'moviepy',
        'boto3', 
        'requests',
        'dotenv',
        'yt_dlp'
    ]
    
    print("Testing module imports...")
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    return True

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\nTesting FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg returned non-zero exit code")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found. Please install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg test timed out")
        return False

def test_env_file():
    """Test if .env file exists"""
    print("\nTesting environment configuration...")
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Please copy env.example to .env and configure your AWS credentials")
        return False

def test_app_modules():
    """Test if app modules can be imported"""
    print("\nTesting app modules...")
    modules = [
        'app.config',
        'app.audio_extractor', 
        'app.transcriber',
        'app.braille_converter',
        'app.s3_handler',
        'app.youtube_downloader',
        'app.orchestrator'
    ]
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    return True

def main():
    print("Touch: Setup Validation")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test FFmpeg
    if not test_ffmpeg():
        all_passed = False
    
    # Test env file
    test_env_file()  # Warning only, not critical
    
    # Test app modules
    if not test_app_modules():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All critical tests passed!")
        print("   You can now run: python cli.py --help")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 