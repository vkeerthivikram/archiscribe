import google.generativeai as genai
from app.ai.base import BaseAIProvider
from app.config import get_settings


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.google_api_key or "dummy")
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        import json
        from PIL import Image
        from io import BytesIO
        
        img = Image.open(BytesIO(image))
        response = self.model.generate_content([prompt, img])
        return json.loads(response.text)

    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self.model.generate_content(full_prompt)
        return response.text
