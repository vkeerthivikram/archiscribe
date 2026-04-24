from dataclasses import dataclass, field
from typing import Literal, Self
from app.models.diagram import Component, DataFlow


@dataclass
class AcceptanceCriterion:
    id: str
    description: str
    is_testable: bool = True

    @classmethod
    def make(cls, description: str) -> Self:
        import uuid
        return cls(id=str(uuid.uuid4())[:8], description=description)


@dataclass
class TechnicalNotes:
    source_components: list[str] = field(default_factory=list)
    source_flows: list[str] = field(default_factory=list)
    diagram_references: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


Priority = Literal["High", "Medium", "Low"]


@dataclass
class UserStory:
    id: str
    epic: str
    title: str
    role: str
    action: str
    value: str
    priority: Priority = "Medium"
    story_points: int | None = None
    acceptance_criteria: list[AcceptanceCriterion] = field(default_factory=list)
    technical_notes: TechnicalNotes = field(default_factory=TechnicalNotes)

    @classmethod
    def make(
        cls,
        epic: str,
        title: str,
        role: str,
        action: str,
        value: str,
        priority: Priority = "Medium",
        components: list[Component] | None = None,
        flows: list[DataFlow] | None = None,
    ) -> Self:
        import uuid
        story_id = str(uuid.uuid4())[:8]
        notes = TechnicalNotes(
            source_components=[c.id for c in (components or [])],
            source_flows=[f.id for f in (flows or [])],
        )
        return cls(
            id=story_id,
            epic=epic,
            title=title,
            role=role,
            action=action,
            value=value,
            priority=priority,
            technical_notes=notes,
        )