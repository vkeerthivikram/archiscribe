from strands import Agent
from app.agents.diagram_to_story import tools

DIAGRAM_TO_STORY_SYSTEM_PROMPT = """You are an expert architect and product manager.
When given an architecture diagram image, extract all components and data flows,
then generate well-structured user stories grouped into epics.

Workflow:
1. Call extract_components(image_bytes=...) on the image
2. Call identify_flows(image_bytes=...) on the image
3. Call generate_stories(components=..., flows=...) with extracted data
4. Call generate_acceptance_criteria for each story

Return a summary of what you extracted and generated."""


def create_diagram_to_story_agent(model):
    return Agent(
        model=model,
        tools=[
            tools.extract_components,
            tools.identify_flows,
            tools.generate_stories,
            tools.generate_acceptance_criteria,
        ],
        system_prompt=DIAGRAM_TO_STORY_SYSTEM_PROMPT,
    )
