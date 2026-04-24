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