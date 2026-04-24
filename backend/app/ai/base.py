from abc import ABC, abstractmethod
from app.models.diagram import Component, DataFlow
from app.models.story import UserStory


EXTRACTION_PROMPT = """You are an expert at analyzing architectural diagrams.

Analyze this diagram image and extract ALL components and data flows you can identify.

For each component, identify:
- name: what it's called (e.g., "PostgreSQL", "API Gateway", "User Browser")
- type: one of: database, api, service, queue, storage, load_balancer, cache, gateway, client, user, external, unknown
- description: brief description of what it does
- position: x,y coordinates if visible (approximate is fine)

For each data flow/connection, identify:
- source: the component name or ID that is the origin
- target: the component name or ID that is the destination
- label: any text label on the arrow/connection
- type: one of: data, api_call, event, async, sync

Return your analysis as a structured JSON object with this format:
{
  "components": [
    {"name": "...", "type": "...", "description": "...", "position": [x, y]}
  ],
  "flows": [
    {"source": "...", "target": "...", "label": "...", "type": "..."}
  ]
}

Be thorough. Identify every component and connection you can see."""


STORY_GENERATION_PROMPT = """You are an expert product manager who transforms architectural diagrams into user stories.

Given the following components and data flows extracted from an architecture diagram, generate a set of user stories.

Components:
{components_text}

Data Flows:
{flows_text}

Generate user stories following this format for EACH distinct functional capability:
- Group related components into epics
- For each epic, create user stories in format:
  **As a** [role]
  **I want** [action]
  **so that** [value]

Rules:
- Derive the role from the diagram context (e.g., "system architect", "backend developer", "DevOps engineer")
- Derive the action from what the component does
- Derive the value from the business/technical benefit
- Each story should be focused on ONE component or ONE data flow
- Infer reasonable acceptance criteria for each story
- Assign priority (High/Medium/Low) based on architectural importance

Return as structured JSON:
{{
  "epics": [
    {{
      "name": "Epic Name",
      "stories": [
        {{
          "title": "Story title",
          "role": "As a...",
          "action": "I want...",
          "value": "so that...",
          "priority": "High/Medium/Low",
          "story_points": 1-13,
          "acceptance_criteria": ["criterion 1", "criterion 2"],
          "source_components": ["component names involved"],
          "source_flows": ["flow labels involved"]
        }}
      ]
    }}
  ]
}}"""


class BaseAIProvider(ABC):
    @abstractmethod
    async def analyze_image(self, image: bytes, prompt: str) -> dict:
        """Send image to vision model, return parsed JSON response."""
        ...

    @abstractmethod
    async def generate_text(self, prompt: str, system: str | None = None) -> str:
        """Send text prompt to language model."""
        ...

    async def extract_components(self, image: bytes) -> list[Component]:
        """Extract components and flows from a diagram image."""
        import json, uuid
        response = await self.analyze_image(image, EXTRACTION_PROMPT)
        components = []
        for item in response.get("components", []):
            comp = Component(
                id=uuid.uuid4().hex[:8],
                name=item.get("name", "Unknown"),
                component_type=item.get("type", "unknown"),
                description=item.get("description", ""),
                position=tuple(item.get("position", [None, None])) if item.get("position") else None,
                source="ai_extraction",
            )
            components.append(comp)
        return components

    async def generate_stories(
        self,
        components: list[Component],
        flows: list[DataFlow],
    ) -> list[UserStory]:
        """Generate user stories from components and flows."""
        import json
        components_text = "\n".join(
            f"- {c.name} ({c.component_type}): {c.description}" for c in components
        )
        flows_text = "\n".join(
            f"- {f.source_id} → {f.target_id}" + (f" [{f.label}]" if f.label else "")
            for f in flows
        )
        prompt = STORY_GENERATION_PROMPT.format(
            components_text=components_text,
            flows_text=flows_text,
        )
        response = await self.generate_text(prompt)
        return self._parse_stories_response(response, components, flows)

    def _parse_stories_response(
        self,
        response: str,
        components: list[Component],
        flows: list[DataFlow],
    ) -> list[UserStory]:
        import json, re
        stories = []
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return []
        
        for epic_data in data.get("epics", []):
            epic_name = epic_data.get("name", "General")
            for story_data in epic_data.get("stories", []):
                role = story_data.get("role", "")
                action = story_data.get("action", "")
                value = story_data.get("value", "")
                if role.startswith("As a"): role = role.replace("**As a** ", "").replace("**As a**", "")
                if action.startswith("I want"): action = action.replace("**I want** ", "").replace("**I want**", "")
                if value.startswith("so that"): value = value.replace("**so that** ", "").replace("**so that**", "")
                story = UserStory.make(
                    epic=epic_name,
                    title=story_data.get("title", "Untitled"),
                    role=role,
                    action=action,
                    value=value,
                    priority=story_data.get("priority", "Medium"),
                )
                story.story_points = story_data.get("story_points")
                for crit in story_data.get("acceptance_criteria", []):
                    from app.models.story import AcceptanceCriterion
                    story.acceptance_criteria.append(
                        AcceptanceCriterion.make(crit)
                    )
                stories.append(story)
        return stories
