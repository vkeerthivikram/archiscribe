# ArchiScribe → Strands Agents Migration Design

## Summary

Migrate the AI layer from 6 hand-rolled provider classes to the Strands Agents SDK, using Approach C (Agent-as-Tool Composition) with a coordinator agent that routes to two specialist agents: one for diagram→story, one for story→diagram.

## Current State

- 6 custom `BaseAIProvider` subclasses in `app/ai/` (openai, anthropic, gemini, bedrock, kilo_gateway, openrouter)
- Each implements `analyze_image()` and `generate_text()` with direct SDK calls
- `ComponentExtractor` and `StoryGenerator` thin wrappers delegate to provider
- `AcceptanceCriteriaGenerator` is template-based (no AI)
- Routers manually orchestrate parse → extract → generate pipeline
- Supports only diagram → stories direction

## Target State

### Architecture

```
FastAPI Router
     │
     ▼
RouterAgent (coordinator)
     │
     ├── diagram_to_story_agent.as_tool()   # Option 1
     │      ├── @tool extract_components
     │      ├── @tool identify_flows
     │      ├── @tool generate_stories
     │      └── @tool generate_acceptance_criteria
     │
     └── story_to_diagram_agent.as_tool()   # Option 2
            ├── @tool parse_user_stories
            ├── @tool synthesize_architecture
            └── @tool render_diagram
```

### File Structure

Replace `app/ai/` entirely with `app/agents/`:

```
backend/app/
├── agents/
│   ├── __init__.py              # exports + get_router_agent()
│   ├── models.py                # model factory (6 providers → Strands models)
│   ├── router_agent.py          # coordinator
│   ├── diagram_to_story/
│   │   ├── __init__.py
│   │   ├── agent.py             # DiagramToStoryAgent
│   │   └── tools.py             # @tool functions
│   └── story_to_diagram/
│       ├── __init__.py
│       ├── agent.py             # StoryToDiagramAgent
│       └── tools.py             # @tool functions
├── generators/                  # kept for acceptance criteria templates only
├── parsers/                     # unchanged
├── models/                      # unchanged (dataclasses)
├── routers/                     # simplified
└── config.py                    # extended with new env vars
```

## Component Details

### Model Provider Factory (`agents/models.py`)

All 6 providers mapped to Strands model classes:

| Provider | Strands Class | Notes |
|---|---|---|
| `openai` | `OpenAIModel` | Native support |
| `anthropic` | `AnthropicModel` | Native support |
| `gemini` | `GeminiModel` | Native support |
| `bedrock` | `BedrockModel` | Native support |
| `openrouter` | `OpenAIModel` | OpenAI-compatible with custom `base_url` |
| `kilo` | `OpenAIModel` | OpenAI-compatible with custom `base_url` |

A single `create_model(provider_id: str)` function reads config and returns the correct Strands model instance. All existing provider files (`*_provider.py`) are deleted.

### RouterAgent (Coordinator)

Lightweight agent that detects intent and delegates:

- System prompt instructs: image/diagram input → `diagram_to_story_agent`, stories/requirements input → `story_to_diagram_agent`
- Tools: two sub-agents registered via `.as_tool()`
- Uses whichever model the project is configured with
- Returns the specialist's result directly to the caller

### DiagramToStoryAgent

System prompt: expert architect + product manager. Workflow: extract → identify flows → generate stories → generate criteria.

Tools:

| Tool | Input | Output | Description |
|---|---|---|---|
| `extract_components` | image bytes | `list[Component]` | Sends image to vision model, returns structured components |
| `identify_flows` | image bytes | `list[DataFlow]` | Sends image to vision model, returns data flows |
| `generate_stories` | components, flows | `list[UserStory]` | Generates stories from extracted architecture |
| `generate_acceptance_criteria` | story, components | `list[AcceptanceCriterion]` | Generates testable criteria per story |

Tools use `structured_output()` internally for typed responses.

### StoryToDiagramAgent

System prompt: expert software architect. Workflow: parse stories → synthesize architecture → render diagram.

Tools:

| Tool | Input | Output | Description |
|---|---|---|---|
| `parse_user_stories` | raw stories text | `list[UserStory]` | Structures unformatted story input into typed objects |
| `synthesize_architecture` | structured stories | `list[Component]`, `list[DataFlow]` | Infers components, services, databases, and connections from story requirements |
| `render_diagram` | components, flows, format | diagram bytes (SVG/PNG/DrawIO/Mermaid) | Generates visual architecture diagram in requested format |

Mermaid is used as intermediate representation; converted to other formats via rendering libraries. All 4 output formats supported: SVG, PNG, DrawIO/XML, Mermaid.

### Router Changes

**New endpoints:**

| Endpoint | Direction | Input | Output |
|---|---|---|---|
| `POST /{id}/diagram-to-story` | Diagram → Stories | Uploaded diagram file | Components, flows, stories with criteria |
| `POST /{id}/story-to-diagram` | Stories → Diagram | Stories text/JSON | Components, flows, diagram (SVG/PNG/DrawIO/Mermaid) |

**Kept unchanged:**
- `GET /{id}/components`, `GET /{id}/stories`
- `PUT/DELETE /{id}/stories/{sid}`
- Upload and project CRUD endpoints

Old `/analyze` and `/generate-stories` endpoints are replaced.

### Error Handling

- Model provider failures → caught at tool level, return structured error to agent for retry
- Invalid image input → `extract_components` tool validates before sending to model
- Malformed stories input → `parse_user_stories` tool validates structure
- Agent loop timeout → configurable max iterations (default: 10)
- All errors surfaced through FastAPI `HTTPException`

### Testing

- Tool functions tested in isolation with mocked Strands model
- Each agent tested with `callback_handler=None` to capture structured results
- Router endpoints tested via FastAPI `TestClient`
- Integration tests mock the Strands model provider

## Dependencies

Add to `requirements.txt`:
- `strands-agents>=1.0.0`
- `strands-agents[openai]` (optional dep for OpenAI provider)
- `strands-agents[anthropic]` (optional dep for Anthropic provider)
- Diagram rendering libraries (for story→diagram direction)

Remove:
- Direct `openai`, `anthropic`, `google-genai`, `boto3` deps (Strands handles these internally)
