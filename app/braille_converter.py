import boto3
import json
import logging
import time
from app.config import REGION
import string

def to_braille(text, mode="unicode"):
    """
    Convert text to Braille using AWS Bedrock.
    mode: 'unicode' for literal Unicode Braille (U+2800–U+28FF),
          'optimized' for Braille-optimized plain text.
    """
    if not text or not text.strip():
        logging.warning("Empty text provided to braille converter")
        return text
    
    logging.info(f"Using Bedrock (Claude) to generate Braille text (mode: {mode})...")
    logging.info(f"Input text length: {len(text)} characters")

    if mode == "unicode":
        prompt = (
            f"\n\nHuman: You are an expert Braille translator. "
            f"Convert the following English text to literal Unicode Braille (using the Unicode Braille Patterns block, U+2800–U+28FF). "
            f"Output only the Braille Unicode characters, with no extra explanation or commentary. "
            f"Text: \"{text}\"\n\n"
            f"Assistant:"
        )
    else:
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

    bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    try:
        start_time = time.time()
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 1000,
                "temperature": 0.1,
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
        if mode == "unicode":
            braille_text_clean = _clean_unicode_braille(braille_text)
            # Fallback: if output is empty or mostly non-Braille, use deterministic mapping
            if not braille_text_clean or _is_mostly_non_braille(braille_text_clean, text):
                logging.warning("Bedrock did not return Unicode Braille. Using deterministic fallback conversion.")
                braille_text_clean = _fallback_to_unicode_braille(text)
            braille_text = braille_text_clean
        else:
            braille_text = _clean_braille_text(braille_text)
        logging.info(f"✅ Received AI-translated Braille text in {processing_time:.2f}s")
        logging.info(f"📊 Output text length: {len(braille_text)} characters")
        return braille_text
    except Exception as e:
        logging.error(f"❌ Failed to invoke Bedrock: {e}")
        logging.warning("🔄 Falling back to deterministic Unicode Braille conversion")
        if mode == "unicode":
            return _fallback_to_unicode_braille(text)
        return text

def _clean_braille_text(text):
    """Clean and format the Braille-optimized text for better readability."""
    if not text:
        return text
    text = text.replace("Here is the Braille-optimized version:", "").strip()
    text = text.replace("Braille-optimized version:", "").strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = ' '.join(lines)
    import re
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def _clean_unicode_braille(text):
    """Remove any non-Braille Unicode characters from the output."""
    return ''.join(c for c in text if 0x2800 <= ord(c) <= 0x28FF)

def _is_mostly_non_braille(braille_text, original_text):
    """Return True if the output is empty or much shorter than the original, indicating a failed conversion."""
    # If less than 30% of the original length, treat as failed
    return len(braille_text) < max(5, 0.3 * len(original_text))

def _fallback_to_unicode_braille(text):
    """Convert plain English to Grade 1 Unicode Braille using a direct mapping."""
    # Direct Unicode Braille mapping
    braille_alphabet = {
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
        'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
        'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
        '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑', '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚',
        ' ': '⠀', ',': '⠂', ';': '⠆', ':': '⠒', '.': '⠲', '!': '⠖', '(': '⠣', ')': '⠜', '?': '⠦', '-': '⠤', "'": '⠄', '"': '⠄', '/': '⠌'
    }
    result = []
    for char in text:
        lower = char.lower()
        if lower in braille_alphabet:
            result.append(braille_alphabet[lower])
        else:
            result.append('⠀')  # blank Braille cell
    return ''.join(result)

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
