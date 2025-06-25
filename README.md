# Touch: Video to Braille Converter

Convert spoken video content to Braille-optimized text using AWS services.

## Features

- 🎥 Extract audio from video files (MP4, AVI, MOV, etc.)
- 📺 Download and process YouTube videos
- 🎤 Transcribe audio using AWS Transcribe
- 🔤 Convert to Braille-optimized text using AWS Bedrock (Claude)
- 🗂️ Automatic cleanup of temporary files
- 📝 Comprehensive logging and error handling

## Prerequisites

- Python 3.8+
- AWS Account with access to:
  - Amazon S3
  - Amazon Transcribe
  - Amazon Bedrock (Claude model)
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd touch
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/download.html

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

## Usage

### Basic Usage

Convert a local video file:
```bash
python cli.py video.mp4
```

Convert a YouTube video:
```bash
python cli.py https://www.youtube.com/watch?v=example
```

### Advanced Usage

Specify output file:
```bash
python cli.py video.mp4 --output my_output.txt
```

Enable verbose logging:
```bash
python cli.py video.mp4 --verbose
```

### Output

The tool generates a text file containing Braille-optimized content that can be:
- Read by screen readers
- Converted to physical Braille using Braille printers
- Used in accessibility applications

## Architecture

```
Video Input → Audio Extraction → S3 Upload → AWS Transcribe → AWS Bedrock → Braille Text
```

1. **Audio Extraction**: Uses MoviePy to extract audio from video files
2. **S3 Storage**: Temporarily stores audio for AWS Transcribe processing
3. **Transcription**: AWS Transcribe converts speech to text
4. **Braille Conversion**: AWS Bedrock (Claude) optimizes text for Braille
5. **Cleanup**: Automatic removal of temporary files and S3 objects

## Error Handling

The tool includes comprehensive error handling for:
- Invalid input files/URLs
- Network connectivity issues
- AWS service failures
- Audio extraction problems
- Transcription timeouts

## Troubleshooting

### Common Issues

1. **"TOUCH_S3_BUCKET environment variable is required"**
   - Ensure your `.env` file is properly configured
   - Check that the S3 bucket exists and is accessible

2. **"Video file has no audio track"**
   - Verify the video file contains audio
   - Try a different video file

3. **"Transcription job failed"**
   - Check AWS credentials and permissions
   - Ensure the audio file is not corrupted
   - Verify AWS Transcribe service is available in your region

### Debug Mode

Run with verbose logging to see detailed information:
```bash
python cli.py video.mp4 --verbose
```

## Cost Estimation

Running Touch on a 5-minute video incurs costs primarily from AWS services. Here is a rough estimate for a single 5-minute video:

| Service         | Estimated Cost |
|-----------------|---------------|
| S3              | <$0.01        |
| Transcribe      | $0.12         |
| Bedrock (Claude)| $0.01–$0.02   |
| **Total**       | **$0.13–$0.15** |

- **S3**: Used for temporary audio storage and transfer. Cost is negligible for small files.
- **AWS Transcribe**: Main cost driver. Priced at ~$0.024 per minute of audio.
- **AWS Bedrock (Claude)**: Used for Braille conversion. Priced per 1,000 tokens; cost is low for short transcripts.

**Note:**
- Costs scale linearly with video length.
- Using more advanced Claude models may increase Bedrock costs.
- Local compute and YouTube download are free (except for your own bandwidth/electricity).
- AWS Free Tier may cover some or all costs for new accounts.

These estimates are based on 2024 AWS pricing and may vary by region or usage.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
