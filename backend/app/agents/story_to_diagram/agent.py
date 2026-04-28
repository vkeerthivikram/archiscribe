from strands import Agent
from app.agents.story_to_diagram import tools

STORY_TO_DIAGRAM_SYSTEM_PROMPT = """You are an expert software architect.
When given user stories or requirements, synthesize a complete architecture:
identify services, databases, APIs, queues, and their connections.

IMPORTANT: When calling tools that need the model, pass model=agent.

Workflow:
1. Call parse_user_stories(raw_text=...) to structure the input
2. Call synthesize_architecture(stories=...) to infer components and flows
3. Call render_diagram(components=..., flows=..., format="mermaid") to generate the diagram

If the user requests a specific format (svg, png, drawio), pass format="svg" etc to render_diagram.

Return a summary of what you inferred and the diagram."""


def create_story_to_diagram_agent(model):
    return Agent(
        model=model,
        tools=[
            tools.parse_user_stories,
            tools.synthesize_architecture,
            tools.render_diagram,
        ],
        system_prompt=STORY_TO_DIAGRAM_SYSTEM_PROMPT,
    )
