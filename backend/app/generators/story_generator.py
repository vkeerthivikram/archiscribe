from app.ai.base import BaseAIProvider
from app.models.diagram import Component, DataFlow
from app.models.story import UserStory


class StoryGenerator:
    """Converts extracted components and flows into user stories."""

    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider

    async def generate(
        self,
        components: list[Component],
        flows: list[DataFlow],
    ) -> list[UserStory]:
        """Generate user stories from components and flows using AI."""
        return await self.ai_provider.generate_stories(components, flows)

    def group_by_epic(self, stories: list[UserStory]) -> dict[str, list[UserStory]]:
        """Group stories into epics by component type."""
        epic_map: dict[str, list[UserStory]] = {}
        for story in stories:
            if story.epic not in epic_map:
                epic_map[story.epic] = []
            epic_map[story.epic].append(story)
        return epic_map
