# Vaani Smart Data Intelligence — Configuration

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database / PostgreSQL
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_db_host: str = "localhost"
    supabase_db_port: int = 5432
    supabase_db_name: str = "postgres"
    supabase_db_user: str = "postgres"
    supabase_db_password: str = ""

    # Sarvam AI (Voice Only)
    sarvam_api_key: str = "dummy"
    sarvam_stt_model: str = "saarika:v2"
    sarvam_tts_model: str = "bulbul:v1"
    sarvam_tts_voice: str = "meera"

    # App Settings
    allowed_origins: str = "*"
    app_env: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Export singleton
settings = Settings()
