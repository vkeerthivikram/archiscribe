import pytest
from unittest.mock import MagicMock
from app.agents.router_agent import create_router_agent, ROUTER_SYSTEM_PROMPT

def test_router_agent_has_correct_system_prompt():
    assert "diagram_to_story_agent" in ROUTER_SYSTEM_PROMPT
    assert "story_to_diagram_agent" in ROUTER_SYSTEM_PROMPT
    assert "routing coordinator" in ROUTER_SYSTEM_PROMPT

def test_create_router_agent_returns_agent():
    mock_model = MagicMock()
    mock_model.config = {"model_id": "test"}
    agent = create_router_agent(mock_model)
    assert agent is not None

def test_router_agent_has_two_tools():
    mock_model = MagicMock()
    mock_model.config = {"model_id": "test"}
    agent = create_router_agent(mock_model)
    assert len(agent.tool_names) == 2
    assert "diagram_to_story_agent" in agent.tool_names
    assert "story_to_diagram_agent" in agent.tool_names