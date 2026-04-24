from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    google_api_key: str | None = None
    kilo_gateway_url: str | None = None
    kilo_api_key: str | None = None
    kilo_model: str = "gpt-4o"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20241022-20241022"
    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-4o"
    max_upload_size_mb: int = 50
    allowed_extensions: set[str] = {
        "png", "jpg", "jpeg", "svg", "webp", "pdf",
        "drawio", "xml", "excalidraw", "vsdx"
    }

    class Config:
        env_prefix = "ARCHISCRIBE_"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()