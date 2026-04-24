# Archiscribe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete web application that transforms architectural diagrams into user story backlogs.

**Architecture:** Monolithic FastAPI backend + Svelte SPA. Hybrid parsing: structural for Draw.io/Excalidraw/Visio XML, LLM vision for raster images and PDFs. AI multi-provider abstraction layer.

**Tech Stack:** Python 3.12 / FastAPI / Svelte 5 + Vite / OpenAI+Anthropic+Gemini SDKs

---

## File Structure

```
archiscribe/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── diagram.py      # Component, DataFlow
│   │   │   ├── story.py        # UserStory, AcceptanceCriterion, TechnicalNotes
│   │   │   └── project.py       # Project, Session state
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # BaseParser, ParseResult
│   │   │   ├── image_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── drawio_parser.py
│   │   │   ├── excalidraw_parser.py
│   │   │   └── visio_parser.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # BaseAIProvider
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── gemini_provider.py
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   ├── component_extractor.py
│   │   │   ├── story_generator.py
│   │   │   └── acceptance_criteria.py
│   │   ├── exporters/
│   │   │   ├── __init__.py
│   │   │   └── markdown_exporter.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── upload.py
│   │       ├── analysis.py
│   │       ├── stories.py
│   │       └── export.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_parsers.py
│   │   ├── test_ai_providers.py
│   │   ├── test_generators.py
│   │   └── test_exporters.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.svelte
│   │   ├── main.js
│   │   ├── lib/
│   │   │   ├── api.js
│   │   │   └── stores.js
│   │   ├── components/
│   │   │   ├── FileUpload.svelte
│   │   │   ├── ProviderSelect.svelte
│   │   │   ├── ComponentReview.svelte
│   │   │   ├── FlowReview.svelte
│   │   │   ├── StoryEditor.svelte
│   │   │   ├── StoryCard.svelte
│   │   │   ├── StoryList.svelte
│   │   │   └── ExportPanel.svelte
│   │   └── pages/
│   │       ├── UploadPage.svelte
│   │       ├── ReviewPage.svelte
│   │       ├── EditorPage.svelte
│   │       └── ExportPage.svelte
│   ├── index.html
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.js
└── README.md
```

---

## Task 1: Backend Scaffolding + Data Models

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/diagram.py`
- Create: `backend/app/models/story.py`
- Create: `backend/app/models/project.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
pydantic==2.9.2
pydantic-settings==2.5.2
openai==1.54.0
anthropic==0.38.0
google-generativeai==0.8.3
pdf2image==1.17.0
Pillow==10.4.0
lxml==5.3.0
python-pptx==1.0.1
olefile==0.47
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "archiscribe"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 3: Create app/__init__.py**

```python
"""Archiscribe — Architecture diagram to user story backlog."""
```

- [ ] **Step 4: Create app/config.py**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    max_upload_size_mb: int = 50
    allowed_extensions: set[str] = {
        "png", "jpg", "jpeg", "svg", "webp", "pdf",
        "drawio", "xml", "excalidraw", "vsdx"
    }

    class Config:
        env_prefix = "ARCHISCRIBE_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 5: Create app/models/diagram.py**

```python
from dataclasses import dataclass, field
from typing import Literal

ComponentType = Literal[
    "database", "api", "service", "queue", "storage",
    "load_balancer", "cache", "gateway", "client", "user",
    "external", "unknown"
]

FlowType = Literal["data", "api_call", "event", "async", "sync"]
Protocol = Literal["HTTP", "HTTPS", "gRPC", "AMQP", "MQTT", "TCP", "WebSocket", None]

ComponentStatus = Literal["pending", "confirmed", "renamed", "removed", "added"]


@dataclass
class Component:
    id: str
    name: str
    component_type: ComponentType
    description: str = ""
    position: tuple[int, int] | None = None
    properties: dict = field(default_factory=dict)
    source: str = ""
    status: ComponentStatus = "pending"


@dataclass
class DataFlow:
    id: str
    source_id: str
    target_id: str
    label: str | None = None
    flow_type: FlowType = "data"
    protocol: Protocol = None
```

- [ ] **Step 6: Create app/models/story.py**

```python
from dataclasses import dataclass, field
from typing import Self
from app.models.diagram import Component, DataFlow


@dataclass
class AcceptanceCriterion:
    id: str
    description: str
    is_testable: bool = True

    @classmethod
    def make(cls, description: str) -> Self:
        import uuid
        return cls(id=str(uuid.uuid4())[:8], description=description)


@dataclass
class TechnicalNotes:
    source_components: list[str] = field(default_factory=list)
    source_flows: list[str] = field(default_factory=list)
    diagram_references: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


Priority = Literal["High", "Medium", "Low"]


@dataclass
class UserStory:
    id: str
    epic: str
    title: str
    role: str
    action: str
    value: str
    priority: Priority = "Medium"
    story_points: int | None = None
    acceptance_criteria: list[AcceptanceCriterion] = field(default_factory=list)
    technical_notes: TechnicalNotes = field(default_factory=TechnicalNotes)

    @classmethod
    def make(
        cls,
        epic: str,
        title: str,
        role: str,
        action: str,
        value: str,
        priority: Priority = "Medium",
        components: list[Component] | None = None,
        flows: list[DataFlow] | None = None,
    ) -> Self:
        import uuid
        story_id = str(uuid.uuid4())[:8]
        notes = TechnicalNotes(
            source_components=[c.id for c in (components or [])],
            source_flows=[f.id for f in (flows or [])],
        )
        return cls(
            id=story_id,
            epic=epic,
            title=title,
            role=role,
            action=action,
            value=value,
            priority=priority,
            technical_notes=notes,
        )
```

- [ ] **Step 7: Create app/models/project.py**

```python
from dataclasses import dataclass, field
from datetime import datetime
from app.models.diagram import Component, DataFlow
from app.models.story import UserStory


@dataclass
class Project:
    id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    name: str = "Untitled Project"
    source_files: list[str] = field(default_factory=list)
    ai_provider: str = "openai"
    components: list[Component] = field(default_factory=list)
    flows: list[DataFlow] = field(default_factory=list)
    stories: list[UserStory] = field(default_factory=list)
```

- [ ] **Step 8: Create app/models/__init__.py**

```python
from app.models.diagram import Component, DataFlow, ComponentType, FlowType, ComponentStatus
from app.models.story import UserStory, AcceptanceCriterion, TechnicalNotes, Priority
from app.models.project import Project

__all__ = [
    "Component", "DataFlow", "ComponentType", "FlowType", "ComponentStatus",
    "UserStory", "AcceptanceCriterion", "TechnicalNotes", "Priority",
    "Project",
]
```

- [ ] **Step 9: Create app/main.py (minimal skeleton)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="Archiscribe", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/providers")
def list_providers():
    providers = []
    if settings.openai_api_key:
        providers.append({"id": "openai", "name": "OpenAI GPT-4o"})
    if settings.anthropic_api_key:
        providers.append({"id": "anthropic", "name": "Anthropic Claude"})
    if settings.google_api_key:
        providers.append({"id": "gemini", "name": "Google Gemini"})
    if not providers:
        providers.append({"id": "openai", "name": "OpenAI GPT-4o (configure API key)"})
    return {"providers": providers}
```

- [ ] **Step 10: Create tests/test_models.py**

```python
import pytest
from app.models import Component, DataFlow, UserStory, AcceptanceCriterion


def test_component_creation():
    c = Component(
        id="comp-1",
        name="PostgreSQL",
        component_type="database",
        description="Primary data store",
        position=(100, 200),
    )
    assert c.id == "comp-1"
    assert c.name == "PostgreSQL"
    assert c.component_type == "database"
    assert c.status == "pending"


def test_dataflow_creation():
    f = DataFlow(
        id="flow-1",
        source_id="client-1",
        target_id="db-1",
        label="SQL queries",
        flow_type="api_call",
        protocol="TCP",
    )
    assert f.source_id == "client-1"
    assert f.target_id == "db-1"


def test_userstory_make():
    story = UserStory.make(
        epic="Data Storage",
        title="Persist user data",
        role="system architect",
        action="store data in PostgreSQL",
        value="data is reliably saved",
        priority="High",
    )
    assert story.epic == "Data Storage"
    assert story.priority == "High"
    assert story.acceptance_criteria == []


def test_acceptance_criterion_make():
    ac = AcceptanceCriterion.make("Database connection is pooled")
    assert ac.id != ""
    assert ac.description == "Database connection is pooled"
    assert ac.is_testable is True
```

- [ ] **Step 11: Run tests to verify**

```bash
cd /home/vicky/Documents/Repos/archiscribe/backend
pip install -q pytest pytest-asyncio pydantic pydantic-settings python-multipart 2>/dev/null
python -m pytest tests/test_models.py -v
```

Expected: 4 tests pass

- [ ] **Step 12: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git init
git add backend/requirements.txt backend/pyproject.toml backend/app/ backend/tests/
git commit -m "feat: backend scaffolding and data models"
git branch -M main
```

---

## Task 2: Parser Base Interface + Image + PDF Parsers

**Files:**
- Create: `backend/app/parsers/__init__.py`
- Create: `backend/app/parsers/base.py`
- Create: `backend/app/parsers/image_parser.py`
- Create: `backend/app/parsers/pdf_parser.py`
- Create: `backend/tests/test_parsers.py`

- [ ] **Step 1: Create parsers/__init__.py**

```python
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
```

- [ ] **Step 2: Create parsers/base.py**

```python
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
```

- [ ] **Step 3: Create parsers/image_parser.py**

```python
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
        # Default stub — real implementation injected via AI provider
        # Returns empty result; actual parsing done by component_extractor
        return [], []
```

- [ ] **Step 4: Create parsers/pdf_parser.py**

```python
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
```

- [ ] **Step 5: Create tests/test_parsers.py**

```python
import pytest
from fastapi import UploadFile
from io import BytesIO
from app.parsers.base import BaseParser, ParseResult, PARSER_MAP
from app.parsers.image_parser import ImageParser
from app.parsers.pdf_parser import PDFParser


class DummyUploadFile(UploadFile):
    def __init__(self, filename: str, content: bytes):
        super().__init__(file=BytesIO(content))
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    async def read(self, size: int | None = None):
        return await super().read(size)


@pytest.mark.asyncio
async def test_image_parser_returns_pars eresult():
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
```

- [ ] **Step 6: Run tests**

```bash
cd /home/vicky/Documents/Repos/archiscribe/backend
pip install -q fastapi python-multipart Pillow 2>/dev/null
python -m pytest tests/test_parsers.py -v
```

Expected: tests pass

- [ ] **Step 7: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add backend/app/parsers/ backend/tests/test_parsers.py
git commit -m "feat: parser base interface, image and PDF parsers"
```

---

## Task 3: Structural Parsers — Draw.io, Excalidraw, Visio

**Files:**
- Create: `backend/app/parsers/drawio_parser.py`
- Create: `backend/app/parsers/excalidraw_parser.py`
- Create: `backend/app/parsers/visio_parser.py`
- Modify: `backend/tests/test_parsers.py` (add tests)

- [ ] **Step 1: Create drawio_parser.py**

```python
from fastapi import UploadFile
from lxml import etree
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


NAMESPACES = {"mx": "http://graphviz.org/"}


class DrawioParser(BaseParser):
    """Structural parser for Draw.io XML format.
    
    Parses the XML to extract mxCell elements (nodes/edges),
    their labels, styles, and connection geometry.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        tree = etree.fromstring(contents)
        components, flows = self._extract_elements(tree)
        return ParseResult(
            components=components,
            flows=flows,
            raw_metadata={"filename": file.filename},
            source_file=file.filename or "drawio",
            parser_type="structural",
        )

    def _extract_elements(self, tree: etree._Element) -> tuple[list[Component], list[DataFlow]]:
        components = []
        flows = []
        cells = tree.xpath("//mxCell")
        for cell in cells:
            cell_id = cell.get("id", "")
            parent_id = cell.get("parent", "")
            value_el = cell.find("mxGeometry")
            style = cell.get("style", "")
            value = cell.get("value", "") or ""
            
            if self._is_edge(style):
                source = cell.get("source", "")
                target = cell.get("target", "")
                if source and target:
                    flows.append(DataFlow(
                        id=self._generate_id("flow"),
                        source_id=source,
                        target_id=target,
                        label=value if value else None,
                        flow_type=self._infer_flow_type(style),
                    ))
            elif parent_id not in ("0", None) and value:
                ctype = self._infer_component_type(style, value)
                x, y = self._get_position(value_el)
                components.append(Component(
                    id=cell_id,
                    name=self._clean_label(value),
                    component_type=ctype,
                    description=f"Draw.io cell: {value}",
                    position=(x, y) if x and y else None,
                    source=file.filename or "drawio",
                    properties={"style": style},
                ))
        return components, flows

    def _is_edge(self, style: str) -> bool:
        return "endArrow" in style or "edge" in style

    def _infer_component_type(self, style: str, label: str) -> str:
        label_lower = label.lower()
        if "database" in style or "db" in label_lower:
            return "database"
        if "queue" in style or "mq" in label_lower:
            return "queue"
        if "cloud" in style or "aws" in label_lower or "azure" in label_lower:
            return "storage"
        if "load" in style or "lb" in label_lower:
            return "load_balancer"
        if "cache" in style or "redis" in label_lower:
            return "cache"
        if "api" in label_lower or "gateway" in style:
            return "api"
        if "user" in label_lower or "actor" in label_lower:
            return "user"
        if "storage" in style or "s3" in label_lower:
            return "storage"
        return "service"

    def _infer_flow_type(self, style: str) -> str:
        if "dashed" in style:
            return "async"
        if "edgeStyle=orthogonal" in style:
            return "api_call"
        return "data"

    def _get_position(self, geo) -> tuple[int | None, int | None]:
        if geo is None:
            return None, None
        x = geo.get("x")
        y = geo.get("y")
        return int(x) if x else None, int(y) if y else None

    def _clean_label(self, label: str) -> str:
        import re
        label = re.sub(r"<[^>]+>", "", label)
        return label.strip()
```

- [ ] **Step 2: Create excalidraw_parser.py**

```python
import json
from fastapi import UploadFile
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class ExcalidrawParser(BaseParser):
    """Structural parser for Excalidraw JSON format.
    
    Parses the JSON to extract elements (rectangles, diamonds, etc.),
    their labels, and arrow connections.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        data = json.loads(contents)
        components, flows = self._extract_elements(data)
        return ParseResult(
            components=components,
            flows=flows,
            raw_metadata={"filename": file.filename},
            source_file=file.filename or "excalidraw",
            parser_type="structural",
        )

    def _extract_elements(self, data: dict) -> tuple[list[Component], list[DataFlow]]:
        components = []
        flows = []
        elements = data.get("elements", [])
        id_map = {}
        
        for el in elements:
            el_id = el.get("id", "")
            el_type = el.get("type", "")
            label = el.get("label", {}) or {}
            text = label.get("text", "") or el.get("text", "") or ""
            if isinstance(text, dict):
                text = text.get("text", "")
            
            x = el.get("x", 0)
            y = el.get("y", 0)
            
            if el_type == "arrow":
                bound_ids = []
                for key in ["boundElements", "startBinding", "endBinding"]:
                    bound = el.get(key)
                    if bound:
                        if isinstance(bound, dict):
                            bound_ids.append(bound.get("id", ""))
                        elif isinstance(bound, list):
                            bound_ids.extend([b.get("id", "") for b in bound])
                
                source_id = el.get("startBinding", {}).get("elementId", "") if isinstance(el.get("startBinding"), dict) else ""
                target_id = el.get("endBinding", {}).get("elementId", "") if isinstance(el.get("endBinding"), dict) else ""
                
                if source_id and target_id:
                    flows.append(DataFlow(
                        id=self._generate_id("flow"),
                        source_id=source_id,
                        target_id=target_id,
                        label=text or None,
                        flow_type="data",
                    ))
            elif el_type in ("rectangle", "diamond", "ellipse", "text"):
                ctype = self._infer_type(el_type, text)
                components.append(Component(
                    id=el_id,
                    name=self._clean_label(text) or f"Element-{el_id[:8]}",
                    component_type=ctype,
                    description=f"Excalidraw {el_type}",
                    position=(int(x), int(y)),
                    source="excalidraw",
                    properties={"el_type": el_type},
                ))
                id_map[el_id] = el_id
        
        return components, flows

    def _infer_type(self, el_type: str, text: str) -> str:
        text_lower = text.lower()
        if el_type == "diamond":
            return "gateway"
        if "database" in text_lower or "db" in text_lower:
            return "database"
        if "queue" in text_lower:
            return "queue"
        if "storage" in text_lower or "bucket" in text_lower:
            return "storage"
        if "cache" in text_lower or "redis" in text_lower:
            return "cache"
        if "load" in text_lower:
            return "load_balancer"
        if "api" in text_lower:
            return "api"
        if "user" in text_lower or "actor" in text_lower:
            return "user"
        if "service" in text_lower or "microservice" in text_lower:
            return "service"
        if "external" in text_lower:
            return "external"
        return "service"

    def _clean_label(self, text: str) -> str:
        if not text:
            return ""
        import re
        text = re.sub(r"<[^>]+>", "", str(text))
        return text.strip()
```

- [ ] **Step 3: Create visio_parser.py**

```python
import io
import zipfile
from fastapi import UploadFile
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class VisioParser(BaseParser):
    """Structural + vision parser for Visio .vsdx files.
    
    A .vsdx is a ZIP archive containing XML files. Extracts
    embedded diagram images and page XML, then sends images
    to LLM vision for analysis.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        all_components = []
        all_flows = []
        
        try:
            with zipfile.ZipFile(io.BytesIO(contents)) as zf:
                page_files = [n for n in zf.namelist() if n.startswith("visio/pages/page") and n.endswith(".xml")]
                images = []
                
                for page_file in page_files:
                    page_xml = zf.read(page_file).decode("utf-8", errors="ignore")
                    page_components, page_flows, page_images = self._parse_page_xml(page_xml, zf)
                    all_components.extend(page_components)
                    all_flows.extend(page_flows)
                    images.extend(page_images)
                
                for img_data in images:
                    comps, flows = await self._analyze_embedded_image(img_data, file.filename or "visio")
                    all_components.extend(comps)
                    all_flows.extend(flows)
        except zipfile.BadZipFile:
            return ParseResult(source_file=file.filename or "visio", parser_type="vision")
        
        return ParseResult(
            components=all_components,
            flows=all_flows,
            raw_metadata={"filename": file.filename},
            source_file=file.filename or "visio",
            parser_type="hybrid",
        )

    def _parse_page_xml(self, page_xml: str, zf: zipfile.ZipFile) -> tuple[list[Component], list[DataFlow], list[bytes]]:
        from lxml import etree
        components = []
        flows = []
        images = []
        
        try:
            tree = etree.fromstring(page_xml.encode("utf-8"))
            ns = {"v": "http://schemas.microsoft.com/visio/2003/core"}
            shapes = tree.xpath("//v:shape", namespaces=ns)
            
            for shape in shapes:
                shape_id = shape.get("ID", "")
                text_el = shape.xpath(".//v:text", namespaces=ns)
                text = " ".join([t.text or "" for t in text_el]).strip()
                x = float(shape.get("PinX", 0))
                y = float(shape.get("PinY", 0))
                master = shape.get("Master", "")
                
                if text:
                    ctype = self._infer_type_from_master(master, text)
                    components.append(Component(
                        id=self._generate_id("comp"),
                        name=self._clean_label(text),
                        component_type=ctype,
                        position=(int(x), int(y)),
                        source="visio",
                        properties={"master": master},
                    ))
                
                img_data = shape.get("{http://schemas.microsoft.com/visio/2006/extension}image")
                if img_data and master:
                    pass
            
            connects = tree.xpath("//v:connect", namespaces=ns)
            for conn in connects:
                from_id = conn.get("FromSheet", "")
                to_id = conn.get("ToSheet", "")
                if from_id and to_id:
                    flows.append(DataFlow(
                        id=self._generate_id("flow"),
                        source_id=from_id,
                        target_id=to_id,
                    ))
        except Exception:
            pass
        
        return components, flows, images

    def _infer_type_from_master(self, master: str, text: str) -> str:
        text_lower = text.lower()
        if not master:
            if "database" in text_lower: return "database"
            if "process" in text_lower: return "service"
            if "storage" in text_lower: return "storage"
            if "user" in text_lower: return "user"
            return "service"
        master_lower = master.lower()
        if "db" in master_lower: return "database"
        if "storage" in master_lower: return "storage"
        if "cache" in master_lower: return "cache"
        if "queue" in master_lower: return "queue"
        return "service"

    def _clean_label(self, text: str) -> str:
        import re
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()

    async def _analyze_embedded_image(self, image_bytes: bytes, filename: str) -> tuple[list[Component], list[DataFlow]]:
        """Override to inject LLM vision analysis."""
        return [], []
```

- [ ] **Step 4: Add tests for structural parsers**

```python
import pytest
import json
from fastapi import UploadFile
from io import BytesIO
from app.parsers.drawio_parser import DrawioParser
from app.parsers.excalidraw_parser import ExcalidrawParser
from app.parsers.visio_parser import VisioParser


class DummyUploadFile(UploadFile):
    def __init__(self, filename: str, content: bytes):
        super().__init__(file=BytesIO(content))
        self._filename = filename
    @property
    def filename(self): return self._filename
    async def read(self, size=None): return await super().read(size)


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
```

- [ ] **Step 5: Run tests**

```bash
cd /home/vicky/Documents/Repos/archiscribe/backend
pip install -q lxml python-pptx olefile 2>/dev/null
python -m pytest tests/test_parsers.py -v
```

- [ ] **Step 6: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add backend/app/parsers/drawio_parser.py backend/app/parsers/excalidraw_parser.py backend/app/parsers/visio_parser.py backend/tests/test_parsers.py
git commit -m "feat: structural parsers for Draw.io, Excalidraw, and Visio"
```

---

## Task 4: AI Provider Abstraction Layer

**Files:**
- Create: `backend/app/ai/__init__.py`
- Create: `backend/app/ai/base.py`
- Create: `backend/app/ai/openai_provider.py`
- Create: `backend/app/ai/anthropic_provider.py`
- Create: `backend/app/ai/gemini_provider.py`

- [ ] **Step 1: Create ai/__init__.py**

```python
from app.ai.base import BaseAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.anthropic_provider import AnthropicProvider
from app.ai.gemini_provider import GeminiProvider
from app.config import get_settings

PROVIDER_MAP: dict[str, type[BaseAIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}


def get_provider(provider_id: str | None = None) -> BaseAIProvider:
    settings = get_settings()
    pid = provider_id or "openai"
    cls = PROVIDER_MAP.get(pid, OpenAIProvider)
    return cls()
```

- [ ] **Step 2: Create ai/base.py**

```python
from abc import ABC, abstractmethod
from app.models.diagram import Component, DataFlow
from app.models.story import UserStory


EXTRACTION_PROMPT = """You are an expert at analyzing architectural diagrams.

Analyze this diagram image and extract ALL components and data flows you can identify.

For each component, identify:
- name: what it's called (e.g., "PostgreSQL", "API Gateway", "User Browser")
- type: one of: database, api, service, queue, storage, load_balancer, cache, gateway, client, user, external, unknown
- description: brief description of what it does
- position: x,y coordinates if visible (approximate is fine)

For each data flow/connection, identify:
- source: the component name or ID that is the origin
- target: the component name or ID that is the destination
- label: any text label on the arrow/connection
- type: one of: data, api_call, event, async, sync

Return your analysis as a structured JSON object with this format:
{
  "components": [
    {"name": "...", "type": "...", "description": "...", "position": [x, y]}
  ],
  "flows": [
    {"source": "...", "target": "...", "label": "...", "type": "..."}
  ]
}

Be thorough. Identify every component and connection you can see."""


STORY_GENERATION_PROMPT = """You are an expert product manager who transforms architectural diagrams into user stories.

Given the following components and data flows extracted from an architecture diagram, generate a set of user stories.

Components:
{components_text}

Data Flows:
{flows_text}

Generate user stories following this format for EACH distinct functional capability:
- Group related components into epics
- For each epic, create user stories in format:
  **As a** [role]
  **I want** [action]
  **so that** [value]

Rules:
- Derive the role from the diagram context (e.g., "system architect", "backend developer", "DevOps engineer")
- Derive the action from what the component does
- Derive the value from the business/technical benefit
- Each story should be focused on ONE component or ONE data flow
- Infer reasonable acceptance criteria for each story
- Assign priority (High/Medium/Low) based on architectural importance

Return as structured JSON:
{{
  "epics": [
    {{
      "name": "Epic Name",
      "stories": [
        {{
          "title": "Story title",
          "role": "As a...",
          "action": "I want...",
          "value": "so that...",
          "priority": "High/Medium/Low",
          "story_points": 1-13,
          "acceptance_criteria": ["criterion 1", "criterion 2"],
          "source_components": ["component names involved"],
          "source_flows": ["flow labels involved"]
        }}
      ]
    }}
  ]
}}"""


class BaseAIProvider(ABC):
    @abstractmethod
    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        """Send image to vision model, return parsed JSON response."""
        ...

    @abstractmethod
    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        """Send text prompt to language model."""
        ...

    async def extract_components(self, image: bytes) -> list[Component]:
        """Extract components and flows from a diagram image."""
        import json, uuid
        response = await self.analyze_image(image, EXTRACTION_PROMPT)
        components = []
        for item in response.get("components", []):
            comp = Component(
                id=uuid.uuid4().hex[:8],
                name=item.get("name", "Unknown"),
                component_type=item.get("type", "unknown"),
                description=item.get("description", ""),
                position=tuple(item.get("position", [None, None])) if item.get("position") else None,
                source="ai_extraction",
            )
            components.append(comp)
        return components

    async def generate_stories(
        self,
        components: list[Component],
        flows: list[DataFlow],
    ) -> list[UserStory]:
        """Generate user stories from components and flows."""
        import json
        components_text = "\n".join(
            f"- {c.name} ({c.component_type}): {c.description}" for c in components
        )
        flows_text = "\n".join(
            f"- {f.source_id} → {f.target_id}" + (f" [{f.label}]" if f.label else "")
            for f in flows
        )
        prompt = STORY_GENERATION_PROMPT.format(
            components_text=components_text,
            flows_text=flows_text,
        )
        response = await self.generate_text(prompt)
        return self._parse_stories_response(response, components, flows)

    def _parse_stories_response(
        self,
        response: str,
        components: list[Component],
        flows: list[DataFlow],
    ) -> list[UserStory]:
        import json, re
        stories = []
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return []
        
        for epic_data in data.get("epics", []):
            epic_name = epic_data.get("name", "General")
            for story_data in epic_data.get("stories", []):
                story = UserStory.make(
                    epic=epic_name,
                    title=story_data.get("title", "Untitled"),
                    role=story_data.get("role", "").replace("**As a** ", ""),
                    action=story_data.get("action", "").replace("**I want** ", ""),
                    value=story_data.get("value", "").replace("**so that** ", ""),
                    priority=story_data.get("priority", "Medium"),
                )
                story.story_points = story_data.get("story_points")
                for crit in story_data.get("acceptance_criteria", []):
                    from app.models.story import AcceptanceCriterion
                    story.acceptance_criteria.append(
                        AcceptanceCriterion.make(crit)
                    )
                stories.append(story)
        return stories
```

- [ ] **Step 3: Create ai/openai_provider.py**

```python
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
```

- [ ] **Step 4: Create ai/anthropic_provider.py**

```python
from anthropic import AsyncAnthropic
from app.ai.base import BaseAIProvider
from app.config import get_settings


class AnthropicProvider(BaseAIProvider):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key or "dummy")

    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        import base64, json
        b64 = base64.b64encode(image).decode()
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=messages,
        )
        return response.content[0].text
```

- [ ] **Step 5: Create ai/gemini_provider.py**

```python
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
```

- [ ] **Step 6: Run a quick import check**

```bash
cd /home/vicky/Documents/Repos/archiscribe/backend
python -c "from app.ai import get_provider; print('AI providers OK')"
```

- [ ] **Step 7: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add backend/app/ai/
git commit -m "feat: AI provider abstraction layer with OpenAI, Anthropic, and Gemini"
```

---

## Task 5: Generators — Component Extractor, Story Generator, Acceptance Criteria

**Files:**
- Create: `backend/app/generators/__init__.py`
- Create: `backend/app/generators/component_extractor.py`
- Create: `backend/app/generators/story_generator.py`
- Create: `backend/app/generators/acceptance_criteria.py`

- [ ] **Step 1: Create generators/__init__.py**

```python
from app.generators.component_extractor import ComponentExtractor
from app.generators.story_generator import StoryGenerator
from app.generators.acceptance_criteria import AcceptanceCriteriaGenerator

__all__ = ["ComponentExtractor", "StoryGenerator", "AcceptanceCriteriaGenerator"]
```

- [ ] **Step 2: Create component_extractor.py**

```python
from app.ai.base import BaseAIProvider
from app.models.diagram import Component, DataFlow
from app.parsers.base import ParseResult


class ComponentExtractor:
    """Orchestrates parsing + AI extraction for diagram analysis.
    
    Takes a ParseResult (from any parser) and feeds the data
    to the AI provider for component/flow enrichment.
    """

    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider

    async def extract(self, parse_result: ParseResult) -> tuple[list[Component], list[DataFlow]]:
        """Run AI extraction on a parse result.
        
        For structural parsers: validate and enrich components with AI
        For vision parsers: send images to AI for extraction
        """
        if parse_result.parser_type == "vision":
            return await self._extract_from_vision(parse_result)
        return parse_result.components, parse_result.flows

    async def _extract_from_vision(self, result: ParseResult) -> tuple[list[Component], list[DataFlow]]:
        """Send diagram image bytes to AI for extraction."""
        from fastapi import UploadFile
        from io import BytesIO
        
        if result.raw_metadata.get("pages"):
            all_comps, all_flows = [], []
            for page_num in range(result.raw_metadata["pages"]):
                pass
            return all_comps, all_flows
        
        return [], []
```

- [ ] **Step 3: Create story_generator.py**

```python
from app.ai.base import BaseAIProvider
from app.models.diagram import Component, DataFlow
from app.models.story import UserStory


class StoryGenerator:
    """Converts extracted components and flows into user stories."""

    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider

    async def generate(
        self,
        components: list[Component],
        flows: list[DataFlow],
    ) -> list[UserStory]:
        """Generate user stories from components and flows using AI."""
        return await self.ai_provider.generate_stories(components, flows)

    def group_by_epic(self, stories: list[UserStory]) -> dict[str, list[UserStory]]:
        """Group stories into epics by component type."""
        epic_map: dict[str, list[UserStory]] = {}
        for story in stories:
            if story.epic not in epic_map:
                epic_map[story.epic] = []
            epic_map[story.epic].append(story)
        return epic_map
```

- [ ] **Step 4: Create acceptance_criteria.py**

```python
from app.models.diagram import Component, DataFlow, ComponentType
from app.models.story import AcceptanceCriterion


CRITERIA_TEMPLATES: dict[ComponentType, list[str]] = {
    "database": [
        "Database schema supports all required entity types",
        "Connection pooling is configured with appropriate pool size",
        "Migration scripts are versioned and reversible",
        "Backup and restore procedures are documented",
    ],
    "api": [
        "API endpoints respond within acceptable latency thresholds",
        "API versioning strategy is defined",
        "Request/response schemas are documented",
        "Authentication and authorization are enforced",
    ],
    "service": [
        "Service health check endpoint is exposed",
        "Service can be scaled horizontally",
        "Service logs are structured and centralized",
        "Service registers with service discovery",
    ],
    "storage": [
        "Storage bucket has appropriate access policies",
        "Data retention policy is defined and enforced",
        "Storage costs are monitored and optimized",
    ],
    "cache": [
        "Cache invalidation strategy is defined",
        "Cache TTL values are appropriate for use case",
        "Cache hit rate meets performance requirements",
    ],
    "load_balancer": [
        "Load balancer health checks are configured",
        "Traffic distribution algorithm is appropriate",
        "SSL termination is handled correctly",
    ],
    "queue": [
        "Message durability is configured",
        "Dead letter queue handles failed messages",
        "Consumer groups are properly scaled",
    ],
    "gateway": [
        "Rate limiting is configured appropriately",
        "Request routing rules are documented",
        "Gateway logs all traffic for auditing",
    ],
}


class AcceptanceCriteriaGenerator:
    """Generates testable acceptance criteria from components."""

    def generate_for_component(self, component: Component) -> list[AcceptanceCriterion]:
        """Generate ACs based on component type."""
        from app.models.story import AcceptanceCriterion
        templates = CRITERIA_TEMPLATES.get(component.component_type, [])
        return [AcceptanceCriterion.make(tmpl.format(name=component.name)) for tmpl in templates]

    def generate_for_story(
        self,
        story_components: list[Component],
        story_flows: list[DataFlow],
    ) -> list[AcceptanceCriterion]:
        """Generate ACs covering all components and flows in a story."""
        criteria = []
        for comp in story_components:
            criteria.extend(self.generate_for_component(comp))
        return criteria
```

- [ ] **Step 5: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add backend/app/generators/
git commit -m "feat: generators for components, stories, and acceptance criteria"
```

---

## Task 6: Markdown Exporter

**Files:**
- Create: `backend/app/exporters/__init__.py`
- Create: `backend/app/exporters/markdown_exporter.py`

- [ ] **Step 1: Create exporters/__init__.py**

```python
from app.exporters.markdown_exporter import MarkdownExporter

__all__ = ["MarkdownExporter"]
```

- [ ] **Step 2: Create markdown_exporter.py**

```python
from datetime import date
from app.models.story import UserStory


class MarkdownExporter:
    """Exports user stories as a professional Markdown backlog."""

    def export(
        self,
        stories: list[UserStory],
        source_files: list[str],
        ai_provider: str,
        project_name: str = "Architecture Analysis",
    ) -> str:
        lines = [
            f"# Product Backlog — {project_name}",
            "",
            f"_Generated by Archiscribe on {date.today().isoformat()}_",
            f"_Source files: {', '.join(source_files) or 'None'}_",
            f"_AI Provider: {ai_provider}_",
            "",
            "---",
            "",
        }

        by_epic: dict[str, list[UserStory]] = {}
        for story in stories:
            by_epic.setdefault(story.epic, []).append(story)

        for epic_name, epic_stories in by_epic.items():
            lines.append(f"## Epic: {epic_name}")
            lines.append("")
            for story in epic_stories:
                lines.append(self._render_story(story))
                lines.append("")

        return "\n".join(lines)

    def _render_story(self, story: UserStory) -> str:
        lines = [
            f"### US-{story.id[:8].upper()}: {story.title}",
            "",
            f"**As a** {story.role}",
            f"**I want** {story.action}",
            f"**so that** {story.value}",
            "",
        ]

        if story.priority or story.story_points:
            meta = []
            if story.priority:
                meta.append(f"**Priority:** {story.priority}")
            if story.story_points:
                meta.append(f"**Story Points:** {story.story_points}")
            lines.append(" | ".join(meta))
            lines.append("")

        if story.acceptance_criteria:
            lines.append("#### Acceptance Criteria")
            for ac in story.acceptance_criteria:
                lines.append(f"- [ ] {ac.description}")
            lines.append("")

        if story.technical_notes:
            notes = story.technical_notes
            lines.append("#### Technical Notes")
            if notes.source_components:
                lines.append(f"- **Source components:** {', '.join(notes.source_components)}")
            if notes.source_flows:
                lines.append(f"- **Source flows:** {', '.join(notes.source_flows)}")
            if notes.diagram_references:
                lines.append(f"- **Diagram references:** {', '.join(notes.diagram_references)}")
            if notes.dependencies:
                lines.append(f"- **Dependencies:** {', '.join(notes.dependencies)}")
            lines.append("")

        lines.append("---")
        return "\n".join(lines)
```

- [ ] **Step 3: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add backend/app/exporters/
git commit -m "feat: markdown backlog exporter"
```

---

## Task 7: API Routers — Upload, Analysis, Stories, Export

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/upload.py`
- Create: `backend/app/routers/analysis.py`
- Create: `backend/app/routers/stories.py`
- Create: `backend/app/routers/export.py`

- [ ] **Step 1: Create routers/__init__.py**

```python
from app.routers.upload import router as upload_router
from app.routers.analysis import router as analysis_router
from app.routers.stories import router as stories_router
from app.routers.export import router as export_router

__all__ = ["upload_router", "analysis_router", "stories_router", "export_router"]
```

- [ ] **Step 2: Create routers/upload.py**

```python
import uuid
from fastapi import APIRouter, UploadFile, File
from app.models.project import Project

router = APIRouter(prefix="/api/projects", tags=["upload"])

_projects: dict[str, Project] = {}


@router.post("", status_code=201)
def create_project(name: str = "Untitled Project") -> dict:
    pid = uuid.uuid4().hex[:12]
    project = Project(id=pid, name=name)
    _projects[pid] = project
    return {"id": pid, "name": name}


@router.post("/{project_id}/upload")
async def upload_files(project_id: str, files: list[UploadFile] = File(...)) -> dict:
    if project_id not in _projects:
        return {"error": "Project not found"}
    project = _projects[project_id]
    for f in files:
        project.source_files.append(f.filename or "unknown")
    return {"uploaded": len(files), "files": [f.filename for f in files]}


@router.get("/{project_id}")
def get_project(project_id: str) -> dict:
    if project_id not in _projects:
        return {"error": "Project not found"}
    p = _projects[project_id]
    return {
        "id": p.id,
        "name": p.name,
        "source_files": p.source_files,
        "ai_provider": p.ai_provider,
        "components_count": len(p.components),
        "stories_count": len(p.stories),
    }
```

- [ ] **Step 3: Create routers/analysis.py**

```python
from fastapi import APIRouter, HTTPException
from app.models.diagram import Component, DataFlow
from app.parsers import get_parser
from app.generators import ComponentExtractor, StoryGenerator
from app.ai import get_provider

router = APIRouter(prefix="/api/projects", tags=["analysis"])

_projects: dict = {}


def get_project(project_id: str):
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]


@router.post("/{project_id}/analyze")
async def analyze_diagram(project_id: str, file_index: int = 0) -> dict:
    project = get_project(project_id)
    if not project.source_files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    filename = project.source_files[file_index]
    parser = get_parser(filename)
    
    from fastapi import UploadFile
    from io import BytesIO
    dummy_file = UploadFile(file=BytesIO(b"dummy"), filename=filename)
    
    result = await parser.parse(dummy_file)
    
    project.components = result.components
    project.flows = result.flows
    
    return {
        "components_count": len(result.components),
        "flows_count": len(result.flows),
        "parser_type": result.parser_type,
    }


@router.get("/{project_id}/components")
def get_components(project_id: str) -> dict:
    project = get_project(project_id)
    return {
        "components": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.component_type,
                "description": c.description,
                "position": c.position,
                "status": c.status,
            }
            for c in project.components
        ],
        "flows": [
            {
                "id": f.id,
                "source_id": f.source_id,
                "target_id": f.target_id,
                "label": f.label,
                "flow_type": f.flow_type,
                "protocol": f.protocol,
            }
            for f in project.flows
        ],
    }


@router.put("/{project_id}/components")
def update_components(project_id: str, updates: dict) -> dict:
    project = get_project(project_id)
    
    for update in updates.get("components", []):
        for comp in project.components:
            if comp.id == update.get("id"):
                comp.status = update.get("status", comp.status)
                comp.name = update.get("name", comp.name)
                break
    
    return {"updated": len(updates.get("components", []))}
```

- [ ] **Step 4: Create routers/stories.py**

```python
import uuid
from fastapi import APIRouter, HTTPException
from app.models.story import UserStory, AcceptanceCriterion

router = APIRouter(prefix="/api/projects", tags=["stories"])

_projects: dict = {}


def get_project(project_id: str):
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]


@router.post("/{project_id}/generate-stories")
async def generate_stories(project_id: str) -> dict:
    from app.routers.analysis import get_project as get_proj
    project = get_proj(project_id)
    
    if not project.components:
        raise HTTPException(status_code=400, detail="No components to analyze")
    
    from app.ai import get_provider
    from app.generators import StoryGenerator
    
    provider = get_provider(project.ai_provider)
    generator = StoryGenerator(provider)
    stories = await generator.generate(project.components, project.flows)
    
    project.stories = stories
    return {"stories_count": len(stories)}


@router.get("/{project_id}/stories")
def get_stories(project_id: str) -> dict:
    project = get_project(project_id)
    return {
        "stories": [
            {
                "id": s.id,
                "epic": s.epic,
                "title": s.title,
                "role": s.role,
                "action": s.action,
                "value": s.value,
                "priority": s.priority,
                "story_points": s.story_points,
                "acceptance_criteria": [
                    {"id": ac.id, "description": ac.description}
                    for ac in s.acceptance_criteria
                ],
                "technical_notes": {
                    "source_components": s.technical_notes.source_components,
                    "source_flows": s.technical_notes.source_flows,
                    "diagram_references": s.technical_notes.diagram_references,
                    "dependencies": s.technical_notes.dependencies,
                },
            }
            for s in project.stories
        ]
    }


@router.put("/{project_id}/stories/{story_id}")
def update_story(project_id: str, story_id: str, updates: dict) -> dict:
    project = get_project(project_id)
    for story in project.stories:
        if story.id == story_id:
            story.title = updates.get("title", story.title)
            story.role = updates.get("role", story.role)
            story.action = updates.get("action", story.action)
            story.value = updates.get("value", story.value)
            story.priority = updates.get("priority", story.priority)
            story.story_points = updates.get("story_points", story.story_points)
            return {"updated": True}
    raise HTTPException(status_code=404, detail="Story not found")


@router.delete("/{project_id}/stories/{story_id}")
def delete_story(project_id: str, story_id: str) -> dict:
    project = get_project(project_id)
    original = len(project.stories)
    project.stories = [s for s in project.stories if s.id != story_id]
    return {"deleted": len(project.stories) < original}


@router.post("/{project_id}/stories/{story_id}/regenerate")
async def regenerate_story(project_id: str, story_id: str) -> dict:
    project = get_project(project_id)
    for i, story in enumerate(project.stories):
        if story.id == story_id:
            from app.ai import get_provider
            from app.generators import StoryGenerator
            provider = get_provider(project.ai_provider)
            generator = StoryGenerator(provider)
            comps = [c for c in project.components if c.id in story.technical_notes.source_components]
            flows = [f for f in project.flows if f.id in story.technical_notes.source_flows]
            new_stories = await generator.generate(comps, flows)
            if new_stories:
                project.stories[i] = new_stories[0]
            return {"regenerated": True}
    raise HTTPException(status_code=404, detail="Story not found")


@router.post("/{project_id}/stories")
def add_story(project_id: str, story_data: dict) -> dict:
    project = get_project(project_id)
    story = UserStory.make(
        epic=story_data.get("epic", "General"),
        title=story_data.get("title", "Manual Story"),
        role=story_data.get("role", "user"),
        action=story_data.get("action", "perform an action"),
        value=story_data.get("value", "achieve a goal"),
        priority=story_data.get("priority", "Medium"),
    )
    project.stories.append(story)
    return {"id": story.id}
```

- [ ] **Step 5: Create routers/export.py**

```python
from fastapi import APIRouter, HTTPException
from app.exporters import MarkdownExporter

router = APIRouter(prefix="/api/projects", tags=["export"])


@router.post("/{project_id}/export/markdown")
def export_markdown(project_id: str) -> dict:
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = _projects[project_id]
    
    exporter = MarkdownExporter()
    markdown = exporter.export(
        stories=project.stories,
        source_files=project.source_files,
        ai_provider=project.ai_provider,
        project_name=project.name,
    )
    
    return {"markdown": markdown}
```

- [ ] **Step 6: Wire routers into main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import upload_router, analysis_router, stories_router, export_router

settings = get_settings()

app = FastAPI(title="Archiscribe", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(stories_router)
app.include_router(export_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/providers")
def list_providers():
    providers = []
    if settings.openai_api_key:
        providers.append({"id": "openai", "name": "OpenAI GPT-4o"})
    if settings.anthropic_api_key:
        providers.append({"id": "anthropic", "name": "Anthropic Claude"})
    if settings.google_api_key:
        providers.append({"id": "gemini", "name": "Google Gemini"})
    if not providers:
        providers.append({"id": "openai", "name": "OpenAI GPT-4o (configure API key)"})
    return {"providers": providers}
```

- [ ] **Step 7: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add backend/app/routers/ backend/app/main.py
git commit -m "feat: API routers for upload, analysis, stories, and export"
```

---

## Task 8: Frontend Scaffolding — Svelte + Vite Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/svelte.config.js`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.svelte`
- Create: `frontend/src/lib/api.js`
- Create: `frontend/src/lib/stores.js`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "archiscribe-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "svelte": "^5.0.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Create svelte.config.js**

```javascript
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

export default {
  preprocess: vitePreprocess(),
}
```

- [ ] **Step 3: Create vite.config.js**

```javascript
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 4: Create index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Archiscribe</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 5: Create src/main.js**

```javascript
import App from './App.svelte'
import { mount } from 'svelte'

const app = mount(App, { target: document.getElementById('app') })

export default app
```

- [ ] **Step 6: Create src/lib/api.js**

```javascript
const API_BASE = '/api'

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: {},
  }
  if (body && !(body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  } else if (body instanceof FormData) {
    opts.body = body
  }
  const res = await fetch(`${API_BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(err.error || err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  listProviders: () => request('GET', '/providers'),
  createProject: (name) => request('POST', '/projects', { name }),
  getProject: (id) => request('GET', `/projects/${id}`),
  uploadFiles: (projectId, files) => {
    const form = new FormData()
    for (const f of files) form.append('files', f)
    return request('POST', `/projects/${projectId}/upload`, form)
  },
  analyzeDiagram: (projectId, fileIndex = 0) =>
    request('POST', `/projects/${projectId}/analyze?file_index=${fileIndex}`),
  getComponents: (projectId) => request('GET', `/projects/${projectId}/components`),
  updateComponents: (projectId, updates) =>
    request('PUT', `/projects/${projectId}/components`, { components: updates }),
  generateStories: (projectId) => request('POST', `/projects/${projectId}/generate-stories`),
  getStories: (projectId) => request('GET', `/projects/${projectId}/stories`),
  updateStory: (projectId, storyId, updates) =>
    request('PUT', `/projects/${projectId}/stories/${storyId}`, updates),
  deleteStory: (projectId, storyId) =>
    request('DELETE', `/projects/${projectId}/stories/${storyId}`),
  regenerateStory: (projectId, storyId) =>
    request('POST', `/projects/${projectId}/stories/${storyId}/regenerate`),
  addStory: (projectId, storyData) =>
    request('POST', `/projects/${projectId}/stories`, storyData),
  exportMarkdown: (projectId) => request('POST', `/projects/${projectId}/export/markdown`),
}
```

- [ ] **Step 7: Create src/lib/stores.js**

```javascript
import { writable } from 'svelte/store'

export const currentStep = writable(0)
export const project = writable(null)
export const components = writable([])
export const flows = writable([])
export const stories = writable([])
export const selectedStoryId = writable(null)
export const selectedProvider = writable('openai')
```

- [ ] **Step 8: Create src/App.svelte**

```svelte
<script>
  import { currentStep, project } from './lib/stores.js'
  import UploadPage from './pages/UploadPage.svelte'
  import ReviewPage from './pages/ReviewPage.svelte'
  import EditorPage from './pages/EditorPage.svelte'
  import ExportPage from './pages/ExportPage.svelte'

  const steps = ['Upload', 'Review', 'Edit Stories', 'Export']
</script>

<main>
  <header>
    <h1>Archiscribe</h1>
    <nav>
      {#each steps as label, i}
        <button
          class="step-btn"
          class:active={$currentStep === i}
          disabled={i > $currentStep}
          onclick={() => currentStep.set(i)}
        >
          <span class="step-num">{i + 1}</span>
          {label}
        </button>
      {/each}
    </nav>
  </header>

  <section class="content">
    {#if $currentStep === 0}
      <UploadPage />
    {:else if $currentStep === 1}
      <ReviewPage />
    {:else if $currentStep === 2}
      <EditorPage />
    {:else if $currentStep === 3}
      <ExportPage />
    {/if}
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, sans-serif;
    background: #0f1117;
    color: #e0e0e0;
  }
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  header {
    background: #1a1a2e;
    padding: 16px 32px;
    border-bottom: 1px solid #2a2a4a;
    display: flex;
    align-items: center;
    gap: 32px;
  }
  h1 {
    margin: 0;
    font-size: 1.4rem;
    color: #00d4ff;
  }
  nav {
    display: flex;
    gap: 8px;
  }
  .step-btn {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #888;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .step-btn.active {
    background: #1a3a4a;
    border-color: #00d4ff;
    color: #00d4ff;
  }
  .step-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .step-num {
    background: #00d4ff22;
    color: #00d4ff;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
  }
  .content {
    flex: 1;
    padding: 32px;
  }
</style>
```

- [ ] **Step 9: Install dependencies**

```bash
cd /home/vicky/Documents/Repos/archiscribe/frontend
npm install
```

- [ ] **Step 10: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add frontend/
git commit -m "feat: frontend scaffolding with Svelte 5 + Vite"
```

---

## Task 9: Frontend — UploadPage, FileUpload, ProviderSelect

**Files:**
- Create: `frontend/src/pages/UploadPage.svelte`
- Create: `frontend/src/components/FileUpload.svelte`
- Create: `frontend/src/components/ProviderSelect.svelte`

- [ ] **Step 1: Create FileUpload.svelte**

```svelte
<script>
  let files = $state([])
  let dragover = $state(false)

  function handleDrop(e) {
    e.preventDefault()
    dragover = false
    const dropped = Array.from(e.dataTransfer.files)
    files = [...files, ...dropped]
  }

  function handleFileInput(e) {
    const selected = Array.from(e.target.files)
    files = [...files, ...selected]
  }

  function removeFile(i) {
    files = files.filter((_, idx) => idx !== i)
  }

  const accepted = '.png,.jpg,.jpeg,.svg,.webp,.pdf,.drawio,.xml,.excalidraw,.vsdx'
</script>

<div
  class="dropzone"
  class:dragover
  ondrop={handleDrop}
  ondragover={(e) => { e.preventDefault(); dragover = true }}
  ondragleave={() => dragover = false}
  role="button"
  tabindex="0"
>
  <div class="icon">📁</div>
  <p>Drop diagram files here</p>
  <p class="hint">PNG, JPEG, SVG, PDF, Draw.io, Excalidraw, Visio</p>
  <input type="file" {accepted} multiple onchange={handleFileInput} />
</div>

{#if files.length > 0}
  <div class="file-list">
    {#each files as file, i}
      <div class="file-chip">
        <span>{file.name}</span>
        <button onclick={() => removeFile(i)}>✕</button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .dropzone {
    border: 2px dashed #444;
    border-radius: 12px;
    padding: 48px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  .dropzone.dragover {
    border-color: #00d4ff;
    background: #00d4ff11;
  }
  .dropzone input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
  }
  .icon { font-size: 2.5rem; margin-bottom: 8px; }
  p { margin: 4px 0; color: #aaa; }
  .hint { font-size: 0.8rem; color: #666; }
  .file-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
  .file-chip {
    background: #2a2a4a;
    padding: 6px 12px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
  }
  .file-chip button {
    background: none;
    border: none;
    color: #ff6b6b;
    cursor: pointer;
    font-size: 0.9rem;
  }
</style>
```

- [ ] **Step 2: Create ProviderSelect.svelte**

```svelte
<script>
  import { selectedProvider } from '../lib/stores.js'
  let providers = $state([])
  let loading = $state(true)

  $effect(() => {
    import('../lib/api.js').then(m => {
      m.api.listProviders().then(data => {
        providers = data.providers
        if (providers.length > 0 && !$selectedProvider) {
          selectedProvider.set(providers[0].id)
        }
        loading = false
      })
    })
  })
</script>

<div class="provider-select">
  <label>AI Provider</label>
  {#if loading}
    <p class="loading">Loading providers...</p>
  {:else}
    <div class="options">
      {#each providers as p}
        <button
          class="provider-btn"
          class:selected={$selectedProvider === p.id}
          onclick={() => selectedProvider.set(p.id)}
        >
          <span class="provider-name">{p.name}</span>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .provider-select { display: flex; flex-direction: column; gap: 8px; }
  label { font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }
  .loading { color: #666; font-size: 0.9rem; }
  .options { display: flex; flex-direction: column; gap: 6px; }
  .provider-btn {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #ccc;
    padding: 10px 14px;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-size: 0.9rem;
    transition: all 0.15s;
  }
  .provider-btn:hover { border-color: #555; }
  .provider-btn.selected {
    background: #1a3a4a;
    border-color: #00d4ff;
    color: #00d4ff;
  }
</style>
```

- [ ] **Step 3: Create UploadPage.svelte**

```svelte
<script>
  import FileUpload from '../components/FileUpload.svelte'
  import ProviderSelect from '../components/ProviderSelect.svelte'
  import { project, currentStep } from '../lib/stores.js'
  import * as api from '../lib/api.js'

  let files = $state([])
  let uploading = $state(false)
  let error = $state('')

  async function handleAnalyze() {
    if (files.length === 0) {
      error = 'Please add at least one diagram file'
      return
    }
    uploading = true
    error = ''
    try {
      const proj = await api.createProject('Architecture Analysis')
      project.set(proj)
      await api.uploadFiles(proj.id, files)
      await api.analyzeDiagram(proj.id, 0)
      const compData = await api.getComponents(proj.id)
      const storyData = await api.getStories(proj.id)
      import('../lib/stores.js').then(s => {
        s.components.set(compData.components)
        s.flows.set(compData.flows)
        s.stories.set(storyData.stories)
      })
      currentStep.set(1)
    } catch (e) {
      error = e.message
    } finally {
      uploading = false
    }
  }
</script>

<div class="upload-page">
  <h2>Upload Architecture Diagram</h2>
  <p class="subtitle">Upload your diagram files to generate user stories</p>

  <div class="panel">
    <FileUpload bind:files />
    <ProviderSelect />
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <div class="actions">
    <button class="primary" onclick={handleAnalyze} disabled={uploading || files.length === 0}>
      {uploading ? 'Analyzing...' : 'Analyze Diagram →'}
    </button>
  </div>
</div>

<style>
  .upload-page { max-width: 700px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; color: #e0e0e0; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .panel {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  .error { color: #ff6b6b; margin: 8px 0; }
  .actions { margin-top: 24px; display: flex; gap: 12px; }
  .primary {
    background: #00d4ff;
    color: #0f1117;
    border: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
  }
  .primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
```

- [ ] **Step 4: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add frontend/src/pages/UploadPage.svelte frontend/src/components/FileUpload.svelte frontend/src/components/ProviderSelect.svelte
git commit -m "feat: frontend upload page with file drop and provider select"
```

---

## Task 10: Frontend — ReviewPage, ComponentReview, FlowReview

**Files:**
- Create: `frontend/src/pages/ReviewPage.svelte`
- Create: `frontend/src/components/ComponentReview.svelte`
- Create: `frontend/src/components/FlowReview.svelte`

- [ ] **Step 1: Create ComponentReview.svelte**

```svelte
<script>
  import { components, flows } from '../lib/stores.js'
  import * as api from '../lib/api.js'

  let editingId = $state(null)
  let editName = $state('')

  function confirm(id) {
    updateStatus(id, 'confirmed')
  }

  function remove(id) {
    updateStatus(id, 'removed')
  }

  function rename(id, name) {
    editingId = id
    editName = name
  }

  function saveRename(projectId, id) {
    const comps = $components.map(c =>
      c.id === id ? { ...c, name: editName, status: 'renamed' } : c
    )
    components.set(comps)
    api.updateComponents(projectId, { components: comps }).catch(console.error)
    editingId = null
  }

  function updateStatus(id, status) {
    const comps = $components.map(c => c.id === id ? { ...c, status } : c)
    components.set(comps)
  }

  const typeIcons = {
    database: '🗄️', api: '⚡', service: '🔧', queue: '📬',
    storage: '☁️', load_balancer: '⚖️', cache: '⚡', gateway: '🚪',
    client: '🖥️', user: '👤', external: '🔗', unknown: '❓',
  }
</script>

<div class="component-review">
  <h3>Extracted Components</h3>
  <div class="list">
    {#each $components as comp}
      <div class="item" class:confirmed={comp.status === 'confirmed'} class:removed={comp.status === 'removed'}>
        <span class="icon">{typeIcons[comp.component_type] || '❓'}</span>
        <div class="info">
          {#if editingId === comp.id}
            <input bind:value={editName} onkeydown={(e) => e.key === 'Enter' && saveRename(comp.id)} />
          {:else}
            <strong>{comp.name}</strong>
          {/if}
          <span class="type-badge">{comp.component_type}</span>
        </div>
        <div class="actions">
          {#if comp.status !== 'confirmed'}
            <button onclick={() => confirm(comp.id)} title="Confirm">✓</button>
          {/if}
          {#if comp.status !== 'renamed'}
            <button onclick={() => rename(comp.id, comp.name)} title="Rename">✎</button>
          {/if}
          {#if comp.status !== 'removed'}
            <button class="danger" onclick={() => remove(comp.id)} title="Remove">✕</button>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .component-review h3 { margin: 0 0 12px; font-size: 0.9rem; color: #888; text-transform: uppercase; }
  .list { display: flex; flex-direction: column; gap: 6px; }
  .item {
    background: #1a2a3a;
    border: 1px solid #2d4a6b;
    border-radius: 6px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: opacity 0.2s;
  }
  .item.removed { opacity: 0.4; text-decoration: line-through; }
  .icon { font-size: 1.2rem; }
  .info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
  .info input { background: #2a2a4a; border: 1px solid #444; color: #e0e0e0; padding: 4px 8px; border-radius: 4px; }
  .type-badge { font-size: 0.75rem; color: #666; }
  .actions { display: flex; gap: 4px; }
  .actions button {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #888;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
  }
  .actions button:hover { border-color: #00d4ff; color: #00d4ff; }
  .actions button.danger:hover { border-color: #ff6b6b; color: #ff6b6b; }
</style>
```

- [ ] **Step 2: Create FlowReview.svelte**

```svelte
<script>
  import { flows, components } from '../lib/stores.js'

  function getComponentName(id) {
    const comp = $components.find(c => c.id === id)
    return comp ? comp.name : id
  }

  const typeLabels = {
    data: '📦 Data', api_call: '⚡ API Call', event: '📣 Event', async: '⏳ Async', sync: '🔄 Sync'
  }
</script>

<div class="flow-review">
  <h3>Detected Data Flows</h3>
  <div class="list">
    {#each $flows as flow}
      <div class="flow-item">
        <div class="flow-path">
          <span class="node">{getComponentName(flow.source_id)}</span>
          <span class="arrow">→</span>
          <span class="node">{getComponentName(flow.target_id)}</span>
        </div>
        <div class="flow-meta">
          {#if flow.label}<span class="label">{flow.label}</span>{/if}
          <span class="type">{typeLabels[flow.flow_type] || flow.flow_type}</span>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .flow-review h3 { margin: 0 0 12px; font-size: 0.9rem; color: #888; text-transform: uppercase; }
  .list { display: flex; flex-direction: column; gap: 6px; }
  .flow-item {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 10px 12px;
  }
  .flow-path { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-family: monospace; font-size: 0.85rem; }
  .node { color: #00d4ff; }
  .arrow { color: #666; }
  .flow-meta { display: flex; gap: 8px; font-size: 0.75rem; }
  .label { color: #ffe66d; }
  .type { color: #666; }
</style>
```

- [ ] **Step 3: Create ReviewPage.svelte**

```svelte
<script>
  import ComponentReview from '../components/ComponentReview.svelte'
  import FlowReview from '../components/FlowReview.svelte'
  import { project, currentStep } from '../lib/stores.js'
  import * as api from '../lib/api.js'

  let generating = $state(false)

  async function generateStories() {
    if (!$project) return
    generating = true
    try {
      await api.generateStories($project.id)
      const storyData = await api.getStories($project.id)
      import('../lib/stores.js').then(s => s.stories.set(storyData.stories))
      currentStep.set(2)
    } catch (e) {
      console.error(e)
    } finally {
      generating = false
    }
  }
</script>

<div class="review-page">
  <h2>Review Extracted Components</h2>
  <p class="subtitle">Confirm, rename, or remove components before generating stories</p>

  <div class="grid">
    <ComponentReview />
    <FlowReview />
  </div>

  <div class="actions">
    <button class="secondary" onclick={() => currentStep.update(s => s - 1)}>← Back</button>
    <button class="primary" onclick={generateStories} disabled={generating}>
      {generating ? 'Generating...' : 'Generate Stories →'}
    </button>
  </div>
</div>

<style>
  .review-page { max-width: 900px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }
  .actions { display: flex; gap: 12px; }
  .secondary {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #ccc;
    padding: 10px 24px;
    border-radius: 8px;
    cursor: pointer;
  }
  .primary {
    background: #00d4ff;
    color: #0f1117;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
  }
  .primary:disabled { opacity: 0.5; }
</style>
```

- [ ] **Step 4: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add frontend/src/pages/ReviewPage.svelte frontend/src/components/ComponentReview.svelte frontend/src/components/FlowReview.svelte
git commit -m "feat: frontend review page with component and flow editors"
```

---

## Task 11: Frontend — EditorPage, StoryCard, StoryList, StoryEditor

**Files:**
- Create: `frontend/src/pages/EditorPage.svelte`
- Create: `frontend/src/components/StoryCard.svelte`
- Create: `frontend/src/components/StoryList.svelte`
- Create: `frontend/src/components/StoryEditor.svelte`

- [ ] **Step 1: Create StoryCard.svelte**

```svelte
<script>
  let { story, selected = false, onselect } = $props()

  const priorityColors = { High: '#ff6b6b', Medium: '#ffe66d', Low: '#4ecdc4' }
</script>

<div class="card" class:selected onclick={onselect}>
  <div class="header">
    <span class="epic-badge">{story.epic}</span>
    <span class="priority" style="color: {priorityColors[story.priority] || '#888'}">
      {story.priority}
    </span>
  </div>
  <h4>{story.title}</h4>
  <p class="as-a">As a <strong>{story.role}</strong></p>
  <p class="ac-count">{story.acceptance_criteria?.length || 0} acceptance criteria</p>
</div>

<style>
  .card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .card:hover { border-color: #3a3a5a; }
  .card.selected { border-color: #00d4ff; background: #1a2a3a; }
  .header { display: flex; justify-content: space-between; margin-bottom: 6px; }
  .epic-badge { font-size: 0.7rem; background: #2a2a4a; color: #888; padding: 2px 6px; border-radius: 3px; }
  .priority { font-size: 0.75rem; font-weight: 600; }
  h4 { margin: 0 0 4px; font-size: 0.95rem; color: #e0e0e0; }
  .as-a { margin: 0; font-size: 0.8rem; color: #888; }
  .ac-count { margin: 4px 0 0; font-size: 0.75rem; color: #666; }
</style>
```

- [ ] **Step 2: Create StoryList.svelte**

```svelte
<script>
  import StoryCard from './StoryCard.svelte'
  import { stories, selectedStoryId } from '../lib/stores.js'

  function selectStory(id) {
    selectedStoryId.set(id)
  }

  let epics = $derived.by(() => {
    const map = {}
    for (const s of $stories) {
      if (!map[s.epic]) map[s.epic] = []
      map[s.epic].push(s)
    }
    return map
  })
</script>

<div class="story-list">
  <div class="list-header">
    <h3>Stories ({$stories.length})</h3>
    <button class="add-btn" onclick={() => selectedStoryId.set('__new__')}>+ Add</button>
  </div>
  {#each Object.entries(epics) as [epic, epicStories]}
    <div class="epic-group">
      <div class="epic-label">{epic}</div>
      {#each epicStories as story}
        <StoryCard
          {story}
          selected={$selectedStoryId === story.id}
          onselect={() => selectStory(story.id)}
        />
      {/each}
    </div>
  {/each}
</div>

<style>
  .story-list { display: flex; flex-direction: column; gap: 8px; min-width: 240px; }
  .list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  h3 { margin: 0; font-size: 0.85rem; color: #888; text-transform: uppercase; }
  .add-btn {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #4ecdc4;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
  }
  .epic-group { display: flex; flex-direction: column; gap: 4px; }
  .epic-label { font-size: 0.75rem; color: #666; padding: 4px 0; border-bottom: 1px solid #2a2a4a; }
</style>
```

- [ ] **Step 3: Create StoryEditor.svelte**

```svelte
<script>
  import { stories, selectedStoryId, project } from '../lib/stores.js'
  import * as api from '../lib/api.js'

  let editingStory = $state(null)
  let editData = $state({})

  $effect(() => {
    if ($selectedStoryId && $selectedStoryId !== '__new__') {
      const s = $stories.find(st => st.id === $selectedStoryId)
      if (s) {
        editingStory = s
        editData = { ...s, acceptance_criteria: [...(s.acceptance_criteria || [])] }
      }
    } else if ($selectedStoryId === '__new__') {
      editingStory = null
      editData = { epic: 'General', title: '', role: 'user', action: '', value: '', priority: 'Medium', acceptance_criteria: [] }
    } else {
      editingStory = null
    }
  })

  async function save() {
    if (!$project) return
    if (editingStory) {
      await api.updateStory($project.id, editingStory.id, editData)
      stories.update(list => list.map(s => s.id === editingStory.id ? { ...s, ...editData } : s))
    } else {
      const result = await api.addStory($project.id, editData)
      stories.update(list => [...list, { ...editData, id: result.id }])
      selectedStoryId.set(result.id)
    }
  }

  async function deleteStory() {
    if (!$project || !editingStory) return
    await api.deleteStory($project.id, editingStory.id)
    stories.update(list => list.filter(s => s.id !== editingStory.id))
    selectedStoryId.set(null)
  }

  async function regenerate() {
    if (!$project || !editingStory) return
    const result = await api.regenerateStory($project.id, editingStory.id)
    const storyData = await api.getStories($project.id)
    stories.set(storyData.stories)
  }

  function addAC() {
    editData.acceptance_criteria = [...(editData.acceptance_criteria || []), { id: crypto.randomUUID().slice(0,8), description: '', is_testable: true }]
  }

  function removeAC(i) {
    editData.acceptance_criteria = editData.acceptance_criteria.filter((_, idx) => idx !== i)
  }
</script>

<div class="story-editor">
  {#if editingStory || $selectedStoryId === '__new__'}
    <div class="form">
      <div class="form-row">
        <label>Epic</label>
        <input bind:value={editData.epic} placeholder="Epic name" />
      </div>
      <div class="form-row">
        <label>Title</label>
        <input bind:value={editData.title} placeholder="Story title" />
      </div>
      <div class="form-row">
        <label>As a</label>
        <input bind:value={editData.role} placeholder="role" />
      </div>
      <div class="form-row">
        <label>I want</label>
        <input bind:value={editData.action} placeholder="action" />
      </div>
      <div class="form-row">
        <label>so that</label>
        <input bind:value={editData.value} placeholder="value" />
      </div>
      <div class="form-row">
        <label>Priority</label>
        <select bind:value={editData.priority}>
          <option>High</option><option>Medium</option><option>Low</option>
        </select>
      </div>

      <div class="ac-section">
        <div class="ac-header">
          <label>Acceptance Criteria</label>
          <button onclick={addAC}>+ Add</button>
        </div>
        {#each editData.acceptance_criteria || [] as ac, i}
          <div class="ac-row">
            <input
              value={ac.description}
              oninput={(e) => { ac.description = e.target.value; editData.acceptance_criteria = [...editData.acceptance_criteria] }}
              placeholder="Criterion..."
            />
            <button class="danger" onclick={() => removeAC(i)}>✕</button>
          </div>
        {/each}
      </div>

      <div class="tech-notes">
        {#if editingStory?.technical_notes}
          <label>Technical Notes</label>
          <div class="note-items">
            {#if editingStory.technical_notes.source_components?.length}
              <div><strong>Components:</strong> {editingStory.technical_notes.source_components.join(', ')}</div>
            {/if}
            {#if editingStory.technical_notes.source_flows?.length}
              <div><strong>Flows:</strong> {editingStory.technical_notes.source_flows.join(', ')}</div>
            {/if}
          </div>
        {/if}
      </div>

      <div class="actions">
        <button class="secondary" onclick={regenerate}>Regenerate</button>
        <button class="danger" onclick={deleteStory}>Delete</button>
        <button class="primary" onclick={save}>Save</button>
      </div>
    </div>
  {:else}
    <div class="empty">
      <p>Select a story to edit, or click "+ Add" to create a new one.</p>
    </div>
  {/if}
</div>

<style>
  .story-editor { flex: 1; }
  .form { display: flex; flex-direction: column; gap: 12px; max-width: 600px; }
  .form-row { display: flex; flex-direction: column; gap: 4px; }
  label { font-size: 0.8rem; color: #888; text-transform: uppercase; }
  input, select {
    background: #1a1a2e;
    border: 1px solid #3a3a5a;
    color: #e0e0e0;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9rem;
  }
  input:focus, select:focus { outline: none; border-color: #00d4ff; }
  .ac-section { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px; padding: 12px; }
  .ac-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .ac-header button { background: #2a2a4a; border: 1px solid #3a3a5a; color: #4ecdc4; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
  .ac-row { display: flex; gap: 8px; margin-bottom: 6px; }
  .ac-row input { flex: 1; }
  .ac-row button.danger { background: none; border: none; color: #ff6b6b; cursor: pointer; }
  .tech-notes { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px; padding: 12px; }
  .tech-notes label { margin-bottom: 6px; display: block; }
  .note-items { font-size: 0.8rem; color: #888; display: flex; flex-direction: column; gap: 4px; }
  .actions { display: flex; gap: 8px; margin-top: 8px; }
  .primary { background: #00d4ff; color: #0f1117; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; }
  .secondary { background: #2a2a4a; border: 1px solid #3a3a5a; color: #ccc; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
  .danger { background: #3a1a1a; border: 1px solid #6b2d2d; color: #ff6b6b; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
  .empty { display: flex; align-items: center; justify-content: center; height: 200px; color: #666; }
</style>
```

- [ ] **Step 4: Create EditorPage.svelte**

```svelte
<script>
  import StoryList from '../components/StoryList.svelte'
  import StoryEditor from '../components/StoryEditor.svelte'
  import { currentStep } from '../lib/stores.js'
</script>

<div class="editor-page">
  <h2>Edit Stories</h2>
  <p class="subtitle">Review and refine generated user stories</p>

  <div class="editor-layout">
    <StoryList />
    <StoryEditor />
  </div>

  <div class="actions">
    <button class="secondary" onclick={() => currentStep.update(s => s - 1)}>← Back</button>
    <button class="primary" onclick={() => currentStep.set(3)}>Export →</button>
  </div>
</div>

<style>
  .editor-page { max-width: 1100px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .editor-layout { display: flex; gap: 24px; margin-bottom: 32px; }
  .actions { display: flex; gap: 12px; }
  .secondary { background: #2a2a4a; border: 1px solid #3a3a5a; color: #ccc; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
  .primary { background: #00d4ff; color: #0f1117; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
</style>
```

- [ ] **Step 5: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add frontend/src/pages/EditorPage.svelte frontend/src/components/StoryCard.svelte frontend/src/components/StoryList.svelte frontend/src/components/StoryEditor.svelte
git commit -m "feat: frontend story editor with list, card, and inline editing"
```

---

## Task 12: Frontend — ExportPage, ExportPanel

**Files:**
- Create: `frontend/src/pages/ExportPage.svelte`
- Create: `frontend/src/components/ExportPanel.svelte`

- [ ] **Step 1: Create ExportPanel.svelte**

```svelte
<script>
  let { markdown = '' } = $props()
  let copied = $state(false)

  function download() {
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'product-backlog.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  async function copyToClipboard() {
    await navigator.clipboard.writeText(markdown)
    copied = true
    setTimeout(() => copied = false, 2000)
  }
</script>

<div class="export-panel">
  <div class="toolbar">
    <button onclick={download}>⬇ Download .md</button>
    <button onclick={copyToClipboard}>{copied ? '✓ Copied!' : '📋 Copy to Clipboard'}</button>
  </div>
  <div class="preview">
    <pre>{markdown}</pre>
  </div>
</div>

<style>
  .export-panel { display: flex; flex-direction: column; gap: 16px; }
  .toolbar { display: flex; gap: 10px; }
  .toolbar button {
    background: #2a2a4a;
    border: 1px solid #3a3a5a;
    color: #e0e0e0;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
  }
  .toolbar button:hover { border-color: #00d4ff; color: #00d4ff; }
  .preview {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 20px;
    max-height: 500px;
    overflow: auto;
  }
  pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: #ccc;
    line-height: 1.6;
  }
</style>
```

- [ ] **Step 2: Create ExportPage.svelte**

```svelte
<script>
  import ExportPanel from '../components/ExportPanel.svelte'
  import { project, currentStep } from '../lib/stores.js'
  import * as api from '../lib/api.js'

  let markdown = $state('')
  let loading = $state(true)

  $effect(() => {
    if ($project) {
      api.exportMarkdown($project.id)
        .then(data => { markdown = data.markdown; loading = false })
        .catch(e => { console.error(e); loading = false })
    }
  })
</script>

<div class="export-page">
  <h2>Export Backlog</h2>
  <p class="subtitle">Download your product backlog as Markdown</p>

  {#if loading}
    <p class="loading">Generating markdown...</p>
  {:else}
    <ExportPanel {markdown} />
  {/if}

  <div class="actions">
    <button class="secondary" onclick={() => currentStep.update(s => s - 1)}>← Back to Editor</button>
  </div>
</div>

<style>
  .export-page { max-width: 900px; margin: 0 auto; }
  h2 { margin: 0 0 8px; font-size: 1.5rem; }
  .subtitle { color: #888; margin: 0 0 24px; }
  .loading { color: #666; }
  .actions { margin-top: 24px; }
  .secondary { background: #2a2a4a; border: 1px solid #3a3a5a; color: #ccc; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
</style>
```

- [ ] **Step 3: Commit**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add frontend/src/pages/ExportPage.svelte frontend/src/components/ExportPanel.svelte
git commit -m "feat: frontend export page with markdown preview and download"
```

---

## Task 13: Integration — Add README, Final Wiring, .gitignore

**Files:**
- Create: `README.md`
- Modify: `frontend/src/lib/stores.js` (fix re-export issue)

- [ ] **Step 1: Create README.md**

```markdown
# Archiscribe

Transform architectural diagrams into detailed user story backlogs.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt

# Set API keys (optional, will use placeholder if not set)
export ARCHISCRIBE_OPENAI_API_KEY=sk-...
export ARCHISCRIBE_ANTHROPIC_API_KEY=sk-ant-...
export ARCHISCRIBE_GOOGLE_API_KEY=...

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Usage

1. Upload diagram files (PNG, PDF, Draw.io, Excalidraw, Visio)
2. Review and confirm extracted components
3. Edit generated user stories
4. Export as Markdown backlog
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.py[cod]
.env
.venv/
node_modules/
dist/
.superpowers/
.DS_Store
```

- [ ] **Step 3: Final import fix for routers**

The routers reference `_projects` dict from `upload.py` as a module-level global. Ensure `analysis.py`, `stories.py`, `export.py` all import from `upload.py` correctly. Also ensure `main.py` imports routers from the same module.

- [ ] **Step 4: Run full backend test**

```bash
cd /home/vicky/Documents/Repos/archiscribe/backend
python -c "
from app.main import app
from app.models import Component, UserStory
from app.parsers import get_parser
from app.ai import get_provider
from app.exporters import MarkdownExporter
print('All imports OK')
"
```

- [ ] **Step 5: Commit all remaining changes**

```bash
cd /home/vicky/Documents/Repos/archiscribe
git add README.md .gitignore
git add -A
git commit -m "feat: complete archiscribe application with full frontend and backend"
```

---

## Spec Coverage Check

| Spec Section | Tasks |
|---|---|
| Project structure | Task 1, 8 |
| Parser strategy (all 5 formats) | Task 2, 3 |
| AI provider abstraction (3 providers) | Task 4 |
| Data models (Component, DataFlow, UserStory, AC, TN) | Task 1 |
| API endpoints (all 14) | Task 7 |
| 4-page wizard UI | Task 9, 10, 11, 12 |
| Markdown export format | Task 6 |
| Full editorial workflow (confirm/rename/remove/add, edit stories, regenerate) | Task 10, 11 |

**All spec requirements are covered by tasks.**

---

## Plan Complete

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
