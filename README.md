# Touch: Video & Audio to Braille Converter

Convert spoken content from video files, MP3 audio, or online platforms (YouTube, Vimeo, Dailymotion) to **literal Unicode Braille** or Braille-optimized text using AWS services.

---

## Features
- 🎥 Extract audio from video files (MP4, AVI, MOV, etc.)
- 🎵 Process MP3 audio files directly
- 📺 Download and process YouTube, Vimeo, and Dailymotion videos
- 🎤 Transcribe audio using AWS Transcribe
- 🔤 Convert to literal Unicode Braille (U+2800–U+28FF) or Braille-optimized text using AWS Bedrock (Claude)
- 🗂️ Automatic cleanup of temporary files
- 📝 Comprehensive logging and error handling

---

## Prerequisites
- **Python**: 3.8–3.12 (Python 3.13+ is not supported due to audio library limitations)
- **AWS Account** with access to:
  - Amazon S3
  - Amazon Transcribe
  - Amazon Bedrock (Claude model)
- **FFmpeg** (for audio processing)

---

## Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd touch
   ```
2. **Create and activate a Python 3.12 virtual environment:**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install FFmpeg:**
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from https://ffmpeg.org/download.html

---

## AWS Setup

### Option 1: Automated Setup (Recommended)

Use the provided script to automatically create an IAM user with the necessary permissions:

1. **Configure your AWS credentials** (if not already done):
   ```bash
   aws configure
   ```

2. **Run the automated setup script:**
   ```bash
   python setup_aws_iam.py --bucket-name my-touch-bucket --output-env
   ```

   This script will:
   - Create an IAM user (`touch-app-user` by default)
   - Create an S3 bucket for audio files
   - Attach the required AWS managed policies:
     - `AmazonS3FullAccess`
     - `AmazonTranscribeFullAccess` 
     - `AmazonBedrockFullAccess`
   - Generate access keys
   - Output the `.env` file content

3. **Create the `.env` file** with the output from the script

4. **Test the setup:**
   ```bash
   python cli.py --test-aws
   ```

**Advanced options:**
- Use custom policy (more secure): `--use-custom-policy`
- Specify different username: `--username my-user`
- Specify different region: `--region us-west-2`

### Option 2: Manual Setup

If you prefer to set up AWS manually:

1. **Create an IAM user** in the AWS Console
2. **Attach these managed policies:**
   - `AmazonS3FullAccess`
   - `AmazonTranscribeFullAccess`
   - `AmazonBedrockFullAccess`
3. **Create access keys** for the user
4. **Create an S3 bucket** for audio files

---

## Configuration
Create a `.env` file in the project root:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
# S3 Configuration
TOUCH_S3_BUCKET=your-s3-bucket-name
```

---

## Usage
### Basic Examples
- **Convert a local video file to Unicode Braille:**
  ```bash
  python cli.py video.mp4
  ```
- **Convert a local MP3 file to Unicode Braille:**
  ```bash
  python cli.py audio.mp3
  ```
- **Convert a YouTube video to Unicode Braille:**
  ```bash
  python cli.py 'https://www.youtube.com/watch?v=example'
  ```

**Note:** Always wrap video URLs in single or double quotes to avoid shell issues. MP3 files are processed directly and do not require extraction from video.

### Testing and Validation
- **Test AWS connectivity:**
  ```bash
  python cli.py --test-aws
  ```
- **Check environment configuration:**
  ```bash
  python cli.py --check-env
  ```

### Output Modes
- By default, output is **literal Unicode Braille** (U+2800–U+28FF).
- To get plain Braille-optimized text instead, use:
  ```bash
  python cli.py video.mp4 --braille-mode optimized
  ```
- `--braille-mode unicode` (default): Output is literal Unicode Braille (⠞⠑⠭⠞ ...)
- `--braille-mode optimized`: Output is plain text, optimized for Braille translation software

### Viewing and Using Unicode Braille Output
- View Unicode Braille in any Unicode-aware text editor (VSCode, Sublime, Notepad++, etc.)
- Copy/paste the output into Braille embosser software, or use it with digital Braille displays that support Unicode Braille.
- For physical Braille, use translation software or embosser tools that accept Unicode Braille input.

### Advanced Usage
- **Specify output file:**
  ```bash
  python cli.py video.mp4 --output my_output.txt
  ```
- **Enable verbose logging:**
  ```bash
  python cli.py video.mp4 --verbose
  ```

---

## Monitoring & Debugging in AWS Console

- **S3 (Audio Storage):**
  - Uploaded audio files are stored in your configured S3 bucket.
  - [View your S3 bucket](https://s3.console.aws.amazon.com/s3/).
- **Transcribe (Speech-to-Text):**
  - Transcription jobs are visible in the [AWS Transcribe Console](https://console.aws.amazon.com/transcribe/).
  - Look for jobs named `touch-...`.
- **Bedrock (AI Model):**
  - Bedrock model invocations are not directly visible, but you can monitor usage and logs in the [Bedrock Console](https://console.aws.amazon.com/bedrock/).
- **CloudWatch (Logs & Errors):**
  - For detailed logs and errors, check [CloudWatch Logs](https://console.aws.amazon.com/cloudwatch/).

---

## Architecture
```
Video/Audio Input → Audio Extraction → S3 Upload → AWS Transcribe → AWS Bedrock → Braille Text
```
1. **Audio Extraction:** MoviePy for video files, pydub for MP3 files
2. **S3 Storage:** Temporary audio storage for AWS Transcribe
3. **Transcription:** AWS Transcribe converts speech to text
4. **Braille Conversion:** AWS Bedrock (Claude) outputs literal Unicode Braille or Braille-optimized text
5. **Cleanup:** Automatic removal of temporary files and S3 objects

---

## Error Handling
- Invalid input files/URLs
- Network connectivity issues
- AWS service failures
- Audio extraction problems
- Transcription timeouts

---

## Troubleshooting
- **"TOUCH_S3_BUCKET environment variable is required"**
  - Ensure your `.env` file is properly configured
  - Check that the S3 bucket exists and is accessible
- **"Video file has no audio track"**
  - Verify the video file contains audio
  - Try a different video file
- **"Transcription job failed"**
  - Check AWS credentials and permissions
  - Ensure the audio file is not corrupted
  - Verify AWS Transcribe service is available in your region
- **"audioop not found" or MP3 extraction errors**
  - Ensure you are using Python 3.12 or lower (Python 3.13+ is not supported)
- **AWS permission errors**
  - Run `python cli.py --test-aws` to diagnose specific service issues
  - Verify your IAM user has the required policies attached

---

## Cost Estimation
| Service         | Estimated Cost |
|-----------------|---------------|
| S3              | <$0.01        |
| Transcribe      | $0.12         |
| Bedrock (Claude)| $0.01–$0.02   |
| **Total**       | **$0.13–$0.15** |
- Costs scale linearly with file length.
- Using more advanced Claude models may increase Bedrock costs.
- Local compute and YouTube download are free (except for your own bandwidth/electricity).
- AWS Free Tier may cover some or all costs for new accounts.

---

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support
For issues and questions, please open an issue on GitHub.

## Output Files

- All output files are placed in the `output/` directory by default.
- Unicode Braille output (default) will be in `.txt` files, and BRF output (embossable) will be in `.brf` files.
- Example: `output/test_output.brf`

## Testing Example

This project was tested using the following YouTube video:

https://www.youtube.com/watch?v=WLQ6HyFbfKU

The pipeline was run as follows (be sure to quote the URL):

```sh
python cli.py --input-url "https://www.youtube.com/watch?v=WLQ6HyFbfKU" --braille-mode unicode
```

The resulting Braille output was saved in the `output/` directory as `test_output.brf` (for BRF) and as `.txt` for Unicode Braille.
