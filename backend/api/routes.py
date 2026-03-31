# Vaani AI Banking Intelligence — API Routes

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from .models import QueryRequest, SpeakRequest, QueryResponse
from ai.claude_client import openai_client
from validators.sql_validator import validate_sql
from database.executor import execute_query, QueryExecutionError
from voice.summary_builder import build_summary
from voice import sarvam_stt, sarvam_tts
import io
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # 1. Generate SQL
        sql = openai_client.generate_sql(request.query)
        
        # 2. Validate SQL
        is_valid, reason = validate_sql(sql)
        if not is_valid:
            return QueryResponse(success=False, error=f"Invalid SQL generated: {reason}")
            
        # 3. Execute Query
        result = execute_query(sql)
        
        # 4. Build Summary
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
        return QueryResponse(success=False, error=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in /query: {e}")
        return QueryResponse(success=False, error="An unexpected error occurred.")

@router.post("/voice/transcribe", response_model=QueryResponse)
async def transcribe_and_query(
    audio: UploadFile = File(...),
    language_code: str = Form("en-IN")
):
    try:
        # 1. Read audio bytes
        audio_bytes = await audio.read()
        
        # 2. Transcribe
        transcript = await sarvam_stt.transcribe(audio_bytes, language_code)
        
        # 3. Run through query pipeline
        return await process_query(QueryRequest(query=transcript))
    except Exception as e:
        logger.error(f"Error in /voice/transcribe: {e}")
        return QueryResponse(success=False, error=str(e))

@router.post("/voice/speak")
async def speak_summary(request: SpeakRequest):
    try:
        audio_bytes = await sarvam_tts.synthesize(request.text, request.language_code)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")
    except Exception as e:
        logger.error(f"Error in /voice/speak: {e}")
        raise HTTPException(status_code=502, detail="Text-to-speech synthesis failed.")

@router.get("/health")
async def health_check():
    from database.connection import db_pool
    db_ok = db_pool.test_connection()
    return {
        "status": "ok",
        "database": "connected" if db_ok else "disconnected"
    }
