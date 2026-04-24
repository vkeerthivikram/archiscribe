# Archiscribe — Design Specification

**Date:** 2026-04-24
**Status:** Approved

## Overview

Archiscribe is a web application that transforms architectural diagrams into structured user story backlogs. Users upload diagram files (images, PDFs, Draw.io, Excalidraw, Visio), the AI extracts components and data flows, and the user reviews/edits before exporting as a professional Markdown product backlog.

## Architecture

**Monolithic pipeline** — single FastAPI backend with Svelte frontend.

```
Upload → Parse (structural or vision) → Extract Components → Generate Stories → Export
```

All processing modules live in one FastAPI process. AI calls are async I/O. Frontend communicates via REST API.

## Tech Stack

- **Frontend:** Svelte 5 + Vite (SPA)
- **Backend:** Python 3.12+ / FastAPI / Uvicorn
- **AI Providers:** OpenAI GPT-4o, Anthropic Claude, Google Gemini (unified abstraction)
- **Deployment:** Local development only

## Project Structure

```
archiscribe/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── diagram.py
│   │   │   ├── story.py
│   │   │   └── project.py
│   │   ├── parsers/
│   │   │   ├── base.py
│   │   │   ├── image_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── drawio_parser.py
│   │   │   ├── excalidraw_parser.py
│   │   │   └── visio_parser.py
│   │   ├── ai/
│   │   │   ├── base.py
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── gemini_provider.py
│   │   ├── generators/
│   │   │   ├── component_extractor.py
│   │   │   ├── story_generator.py
│   │   │   └── acceptance_criteria.py
│   │   ├── exporters/
│   │   │   └── markdown_exporter.py
│   │   └── routers/
│   │       ├── upload.py
│   │       ├── analysis.py
│   │       ├── stories.py
│   │       └── export.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.svelte
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
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.js
├── docs/
│   └── superpowers/specs/
├── .gitignore
└── README.md
```

## Parser Strategy — Hybrid Structural + Vision

Each format uses the optimal parsing strategy:

| Format | Parser | Strategy |
|--------|--------|----------|
| PNG/JPEG/SVG/WebP | `image_parser` | Send directly to LLM vision with extraction prompt |
| PDF | `pdf_parser` | Convert pages to images via `pdf2image`, then LLM vision |
| Draw.io (.drawio/.xml) | `drawio_parser` | Parse XML structurally — extract cells, edges, labels |
| Excalidraw (.excalidraw/.json) | `excalidraw_parser` | Parse JSON structurally — extract elements, arrows, text |
| Visio (.vsdx) | `visio_parser` | Extract embedded images + parse page XML, then LLM vision |

All parsers implement a common interface:

```python
class BaseParser(ABC):
    @abstractmethod
    async def parse(self, file: UploadFile) -> ParseResult:
        """Returns ParseResult with components, flows, and raw metadata."""

@dataclass
class ParseResult:
    components: list[Component]
    flows: list[DataFlow]
    raw_metadata: dict
    source_file: str
    parser_type: str  # "structural" or "vision"
```

## AI Provider Abstraction

```python
class BaseAIProvider(ABC):
    @abstractmethod
    async def analyze_image(self, image: bytes, prompt: str) -> dict: ...

    @abstractmethod
    async def generate_text(self, prompt: str, system: str) -> str: ...

    @abstractmethod
    async def extract_components(self, image: bytes) -> list[Component]: ...

    @abstractmethod
    async def generate_stories(self, components: list[Component], flows: list[DataFlow]) -> list[UserStory]: ...
```

Each provider implements this with provider-specific SDKs. Prompt templates are stored as string constants and shared across providers.

## Data Models

```python
@dataclass
class Component:
    id: str
    name: str
    component_type: str      # database, api, service, queue, storage, load_balancer, etc.
    description: str
    position: tuple[int, int] | None
    properties: dict
    source: str
    status: str              # "confirmed", "renamed", "removed", "added"

@dataclass
class DataFlow:
    id: str
    source_id: str
    target_id: str
    label: str | None
    flow_type: str           # "data", "api_call", "event", "async"
    protocol: str | None

@dataclass
class UserStory:
    id: str
    epic: str
    title: str
    role: str
    action: str
    value: str
    priority: str            # High, Medium, Low
    story_points: int | None
    acceptance_criteria: list[AcceptanceCriterion]
    technical_notes: TechnicalNotes

@dataclass
class AcceptanceCriterion:
    id: str
    description: str
    is_testable: bool

@dataclass
class TechnicalNotes:
    source_components: list[str]
    source_flows: list[str]
    diagram_references: list[str]
    dependencies: list[str]
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/projects` | Create new project/session |
| `POST` | `/api/projects/{id}/upload` | Upload diagram files |
| `POST` | `/api/projects/{id}/analyze` | Run parser + component extraction |
| `GET` | `/api/projects/{id}/components` | Get extracted components |
| `PUT` | `/api/projects/{id}/components` | Update components (confirm/rename/remove/add) |
| `POST` | `/api/projects/{id}/generate-stories` | Generate stories from confirmed components |
| `GET` | `/api/projects/{id}/stories` | List all stories |
| `PUT` | `/api/projects/{id}/stories/{sid}` | Edit individual story |
| `DELETE` | `/api/projects/{id}/stories/{sid}` | Remove story |
| `POST` | `/api/projects/{id}/stories/{sid}/regenerate` | Regenerate single story |
| `POST` | `/api/projects/{id}/stories` | Add manual story |
| `POST` | `/api/projects/{id}/export/markdown` | Export as Markdown |
| `GET` | `/api/providers` | List configured AI providers |

## Frontend — 4-Page Wizard

Managed by a Svelte store tracking current step and project state:

1. **UploadPage** — File drop zone + AI provider selector. Uploads files and triggers analysis.
2. **ReviewPage** — Two-column: extracted components (left) with confirm/rename/remove/add actions, detected data flows (right).
3. **EditorPage** — Story list sidebar + focused story editor. Inline editing, drag reorder, add/regenerate stories.
4. **ExportPage** — Markdown preview with download and copy-to-clipboard.

State management via Svelte stores with a single `project` store mirroring backend state.

## Markdown Export Format

```markdown
# Product Backlog — Architectural Diagram Analysis

_Generated by Archiscribe on {date}_
_Source files: {filenames}_
_AI Provider: {provider}_

---

## Epic: {epic_name}

### US-{id}: {title}

**As a** {role}
**I want** {action}
**so that** {value}

**Priority:** {priority} | **Story Points:** {points}

#### Acceptance Criteria
- [ ] {criterion_1}
- [ ] {criterion_2}

#### Technical Notes
- **Source components:** {component_names}
- **Diagram references:** {file} ({x}, {y})
- **Dependencies:** US-{ids}

---
```

## Key Dependencies

**Backend:**
- `fastapi`, `uvicorn` — API server
- `python-multipart` — file uploads
- `openai`, `anthropic`, `google-generativeai` — AI SDKs
- `pdf2image`, `Pillow` — PDF/image processing
- `lxml` — Draw.io XML parsing
- `python-pptx`, `olefile` — Visio file extraction
- `pydantic` — data validation

**Frontend:**
- Svelte 5 + Vite
- No heavy UI framework — custom components with Svelte built-in reactivity

## Out of Scope

- User authentication — single-user local tool
- Database persistence — in-memory session state (data lives for the duration of a browser session)
- Real-time collaboration
- Direct Jira/Azure DevOps API push
- CI/CD pipeline
