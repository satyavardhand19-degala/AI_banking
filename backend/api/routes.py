# Vaani Smart Data Intelligence — API Routes

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from .models import QueryRequest, QueryResponse, SpeakRequest
from ai.rule_engine import rule_engine
from validators.sql_validator import validate_sql
from database.executor import execute_query, QueryExecutionError
from voice.summary_builder import build_summary # Rule-based summary
from voice import sarvam_stt, sarvam_tts
import logging
import pandas as pd
import re
import io
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

def sanitize_columns(columns):
    return [re.sub(r'\W+', '_', str(col).lower().strip()) for col in columns]

@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_io = io.BytesIO(content)
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_io)
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_io)
        else:
            return {"success": False, "error": "Unsupported file format. Please upload CSV or Excel."}
            
        if df.empty:
            return {"success": False, "error": "The uploaded file is empty."}
            
        # Drop rows where all elements are missing
        df = df.dropna(how='all')
        
        if df.empty:
            return {"success": False, "error": "The uploaded file contains only empty rows."}

        df.columns = sanitize_columns(df.columns)
        
        from database.connection import engine
        df.to_sql('user_uploaded_data', con=engine, if_exists='replace', index=False)
            
        return {"success": True, "rows_inserted": len(df)}
        
    except pd.errors.EmptyDataError:
        return {"success": False, "error": "The uploaded file is empty."}
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}", exc_info=True)
        return {"success": False, "error": "Failed to parse file: " + str(e)}


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # 1. RULE-BASED SQL PIPELINE
        sql = rule_engine.generate_sql(request.query)
        logger.info(f"Generated SQL (Rule-Engine): {sql}")

        # 2. Validate SQL for safety
        is_valid, reason = validate_sql(sql)
        if not is_valid:
            logger.warning(f"SQL validation failed: {reason}")
            return QueryResponse(success=False, error=f"Invalid SQL generated: {reason}")

        # 3. Execute the validated query
        result = execute_query(sql)

        # 4. Build a summary using programmatic logic
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
        return QueryResponse(success=False, error="An error occurred while processing your query.")


@router.post("/voice/transcribe", response_model=QueryResponse)
async def transcribe_and_query(
    audio: UploadFile = File(...),
    language_code: str = Form("en-IN")
):
    try:
        audio_bytes = await audio.read()
        transcript = await sarvam_stt.transcribe(audio_bytes, language_code)
        logger.info(f"Voice transcript: {transcript}")
        return await process_query(QueryRequest(query=transcript))
    except Exception as e:
        logger.error(f"Error in /voice/transcribe: {e}", exc_info=True)
        return QueryResponse(success=False, error="Voice processing failed.")


@router.post("/voice/speak")
async def speak_summary(request: SpeakRequest):
    try:
        audio_bytes = await sarvam_tts.synthesize(request.text, request.language_code)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")
    except Exception as e:
        logger.error(f"Error in /voice/speak: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Speech synthesis failed.")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    from database.connection import db_pool
    db_ok = db_pool.test_connection()
    
    sarvam_status = "unreachable"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.head("https://api.sarvam.ai")
            sarvam_status = "reachable" if resp.status_code < 500 else "unreachable"
    except: pass

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "sarvam": sarvam_status
    }

