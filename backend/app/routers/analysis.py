from fastapi import APIRouter, HTTPException
from app.models.diagram import Component, DataFlow
from app.parsers import get_parser
from app.generators import ComponentExtractor, StoryGenerator
from app.ai import get_provider

router = APIRouter(prefix="/api/projects", tags=["analysis"])

_projects: dict = {}


def get_project_ref(project_id: str):
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]


@router.post("/{project_id}/analyze")
async def analyze_diagram(project_id: str, file_index: int = 0) -> dict:
    project = get_project_ref(project_id)
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