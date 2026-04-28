from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"
    google_api_key: str | None = None
    google_model: str = "gemini-3.1-pro-preview"
    kilo_gateway_url: str | None = None
    kilo_api_key: str | None = None
    kilo_model: str = "anthropic/claude-sonnet-4.6"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-sonnet-4-6"
    openrouter_api_key: str | None = None
    openrouter_model: str = "anthropic/claude-sonnet-4-6"
    default_provider: str = "anthropic"
    max_upload_size_mb: int = 50
    allowed_extensions: set[str] = {
        "png", "jpg", "jpeg", "svg", "webp", "pdf",
        "drawio", "xml", "excalidraw", "vsdx"
    }

    model_config = ConfigDict(env_prefix="ARCHISCRIBE_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()