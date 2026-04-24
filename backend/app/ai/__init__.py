from app.ai.base import BaseAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.anthropic_provider import AnthropicProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.kilo_gateway_provider import KiloGatewayProvider
from app.ai.bedrock_provider import BedrockProvider
from app.ai.openrouter_provider import OpenRouterProvider
from app.config import get_settings

PROVIDER_MAP: dict[str, type[BaseAIProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "kilo": KiloGatewayProvider,
    "bedrock": BedrockProvider,
    "openrouter": OpenRouterProvider,
}


def get_provider(provider_id: str | None = None) -> BaseAIProvider:
    settings = get_settings()
    pid = provider_id or "anthropic"
    cls = PROVIDER_MAP.get(pid, AnthropicProvider)
    return cls()
