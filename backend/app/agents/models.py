from typing import Union

from strands.models import Model
from strands.models.openai import OpenAIModel
from strands.models.anthropic import AnthropicModel
from strands.models.gemini import GeminiModel
from strands.models.bedrock import BedrockModel

from app.config import get_settings

PROVIDER_MAP: dict[str, type[Model]] = {
    "openai": OpenAIModel,
    "anthropic": AnthropicModel,
    "gemini": GeminiModel,
    "bedrock": BedrockModel,
    "openrouter": OpenAIModel,
    "kilo": OpenAIModel,
}


def create_model(provider_id: str | None = None) -> Model:
    settings = get_settings()
    pid = provider_id or settings.default_provider or "anthropic"

    if pid == "openrouter":
        return OpenAIModel(
            model_id=settings.openrouter_model,
            client_args={
                "api_key": settings.openrouter_api_key,
                "base_url": "https://openrouter.ai/api/v1",
            },
        )
    elif pid == "kilo":
        return OpenAIModel(
            model_id=settings.kilo_model,
            client_args={
                "api_key": settings.kilo_api_key,
                "base_url": settings.kilo_gateway_url or "http://localhost:8000",
            },
        )
    elif pid in PROVIDER_MAP:
        model_cls = PROVIDER_MAP[pid]
        return _create_standard_model(pid, model_cls, settings)
    else:
        return AnthropicModel(
            model_id=settings.anthropic_model,
            client_args={"api_key": settings.anthropic_api_key},
        )


def _create_standard_model(
    pid: str, model_cls: type[Model], settings
) -> Model:
    if pid == "bedrock":
        return BedrockModel(
            model_id=settings.bedrock_model,
            region_name=settings.aws_region,
        )
    elif pid == "openai":
        return model_cls(
            model_id=settings.openai_model,
            client_args={"api_key": settings.openai_api_key},
        )
    elif pid == "anthropic":
        return model_cls(
            model_id=settings.anthropic_model,
            client_args={"api_key": settings.anthropic_api_key},
        )
    elif pid == "gemini":
        return model_cls(
            model_id=settings.google_model,
            client_args={"api_key": settings.google_api_key},
        )
    else:
        return model_cls(
            model_id=settings.anthropic_model,
            client_args={"api_key": settings.anthropic_api_key},
        )