# Vaani AI Banking Intelligence — Configuration

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Supabase / PostgreSQL
    supabase_url: str
    supabase_service_key: str
    supabase_db_host: str
    supabase_db_port: int = 5432
    supabase_db_name: str = "postgres"
    supabase_db_user: str = "postgres"
    supabase_db_password: str

    # Anthropic AI
    anthropic_api_key: Optional[str] = None

    # OpenAI AI
    openai_api_key: str

    # Sarvam AI
    sarvam_api_key: str
    sarvam_stt_model: str = "saarika:v2"
    sarvam_tts_model: str = "bulbul:v1"
    sarvam_tts_voice: str = "meera"

    # App Settings
    allowed_origins: str = "*"
    app_env: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False

# Export singleton
settings = Settings()
