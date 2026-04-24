from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from fastapi import UploadFile
from app.models.diagram import Component, DataFlow


@dataclass
class ParseResult:
    components: list[Component] = field(default_factory=list)
    flows: list[DataFlow] = field(default_factory=list)
    raw_metadata: dict = field(default_factory=dict)
    source_file: str = ""
    parser_type: str = "vision"


class BaseParser(ABC):
    @abstractmethod
    async def parse(self, file: UploadFile) -> ParseResult:
        """Parse uploaded file and return structured components and flows."""
        ...

    def _generate_id(self, prefix: str) -> str:
        import uuid
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
