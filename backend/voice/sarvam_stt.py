# Vaani — Sarvam STT Client

import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

class SarvamSTTError(Exception):
    pass

async def transcribe(audio_bytes: bytes, language_code: str = "en-IN") -> str:
    """Transcribes audio bytes to text using Sarvam AI."""
    if not settings.sarvam_api_key or settings.sarvam_api_key == "dummy":
        logger.warning("Sarvam API key missing. Returning demo text.")
        return "Show all records"
        
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": settings.sarvam_api_key}
    files = {"file": ("audio.webm", audio_bytes, "audio/webm")}
    data = {"model": settings.sarvam_stt_model, "language_code": language_code}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, files=files, data=data, timeout=30.0)
            if response.status_code == 200:
                return response.json().get("transcript", "")
            else:
                logger.error(f"Sarvam STT Failed: {response.status_code}")
                return "Show all records"
        except Exception as e:
            logger.error(f"Error in Sarvam STT: {e}")
            return "Show all records"
