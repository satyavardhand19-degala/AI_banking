# Vaani AI Banking Intelligence — Sarvam STT Client

import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

class SarvamSTTError(Exception):
    pass

async def transcribe(audio_bytes: bytes, language_code: str = "en-IN") -> str:
    """
    Transcribes audio bytes to text using Sarvam AI's saarika:v2 model.
    """
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {
        "api-subscription-key": settings.sarvam_api_key
    }
    
    files = {
        "file": ("audio.webm", audio_bytes, "audio/webm")
    }
    data = {
        "model": settings.sarvam_stt_model,
        "language_code": language_code
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, files=files, data=data, timeout=30.0)
            if response.status_code == 200:
                return response.json().get("transcript", "")
            else:
                logger.error(f"Sarvam STT Failed: {response.status_code} {response.text}")
                raise SarvamSTTError(f"STT failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Error in Sarvam STT: {e}")
            raise SarvamSTTError(str(e))
