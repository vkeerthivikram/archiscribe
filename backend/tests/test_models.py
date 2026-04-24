import pytest
from app.models import Component, DataFlow, UserStory, AcceptanceCriterion


def test_component_creation():
    c = Component(
        id="comp-1",
        name="PostgreSQL",
        component_type="database",
        description="Primary data store",
        position=(100, 200),
    )
    assert c.id == "comp-1"
    assert c.name == "PostgreSQL"
    assert c.component_type == "database"
    assert c.status == "pending"


def test_dataflow_creation():
    f = DataFlow(
        id="flow-1",
        source_id="client-1",
        target_id="db-1",
        label="SQL queries",
        flow_type="api_call",
        protocol="TCP",
    )
    assert f.source_id == "client-1"
    assert f.target_id == "db-1"


def test_userstory_make():
    story = UserStory.make(
        epic="Data Storage",
        title="Persist user data",
        role="system architect",
        action="store data in PostgreSQL",
        value="data is reliably saved",
        priority="High",
    )
    assert story.epic == "Data Storage"
    assert story.priority == "High"
    assert story.acceptance_criteria == []


def test_acceptance_criterion_make():
    ac = AcceptanceCriterion.make("Database connection is pooled")
    assert ac.id != ""
    assert ac.description == "Database connection is pooled"
    assert ac.is_testable is True