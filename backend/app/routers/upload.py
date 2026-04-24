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