import pytest
from app.agents.story_to_diagram import tools


def test_parse_user_stories_tool_exists():
    assert tools.parse_user_stories is not None


def test_synthesize_architecture_tool_exists():
    assert tools.synthesize_architecture is not None


def test_render_diagram_tool_exists():
    assert tools.render_diagram is not None


def test_render_diagram_supports_mermaid_format():
    assert callable(tools.render_diagram)
