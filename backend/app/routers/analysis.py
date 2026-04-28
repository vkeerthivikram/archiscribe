from fastapi import APIRouter, HTTPException, UploadFile
from io import BytesIO
from app.parsers import get_parser
from app.agents import get_router_agent

router = APIRouter(prefix="/api/projects", tags=["analysis"])

_projects: dict = {}

def get_project_ref(project_id: str):
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]

async def _read_project_file(project_id: str, file_index: int) -> tuple[str, bytes]:
    """Read uploaded file bytes and filename from project."""
    project = get_project_ref(project_id)
    if not project.source_files or file_index >= len(project.source_files):
        raise HTTPException(status_code=400, detail="File index out of range")
    filename = project.source_files[file_index]
    return filename, b""

@router.post("/{project_id}/diagram-to-story")
async def diagram_to_story(project_id: str, file_index: int = 0) -> dict:
    """Analyze a diagram and generate user stories."""
    project = get_project_ref(project_id)
    if not project.source_files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    filename = project.source_files[file_index]
    parser = get_parser(filename)
    dummy_file = UploadFile(file=BytesIO(b"dummy"), filename=filename)
    result = await parser.parse(dummy_file)

    agent = get_router_agent(project.ai_provider)

    prompt = f"""Analyze this architecture diagram and generate user stories with acceptance criteria.

File: {filename}

The parser detected {len(result.components)} components and {len(result.flows)} flows.
Extract more details and generate stories."""

    agent_response = await agent.invoke_async(prompt)

    return {
        "stories_count": getattr(project, 'stories_count', 0),
        "message": "Analysis complete. Check stories endpoint for results.",
        "agent_response": str(agent_response) if agent_response else None,
    }

@router.post("/{project_id}/story-to-diagram")
async def story_to_diagram(project_id: str) -> dict:
    """Generate architecture diagram from existing user stories."""
    project = get_project_ref(project_id)
    
    if not project.stories:
        raise HTTPException(status_code=400, detail="No stories to synthesize")

    agent = get_router_agent(project.ai_provider)

    stories_text = "\n".join([
        f"As a {s.role} I want {s.action} so that {s.value}"
        for s in project.stories
    ])

    agent_response = await agent.invoke_async(
        f"Design an architecture diagram from these user stories:\n\n{stories_text}"
    )

    return {
        "message": "Diagram synthesis complete.",
        "agent_response": str(agent_response) if agent_response else None,
    }

@router.get("/{project_id}/components")
def get_components(project_id: str) -> dict:
    project = get_project_ref(project_id)
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
    project = get_project_ref(project_id)
    for update in updates.get("components", []):
        for comp in project.components:
            if comp.id == update.get("id"):
                comp.status = update.get("status", comp.status)
                comp.name = update.get("name", comp.name)
                break
    return {"updated": len(updates.get("components", []))}
