from anthropic import AsyncAnthropic
from app.ai.base import BaseAIProvider
from app.config import get_settings


class AnthropicProvider(BaseAIProvider):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key or "dummy")
        self.model = settings.anthropic_model

    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        import base64, json
        b64 = base64.b64encode(image).decode()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/png", "data": b64},
                        },
                    ],
                }
            ],
        )
        return json.loads(response.content[0].text)

    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=messages,
        )
        return response.content[0].text
