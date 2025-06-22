import boto3
import json
import logging
from app.config import REGION

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def to_braille(text):
    logging.info("Using Bedrock (Claude) to generate Braille-optimized text...")

    prompt = (
        f"\n\nHuman: You are a Braille translator. "
        f"Take the following English text and return a simplified, Grade 1 Braille-optimized version. "
        f"Keep it concise, literal, and semantically accurate. Avoid emojis and non-verbal characters. "
        f"Text: \"{text}\"\n\nAssistant:"
    )

    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.3,
            })
        )
        result = json.loads(response["body"].read())
        braille_text = result["completion"].strip()
        logging.info("Received AI-translated Braille-friendly text.")
        return braille_text
    except Exception as e:
        logging.error(f"Failed to invoke Bedrock: {e}")
        raise
