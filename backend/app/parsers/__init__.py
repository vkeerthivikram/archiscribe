from app.parsers.base import BaseParser, ParseResult
from app.parsers.image_parser import ImageParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.drawio_parser import DrawioParser
from app.parsers.excalidraw_parser import ExcalidrawParser
from app.parsers.visio_parser import VisioParser

PARSER_MAP: dict[str, type[BaseParser]] = {
    "png": ImageParser,
    "jpg": ImageParser,
    "jpeg": ImageParser,
    "svg": ImageParser,
    "webp": ImageParser,
    "pdf": PDFParser,
    "drawio": DrawioParser,
    "xml": DrawioParser,
    "excalidraw": ExcalidrawParser,
    "vsdx": VisioParser,
}


def get_parser(filename: str) -> BaseParser:
    ext = filename.rsplit(".", 1)[-1].lower()
    parser_cls = PARSER_MAP.get(ext, ImageParser)
    return parser_cls()
