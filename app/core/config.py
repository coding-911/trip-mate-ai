# app/core/config.py
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # === Database ===
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # === Auth & Security ===
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Elasticsearch ===
    ELASTICSEARCH_HOSTS: str
    ELASTIC_USERNAME: str
    ELASTIC_PASSWORD: str

    # === Redis ===
    REDIS_HOST: str
    REDIS_PORT: int

    # === External Services ===
    KAKAO_REST_API_KEY: str    
    GOOGLE_API_KEY: str

    class Config:
        env_file = (
            ".env.local" if os.getenv("ENV") == "local"
            else ".env"  # fallback
        )

settings = Settings()

print(">>> Loaded ENV:", os.getenv("ENV"))
print("✅ Loaded DATABASE_URL:", repr(settings.DATABASE_URL))
print("✅ Loaded ELASTICSEARCH_HOSTS:", repr(settings.ELASTICSEARCH_HOSTS))
