from strands import Agent
from app.agents.diagram_to_story.agent import create_diagram_to_story_agent
from app.agents.story_to_diagram.agent import create_story_to_diagram_agent

ROUTER_SYSTEM_PROMPT = """You are a routing coordinator for ArchiScribe.
Given user input, determine which specialist to invoke:

- If the input contains or references an architecture diagram/image → use diagram_to_story_agent
- If the input contains user stories or requirements → use story_to_diagram_agent
- If unclear, ask the user to clarify

Always delegate to exactly one specialist agent. Do not attempt to solve the request yourself."""

def create_router_agent(model):
    diagram_agent = create_diagram_to_story_agent(model)
    story_agent = create_story_to_diagram_agent(model)

    return Agent(
        model=model,
        tools=[
            diagram_agent.as_tool(name="diagram_to_story_agent"),
            story_agent.as_tool(name="story_to_diagram_agent"),
        ],
        system_prompt=ROUTER_SYSTEM_PROMPT,
    )