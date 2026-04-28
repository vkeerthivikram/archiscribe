import pytest
from app.agents.diagram_to_story import tools


def test_extract_components_tool_exists():
    assert tools.extract_components is not None


def test_identify_flows_tool_exists():
    assert tools.identify_flows is not None


def test_generate_stories_tool_exists():
    assert tools.generate_stories is not None


def test_generate_acceptance_criteria_tool_exists():
    assert tools.generate_acceptance_criteria is not None
