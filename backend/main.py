# Vaani AI Banking Intelligence — Main Entry Point

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router as api_router
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup
    logger.info(f"Vaani AI Banking Assistant started — ENV: {settings.app_env}")
    logger.info("Database mode: Supabase PostgreSQL (Managed)")

    # Warm the DB pool on startup
    from database.connection import db_pool
    if db_pool.test_connection():
        logger.info("Database connection verified ✓")
    else:
        logger.warning("Database connection failed on startup — check credentials")

    yield

    # Shutdown
    logger.info("Vaani AI Banking Assistant shutting down")


app = FastAPI(
    title="Vaani — Smart Data Intelligence",
    description="Natural language interface for banking data analysis.",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api")


@app.get("/api-status")
async def api_status():
    return {"message": "Vaani AI Banking API is running. Visit /docs for documentation."}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(status_code=204, content={})


# ── Global Exception Handler — never expose stack traces ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error. Please try again."}
    )
