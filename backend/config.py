# Vaani Smart Data Intelligence — Configuration

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_service_key: str = ""

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
