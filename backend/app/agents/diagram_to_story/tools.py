import base64
import json
import uuid
from typing import Any

from pydantic import BaseModel, Field
from strands import tool

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


class ComponentSchema(BaseModel):
    name: str = Field(description="Component name")
    type: str = Field(description="Component type")
    description: str = Field(description="Component description")
    position: list | None = Field(default=None, description="x,y coordinates")


class FlowSchema(BaseModel):
    source: str = Field(description="Source component name or ID")
    target: str = Field(description="Target component name or ID")
    label: str | None = Field(default=None, description="Text label on the connection")
    type: str = Field(description="Flow type: data, api_call, event, async, sync")


class ExtractionResponse(BaseModel):
    components: list[ComponentSchema] = Field(description="Extracted components")
    flows: list[FlowSchema] = Field(description="Extracted data flows")


class StorySchema(BaseModel):
    title: str = Field(description="Story title")
    role: str = Field(description="As a role")
    action: str = Field(description="I want action")
    value: str = Field(description="so that value")
    priority: str = Field(description="High/Medium/Low")
    story_points: int = Field(description="Story points 1-13")
    acceptance_criteria: list[str] = Field(description="Acceptance criteria")
    source_components: list[str] = Field(description="Component names involved")
    source_flows: list[str] = Field(description="Flow labels involved")


class EpicSchema(BaseModel):
    name: str = Field(description="Epic name")
    stories: list[StorySchema] = Field(description="Stories in this epic")


class StoriesResponse(BaseModel):
    epics: list[EpicSchema] = Field(description="Epics with stories")


class AcceptanceCriterionSchema(BaseModel):
    description: str = Field(description="Acceptance criterion description")
    is_testable: bool = Field(description="Whether criterion is testable")


class AcceptanceCriteriaResponse(BaseModel):
    criteria: list[AcceptanceCriterionSchema] = Field(description="Acceptance criteria")


@tool
def extract_components(image_bytes: bytes, agent: Any) -> list[dict]:
    """Extract architectural components from a diagram image.
    
    Args:
        image_bytes: Raw bytes of the diagram image (PNG, JPG, SVG, etc.)
    
    Returns:
        List of component dicts with name, type, description, position.
    """
    model = agent.model
    b64 = base64.b64encode(image_bytes).decode()
    response = model.structured_output(
        ExtractionResponse,
        prompt=f"{EXTRACTION_PROMPT}\n\nImage: data:image/png;base64,{b64}",
    )
    return [c.model_dump() for c in response.components]


@tool
def identify_flows(image_bytes: bytes, agent: Any) -> list[dict]:
    """Extract data flows and connections from a diagram image.
    
    Args:
        image_bytes: Raw bytes of the diagram image
    
    Returns:
        List of flow dicts with source, target, label, type.
    """
    model = agent.model
    b64 = base64.b64encode(image_bytes).decode()
    response = model.structured_output(
        ExtractionResponse,
        prompt=f"{EXTRACTION_PROMPT}\n\nImage: data:image/png;base64,{b64}",
    )
    return [f.model_dump() for f in response.flows]


@tool
def generate_stories(components: list[dict], flows: list[dict], agent: Any) -> list[dict]:
    """Generate user stories from components and data flows.
    
    Args:
        components: List of component dicts from extract_components
        flows: List of flow dicts from identify_flows
    
    Returns:
        List of story dicts with epic, title, role, action, value, priority, etc.
    """
    model = agent.model
    components_text = json.dumps(components, indent=2)
    flows_text = json.dumps(flows, indent=2)
    
    response = model.structured_output(
        StoriesResponse,
        prompt=STORY_GENERATION_PROMPT.format(
            components_text=components_text,
            flows_text=flows_text,
        ),
    )
    
    result = []
    for epic in response.epics:
        for story in epic.stories:
            story_dict = story.model_dump()
            story_dict["epic"] = epic.name
            result.append(story_dict)
    return result


@tool
def generate_acceptance_criteria(
    story: dict, components: list[dict], agent: Any
) -> list[dict]:
    """Generate testable acceptance criteria for a user story.
    
    Args:
        story: Story dict from generate_stories
        components: List of component dicts related to this story
    
    Returns:
        List of acceptance criterion dicts with description.
    """
    model = agent.model
    prompt = f"""Generate detailed, testable acceptance criteria for this user story:

Story: {story.get('title', 'Untitled')}
Role: {story.get('role', 'Unknown')}
Action: {story.get('action', 'Unknown')}
Value: {story.get('value', 'Unknown')}
Priority: {story.get('priority', 'Medium')}

Related Components:
{json.dumps(components, indent=2)}

Generate specific, measurable acceptance criteria that a developer or QA engineer could use to verify the story is complete.
Each criterion should be testable (can be verified as pass/fail).
Return as JSON array of criterion objects with 'description' and 'is_testable' fields."""

    response = model.structured_output(
        AcceptanceCriteriaResponse,
        prompt=prompt,
    )
    return [c.model_dump() for c in response.criteria]
