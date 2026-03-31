# Vaani AI Banking Intelligence — Main Entry Point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vaani — AI Banking Intelligence",
    description="Natural language and voice interface for banking data."
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

@app.on_event("startup")
async def startup_event():
    logger.info(f"Vaani AI Banking Assistant started — ENV: {settings.app_env}")

@app.get("/")
async def root():
    return {"message": "Vaani AI Banking API is running. Visit /docs for documentation."}
