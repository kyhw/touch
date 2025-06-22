import boto3
import json
import logging
import time
from app.config import REGION

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def to_braille(text):
    """Convert text to Braille-optimized format using AWS Bedrock with enhanced error handling."""
    if not text or not text.strip():
        logging.warning("Empty text provided to braille converter")
        return text
    
    logging.info("Using Bedrock (Claude) to generate Braille-optimized text...")
    logging.info(f"Input text length: {len(text)} characters")

    # Optimize prompt for better results
    prompt = (
        f"\n\nHuman: You are an expert Braille translator and accessibility specialist. "
        f"Your task is to convert the following English text into a simplified, Grade 1 Braille-optimized version. "
        f"Follow these guidelines:\n"
        f"1. Keep the text concise and literal\n"
        f"2. Maintain semantic accuracy\n"
        f"3. Avoid emojis, special characters, and non-verbal elements\n"
        f"4. Use simple, clear language suitable for Braille reading\n"
        f"5. Preserve important information and context\n"
        f"6. Break long sentences into shorter, more readable segments\n\n"
        f"Text to convert: \"{text}\"\n\n"
        f"Assistant: Here is the Braille-optimized version:\n"
    )

    try:
        start_time = time.time()
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 1000,  # Increased for longer texts
                "temperature": 0.1,  # Lower temperature for more consistent output
                "top_p": 0.9,
                "stop_sequences": ["\n\nHuman:", "\n\nAssistant:"]
            })
        )
        
        result = json.loads(response["body"].read())
        braille_text = result["completion"].strip()
        
        processing_time = time.time() - start_time
        
        if not braille_text:
            logging.warning("⚠️  Bedrock returned empty response, using original text")
            return text
        
        # Clean up the response
        braille_text = _clean_braille_text(braille_text)
        
        logging.info(f"✅ Received AI-translated Braille-friendly text in {processing_time:.2f}s")
        logging.info(f"📊 Output text length: {len(braille_text)} characters")
        
        return braille_text
        
    except Exception as e:
        logging.error(f"❌ Failed to invoke Bedrock: {e}")
        logging.warning("🔄 Falling back to original text")
        return text

def _clean_braille_text(text):
    """Clean and format the Braille text for better readability."""
    if not text:
        return text
    
    # Remove common AI artifacts
    text = text.replace("Here is the Braille-optimized version:", "").strip()
    text = text.replace("Braille-optimized version:", "").strip()
    
    # Remove extra whitespace and normalize
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = ' '.join(lines)
    
    # Remove multiple spaces
    import re
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def validate_braille_text(text):
    """Validate that the Braille text is reasonable."""
    if not text:
        return False
    
    # Check for reasonable length (not too short, not too long)
    if len(text) < 10:
        logging.warning("Braille text seems too short")
        return False
    
    if len(text) > 10000:
        logging.warning("Braille text seems too long")
        return False
    
    # Check for common issues
    if text.lower() == "i'm sorry" or text.lower() == "i cannot":
        logging.warning("AI returned an error response")
        return False
    
    return True
