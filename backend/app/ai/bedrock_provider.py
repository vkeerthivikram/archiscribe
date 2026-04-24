import boto3
from botocore.config import Config as BotoConfig
from app.ai.base import BaseAIProvider
from app.config import get_settings


class BedrockProvider(BaseAIProvider):
    def __init__(self):
        settings = get_settings()
        self.model = settings.bedrock_model or "anthropic.claude-3-5-sonnet-20241022-20241022"
        self.client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region or "us-east-1",
            config=BotoConfig(signature_version="s3v4"),
        )

    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        import base64, json

        b64 = base64.b64encode(image).decode()
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64,
                            },
                        },
                    ],
                }
            ],
        }

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        content = response_body["content"][0]["text"]
        return json.loads(content)

    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        import json

        messages = []
        if system:
            messages.append({"role": "user", "content": f"\n\nSystem: {system}\n\n{prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": messages,
        }

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
