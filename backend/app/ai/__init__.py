from app.ai.base import BaseAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.anthropic_provider import AnthropicProvider
from app.ai.gemini_provider import GeminiProvider
from app.config import get_settings

PROVIDER_MAP: dict[str, type[BaseAIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}


def get_provider(provider_id: str | None = None) -> BaseAIProvider:
    settings = get_settings()
    pid = provider_id or "openai"
    cls = PROVIDER_MAP.get(pid, OpenAIProvider)
    return cls()
