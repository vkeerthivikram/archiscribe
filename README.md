# Archiscribe

Transform architectural diagrams into detailed user story backlogs.

Upload a diagram (PNG, JPEG, SVG, PDF, Draw.io, Excalidraw, or Visio) and get back a structured Markdown backlog with user stories, acceptance criteria, and technical notes tracing each story back to the original diagram.

## Setup

### Backend

```bash
cd backend
uv pip install -r requirements.txt

# Set API keys (optional - will use placeholder if not set)
export ARCHISCRIBE_OPENAI_API_KEY=sk-...
export ARCHISCRIBE_ANTHROPIC_API_KEY=sk-ant-...
export ARCHISCRIBE_GOOGLE_API_KEY=...

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
bun install
bun run dev
```

Open http://localhost:5173

## Usage

1. **Upload** — Drag and drop diagram files
2. **Review** — Confirm, rename, or remove extracted components
3. **Edit** — Refine generated user stories, add acceptance criteria
4. **Export** — Download as Markdown product backlog

## Architecture

- `backend/app/parsers/` — File format parsers (structural + LLM vision)
- `backend/app/ai/` — Multi-provider AI abstraction (OpenAI, Anthropic, Gemini)
- `backend/app/generators/` — Component extraction and story generation
- `backend/app/exporters/` — Markdown backlog export
- `frontend/src/` — Svelte 5 SPA with 4-page wizard
