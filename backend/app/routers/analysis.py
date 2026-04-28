import json
import uuid
from fastapi import APIRouter, HTTPException, UploadFile
from io import BytesIO
from app.parsers import get_parser
from app.agents import get_router_agent
from app.models.diagram import Component, DataFlow
from app.models.story import UserStory, AcceptanceCriterion

router = APIRouter(prefix="/api/projects", tags=["analysis"])

_projects: dict = {}

def get_project_ref(project_id: str):
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]


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

    try:
        agent_response = await agent.invoke_async(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")

    if agent_response:
        try:
            parsed = json.loads(str(agent_response)) if isinstance(agent_response, str) else agent_response
            if isinstance(parsed, dict) and "stories" in parsed:
                for story_data in parsed.get("stories", []):
                    story = UserStory.make(
                        epic=story_data.get("epic", "General"),
                        title=story_data.get("title", "Untitled"),
                        role=story_data.get("role", "user"),
                        action=story_data.get("action", "perform action"),
                        value=story_data.get("value", "derive value"),
                        priority=story_data.get("priority", "Medium"),
                    )
                    for criterion_desc in story_data.get("acceptance_criteria", []):
                        story.acceptance_criteria.append(AcceptanceCriterion.make(criterion_desc))
                    project.stories.append(story)
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "stories_count": len(project.stories),
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

    try:
        agent_response = await agent.invoke_async(
            f"Design an architecture diagram from these user stories:\n\n{stories_text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")

    if agent_response:
        try:
            parsed = json.loads(str(agent_response)) if isinstance(agent_response, str) else agent_response
            if isinstance(parsed, dict):
                for comp_data in parsed.get("components", []):
                    comp = Component(
                        id=str(uuid.uuid4())[:8],
                        name=comp_data.get("name", "Unknown"),
                        component_type=comp_data.get("type", "unknown"),
                        description=comp_data.get("description", ""),
                        position=tuple(comp_data.get("position", [0, 0])) if comp_data.get("position") else None,
                    )
                    project.components.append(comp)
                for flow_data in parsed.get("flows", []):
                    flow = DataFlow(
                        id=str(uuid.uuid4())[:8],
                        source_id=flow_data.get("source", ""),
                        target_id=flow_data.get("target", ""),
                        label=flow_data.get("label"),
                        flow_type=flow_data.get("type", "data"),
                    )
                    project.flows.append(flow)
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "components_count": len(project.components),
        "flows_count": len(project.flows),
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
