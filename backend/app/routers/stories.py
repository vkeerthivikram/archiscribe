from fastapi import APIRouter, HTTPException
from app.models.story import UserStory

router = APIRouter(prefix="/api/projects", tags=["stories"])


def get_project_ref(project_id: str):
    from app.routers.upload import _projects
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]


@router.post("/{project_id}/generate-stories")
async def generate_stories(project_id: str) -> dict:
    project = get_project_ref(project_id)

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
    project = get_project_ref(project_id)
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
    project = get_project_ref(project_id)
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
    project = get_project_ref(project_id)
    original = len(project.stories)
    project.stories = [s for s in project.stories if s.id != story_id]
    return {"deleted": len(project.stories) < original}


@router.post("/{project_id}/stories/{story_id}/regenerate")
async def regenerate_story(project_id: str, story_id: str) -> dict:
    project = get_project_ref(project_id)
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
    project = get_project_ref(project_id)
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