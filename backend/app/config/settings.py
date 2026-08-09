import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    SUPABASE_URL: str = "https://mock-supabase.supabase.co"
    SUPABASE_KEY: str = "mock-key"
    GROQ_API_KEY: Optional[str] = "mock-groq-key"
    GEMINI_API_KEY: Optional[str] = "mock-gemini-key"
    AI_PROVIDER: str = "groq"  # "groq" or "gemini"
    WHATSAPP_TOKEN: str = "mock-whatsapp-token"
    WHATSAPP_PHONE_NUMBER_ID: str = "mock-phone-id"
    VERIFY_TOKEN: str = "homehelp-verify-token"
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
