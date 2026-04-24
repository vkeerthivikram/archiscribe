from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from app.ai.base import BaseAIProvider
from app.config import get_settings


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.google_api_key or "dummy")
        self.model = settings.google_model

    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        import json

        img = Image.open(BytesIO(image))
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, img],
        )
        return json.loads(response.text)

    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        contents = prompt
        config = None
        if system:
            config = types.GenerateContentConfig(
                system_instruction=system,
            )
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return response.text
