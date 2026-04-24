from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    max_upload_size_mb: int = 50
    allowed_extensions: set[str] = {
        "png", "jpg", "jpeg", "svg", "webp", "pdf",
        "drawio", "xml", "excalidraw", "vsdx"
    }

    class Config:
        env_prefix = "ARCHISCRIBE_"


@lru_cache
def get_settings() -> Settings:
    return Settings()