from strands.models.openai import OpenAIModel
from strands.models.anthropic import AnthropicModel
from strands.models.gemini import GeminiModel
from strands.models.bedrock import BedrockModel

from app.config import get_settings

PROVIDER_MAP = {
    "openai": OpenAIModel,
    "anthropic": AnthropicModel,
    "gemini": GeminiModel,
    "bedrock": BedrockModel,
    "openrouter": OpenAIModel,
    "kilo": OpenAIModel,
}

def create_model(provider_id: str):
    settings = get_settings()

    if provider_id == "openai":
        return OpenAIModel(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
        )
    elif provider_id == "anthropic":
        return AnthropicModel(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
        )
    elif provider_id == "gemini":
        return GeminiModel(
            model=settings.google_model,
            api_key=settings.google_api_key,
        )
    elif provider_id == "bedrock":
        return BedrockModel(
            model=settings.bedrock_model,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            aws_region=settings.aws_region,
        )
    elif provider_id == "openrouter":
        return OpenAIModel(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    elif provider_id == "kilo":
        return OpenAIModel(
            model=settings.kilo_model,
            api_key=settings.kilo_api_key,
            base_url=settings.kilo_gateway_url,
        )
    else:
        return AnthropicModel(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
        )