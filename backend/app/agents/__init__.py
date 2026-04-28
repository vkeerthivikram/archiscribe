from strands import Agent
from app.agents.models import create_model, PROVIDER_MAP
from app.agents.router_agent import create_router_agent

def get_router_agent(provider_id: str | None = None) -> Agent:
    model = create_model(provider_id)
    return create_router_agent(model)

__all__ = ["create_model", "PROVIDER_MAP", "get_router_agent", "create_router_agent"]
