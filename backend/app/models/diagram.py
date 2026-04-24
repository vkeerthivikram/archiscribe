from dataclasses import dataclass, field
from typing import Literal

ComponentType = Literal[
    "database", "api", "service", "queue", "storage",
    "load_balancer", "cache", "gateway", "client", "user",
    "external", "unknown"
]

FlowType = Literal["data", "api_call", "event", "async", "sync"]
Protocol = Literal["HTTP", "HTTPS", "gRPC", "AMQP", "MQTT", "TCP", "WebSocket", None]

ComponentStatus = Literal["pending", "confirmed", "renamed", "removed", "added"]


@dataclass
class Component:
    id: str
    name: str
    component_type: ComponentType
    description: str = ""
    position: tuple[int, int] | None = None
    properties: dict = field(default_factory=dict)
    source: str = ""
    status: ComponentStatus = "pending"


@dataclass
class DataFlow:
    id: str
    source_id: str
    target_id: str
    label: str | None = None
    flow_type: FlowType = "data"
    protocol: Protocol = None