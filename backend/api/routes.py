# Vaani AI Banking Intelligence — API Routes

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from .models import QueryRequest, SpeakRequest, QueryResponse
from ai.claude_client import openai_client
from validators.sql_validator import validate_sql
from database.executor import execute_query, QueryExecutionError
from voice.summary_builder import build_summary
from voice import sarvam_stt, sarvam_tts
import httpx
import io
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # 1. Generate SQL from natural language
        sql = openai_client.generate_sql(request.query)
        logger.info(f"Generated SQL: {sql}")

        # 2. Validate SQL for safety
        is_valid, reason = validate_sql(sql)
        if not is_valid:
            logger.warning(f"SQL validation failed: {reason}")
            return QueryResponse(success=False, error=f"Invalid SQL generated: {reason}")

        # 3. Execute the validated query
        result = execute_query(sql)

        # 4. Build a speakable summary
        summary = build_summary(request.query, result["columns"], result["rows"], result["count"])

        return QueryResponse(
            success=True,
            sql=sql,
            columns=result["columns"],
            rows=result["rows"],
            count=result["count"],
            summary=summary
        )
    except QueryExecutionError as e:
        logger.error(f"Database execution error: {e}")
        return QueryResponse(success=False, error=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in /query: {e}", exc_info=True)
        return QueryResponse(success=False, error="An error occurred while processing your query. Please try again.")


@router.post("/voice/transcribe", response_model=QueryResponse)
async def transcribe_and_query(
    audio: UploadFile = File(...),
    language_code: str = Form("en-IN")
):
    try:
        # 1. Read audio bytes from the uploaded file
        audio_bytes = await audio.read()
        if len(audio_bytes) == 0:
            return QueryResponse(success=False, error="Empty audio file received.")

        # 2. Transcribe audio to text via Sarvam STT
        transcript = await sarvam_stt.transcribe(audio_bytes, language_code)
        if not transcript or not transcript.strip():
            return QueryResponse(success=False, error="Could not transcribe audio. Please try again.")

        logger.info(f"Voice transcript: {transcript}")

        # 3. Run the transcribed text through the same query pipeline
        return await process_query(QueryRequest(query=transcript))
    except sarvam_stt.SarvamSTTError as e:
        logger.error(f"Sarvam STT error: {e}")
        return QueryResponse(success=False, error="Voice transcription failed. Please try again.")
    except Exception as e:
        logger.error(f"Error in /voice/transcribe: {e}", exc_info=True)
        return QueryResponse(success=False, error="Voice processing failed. Please try again.")


@router.post("/voice/speak")
async def speak_summary(request: SpeakRequest):
    try:
        audio_bytes = await sarvam_tts.synthesize(request.text, request.language_code)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")
    except sarvam_tts.SarvamTTSError as e:
        logger.error(f"Sarvam TTS error: {e}")
        raise HTTPException(status_code=502, detail="Text-to-speech synthesis failed.")
    except Exception as e:
        logger.error(f"Error in /voice/speak: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Text-to-speech synthesis failed.")


@router.get("/health")
async def health_check():
    """Health check endpoint — verifies DB connectivity and Sarvam AI reachability."""
    from database.connection import db_pool

    # Check database
    db_ok = db_pool.test_connection()

    # Check Sarvam AI reachability
    sarvam_status = "unreachable"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.head("https://api.sarvam.ai")
            sarvam_status = "reachable" if response.status_code < 500 else "unreachable"
    except Exception:
        sarvam_status = "unreachable"

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "sarvam": sarvam_status
    }
