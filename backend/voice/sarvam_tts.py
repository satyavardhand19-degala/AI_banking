# Vaani AI Banking Intelligence — Sarvam TTS Client

import httpx
import base64
from config import settings
import logging

logger = logging.getLogger(__name__)

class SarvamTTSError(Exception):
    pass

async def synthesize(text: str, language_code: str = "en-IN") -> bytes:
    """
    Synthesizes text to speech using Sarvam AI's bulbul:v1 model.
    """
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": settings.sarvam_api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": [text],
        "target_language_code": language_code,
        "speaker": settings.sarvam_tts_voice,
        "model": settings.sarvam_tts_model,
        "enable_preprocessing": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            if response.status_code == 200:
                audio_base64 = response.json().get("audios", [])[0]
                return base64.b64decode(audio_base64)
            else:
                logger.error(f"Sarvam TTS Failed: {response.status_code} {response.text}")
                raise SarvamTTSError(f"TTS failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Error in Sarvam TTS: {e}")
            raise SarvamTTSError(str(e))
