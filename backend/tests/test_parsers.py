import pytest
import json
from fastapi import UploadFile
from starlette.datastructures import Headers
from io import BytesIO
from app.parsers.base import BaseParser, ParseResult
from app.parsers import PARSER_MAP
from app.parsers.image_parser import ImageParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.drawio_parser import DrawioParser
from app.parsers.excalidraw_parser import ExcalidrawParser
from app.parsers.visio_parser import VisioParser


class DummyUploadFile(UploadFile):
    def __init__(self, filename: str, content: bytes):
        super().__init__(
            file=BytesIO(content),
            filename=filename,
            headers=Headers(),
        )

    async def read(self, size: int | None = None) -> bytes:
        if size is None:
            return self.file.read()
        return self.file.read(size)


@pytest.mark.asyncio
async def test_image_parser_returns_parseresult():
    parser = ImageParser()
    dummy = DummyUploadFile("diagram.png", b"fake-png-bytes")
    result = await parser.parse(dummy)
    assert isinstance(result, ParseResult)
    assert result.parser_type == "vision"
    assert result.source_file == "diagram.png"


def test_parser_map_contains_all_formats():
    expected = ["png", "jpg", "jpeg", "svg", "webp", "pdf", "drawio", "xml", "excalidraw", "vsdx"]
    for ext in expected:
        assert ext in PARSER_MAP, f"Missing parser for .{ext}"


DRAWIO_XML = b"""<?xml version="1.0"?>
<mxfile>
  <diagram name="Test">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="API Gateway" style="text;html=1" parent="1" vertex="1">
          <mxGeometry x="200" y="100" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="PostgreSQL" style="shape=database" parent="1" vertex="1">
          <mxGeometry x="400" y="100" as="geometry"/>
        </mxCell>
        <mxCell id="4" source="2" target="3" edge="1"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""


EXCALIDRAW_JSON = json.dumps({
    "elements": [
        {"id": "el1", "type": "rectangle", "x": 100, "y": 200, "text": {"text": "API Service"}},
        {"id": "el2", "type": "arrow", "x": 0, "y": 0, "text": "", "startBinding": {"elementId": "el1"}, "endBinding": {"elementId": "el3"}},
        {"id": "el3", "type": "ellipse", "x": 300, "y": 200, "text": {"text": "Database"}},
    ]
}).encode()


@pytest.mark.asyncio
async def test_drawio_parser_extracts_components():
    parser = DrawioParser()
    dummy = DummyUploadFile("test.drawio", DRAWIO_XML)
    result = await parser.parse(dummy)
    assert result.parser_type == "structural"
    assert len(result.components) >= 2
    assert len(result.flows) >= 1


@pytest.mark.asyncio
async def test_excalidraw_parser_extracts_elements():
    parser = ExcalidrawParser()
    dummy = DummyUploadFile("diagram.excalidraw", EXCALIDRAW_JSON)
    result = await parser.parse(dummy)
    assert result.parser_type == "structural"
    assert len(result.components) >= 2


@pytest.mark.asyncio
async def test_visio_parser_handles_bad_zip():
    parser = VisioParser()
    dummy = DummyUploadFile("test.vsdx", b"not-a-zip")
    result = await parser.parse(dummy)
    assert result.source_file == "test.vsdx"
    assert result.parser_type == "vision"
