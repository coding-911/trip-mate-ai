# app/core/config.py
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ELASTICSEARCH_HOSTS: str
    ELASTIC_USERNAME: str
    ELASTIC_PASSWORD: str
    KAKAO_REST_API_KEY: str
    GOOGLE_API_KEY: str

    class Config:
        env_file = (
            ".env.local" if os.getenv("ENV") == "local"
            else ".env.docker" if os.getenv("ENV") == "docker"
            else ".env"  # fallback
        )

settings = Settings()

print(">>> Loaded ENV:", os.getenv("ENV"))
print("✅ Loaded DATABASE_URL:", repr(settings.DATABASE_URL))
print("✅ Loaded ELASTICSEARCH_HOSTS:", repr(settings.ELASTICSEARCH_HOSTS))
