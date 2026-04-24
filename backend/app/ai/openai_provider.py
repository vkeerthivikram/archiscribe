from openai import AsyncOpenAI
from app.ai.base import BaseAIProvider
from app.config import get_settings


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key or "dummy")

    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        import base64, json
        b64 = base64.b64encode(image).decode()
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    ],
                }
            ],
            max_tokens=4096,
        )
        content = response.choices[0].message.content
        return json.loads(content)

    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4096,
        )
        return response.choices[0].message.content
