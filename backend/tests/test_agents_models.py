import pytest
from app.agents.models import create_model, PROVIDER_MAP

def test_provider_map_contains_all_providers():
    expected = ["openai", "anthropic", "gemini", "bedrock", "openrouter", "kilo"]
    for p in expected:
        assert p in PROVIDER_MAP, f"Missing provider: {p}"

def test_create_model_returns_model_instance():
    for provider_id in PROVIDER_MAP:
        model = create_model(provider_id)
        assert model is not None, f"create_model({provider_id}) returned None"