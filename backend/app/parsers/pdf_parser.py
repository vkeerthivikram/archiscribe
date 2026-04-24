import io
from fastapi import UploadFile
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class PDFParser(BaseParser):
    """Parser for PDF documents.

    Converts PDF pages to images using pdf2image, then processes
    each page through LLM vision analysis.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        all_components = []
        all_flows = []
        pages = self._pdf_to_images(contents)
        for page_num, page_image in enumerate(pages):
            components, flows = await self._analyze_page(
                page_image, file.filename or "pdf", page_num
            )
            all_components.extend(components)
            all_flows.extend(flows)
        return ParseResult(
            components=all_components,
            flows=all_flows,
            raw_metadata={"filename": file.filename, "pages": len(pages)},
            source_file=file.filename or "pdf",
            parser_type="vision",
        )

    def _pdf_to_images(self, pdf_bytes: bytes) -> list[bytes]:
        """Convert PDF pages to image bytes. Returns list of PNG bytes per page."""
        try:
            from pdf2image import convert_from_bytes
        except ImportError:
            return []
        pages = convert_from_bytes(pdf_bytes, dpi=150)
        images = []
        for page in pages:
            buf = io.BytesIO()
            page.save(buf, format="PNG")
            images.append(buf.getvalue())
        return images

    async def _analyze_page(
        self, image_bytes: bytes, filename: str, page_num: int
    ) -> tuple[list[Component], list[DataFlow]]:
        """Override in tests or inject AI provider."""
        return [], []
