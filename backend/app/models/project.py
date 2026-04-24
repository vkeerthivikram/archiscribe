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