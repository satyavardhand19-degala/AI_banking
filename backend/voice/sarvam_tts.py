# Vaani — Sarvam TTS Client

import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

class SarvamTTSError(Exception):
    pass

async def synthesize(text: str, language_code: str = "en-IN") -> bytes:
    """Synthesizes text to speech using Sarvam AI."""
    if not settings.sarvam_api_key or settings.sarvam_api_key == "dummy":
        raise SarvamTTSError("TTS Disabled (No API Key)")

    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": settings.sarvam_api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": [text.replace('"', "'")],
        "target_language_code": language_code,
        "model": settings.sarvam_tts_model,
        "speaker": settings.sarvam_tts_voice,
        "enable_preprocessing": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.content
            else:
                raise SarvamTTSError(f"TTS failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Error in Sarvam TTS: {e}")
            raise SarvamTTSError(str(e))
