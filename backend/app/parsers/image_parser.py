from fastapi import UploadFile
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class ImageParser(BaseParser):
    """Parser for raster/vector image formats using LLM vision.

    Sends the image bytes directly to the AI provider for analysis.
    The actual AI call is injected via the analyze_image callback.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        components, flows = await self._analyze_with_vision(contents, file.filename or "image")
        return ParseResult(
            components=components,
            flows=flows,
            raw_metadata={"filename": file.filename, "size": len(contents)},
            source_file=file.filename or "image",
            parser_type="vision",
        )

    async def _analyze_with_vision(
        self, image_bytes: bytes, filename: str
    ) -> tuple[list[Component], list[DataFlow]]:
        """Override this in tests or inject AI provider."""
        return [], []
