import json
from typing import Any, Literal

from pydantic import BaseModel, Field
from strands import tool

ARCHITECTURE_SYNTHESIS_PROMPT = """You are an expert software architect.
Given user stories, synthesize a complete architecture by identifying:
- Services/components needed to fulfill the stories
- Databases, caches, queues
- APIs and their connections
- External systems

For each inferred component, specify:
- name: descriptive name (e.g., "UserService", "PostgreSQL", "Redis Cache")
- type: one of: database, api, service, queue, storage, load_balancer, cache, gateway, client, user, external, unknown
- description: what this component does in the system

For connections between components:
- source: component name that initiates the connection
- target: component name that receives
- label: protocol or data being exchanged (e.g., "REST API", "gRPC", "SQL queries", "Pub/Sub events")
- type: one of: data, api_call, event, async, sync

Return as structured JSON with components and flows arrays."""

DIAGRAM_RENDER_PROMPT = """You are an expert at rendering architecture diagrams in Mermaid syntax.

Given components and data flows, generate a Mermaid C4Context or flow diagram that shows:
- All components with their types (using appropriate shapes)
- All connections between components
- Labels on connections showing protocol/data flow

Use Mermaid syntax like:
```mermaid
graph TD
    Client["Client<br/>Browser"]-->APIGateway["API Gateway"]
    APIGateway-->UserService["UserService"]
    UserService-->Database[("Database")]
```

Make sure to use appropriate shapes for different component types:
- People/users: rectangular with person icon styling
- External systems: external entity styling
- Databases: cylinder shape
- Services/APIs: rectangle/rounded rectangle
- Queues: oval/capsule

Return ONLY the raw Mermaid code without markdown code blocks."""

DRAWIO_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app">
  <diagram name="Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {cells}
      </mxGraphModel>
    </diagram>
  </diagram>
</mxfile>"""


class ParsedStory(BaseModel):
    role: str = Field(description="The user role (As a...)")
    action: str = Field(description="What they want to do (I want...)")
    value: str = Field(description="Why they want it (so that...)")
    title: str | None = Field(default=None, description="Story title")
    epic: str | None = Field(default=None, description="Epic grouping")
    priority: Literal["High", "Medium", "Low"] | None = Field(default=None)


class StoriesResponse(BaseModel):
    stories: list[ParsedStory]


class ComponentSchema(BaseModel):
    name: str = Field(description="Component name")
    type: str = Field(description="Component type")
    description: str = Field(description="Component description")


class FlowSchema(BaseModel):
    source: str = Field(description="Source component name")
    target: str = Field(description="Target component name")
    label: str | None = Field(default=None, description="Protocol or data exchanged")
    type: str = Field(description="Flow type: data, api_call, event, async, sync")


class ArchitectureResponse(BaseModel):
    components: list[ComponentSchema] = Field(description="Inferred components")
    flows: list[FlowSchema] = Field(description="Inferred data flows")


@tool
def parse_user_stories(raw_text: str, agent: Any) -> list[dict]:
    """Parse unstructured user story text into structured story objects.
    
    Handles formats:
    - "As a [role] I want [action] so that [value]"
    - JSON dicts with role/action/value/title fields
    
    Args:
        raw_text: Raw story text or JSON string
        agent: Agent instance for model access
    
    Returns:
        List of story dicts with role, action, value, title, epic, priority.
    """
    model = agent.model
    response = model.structured_output(
        StoriesResponse,
        prompt=f"""Parse the following user stories into structured format.

Stories to parse:
{raw_text}

Return a JSON object with a 'stories' array containing each parsed story.""",
    )
    return [s.model_dump() for s in response.stories]


@tool
def synthesize_architecture(stories: list[dict], agent: Any) -> dict:
    """Infer architecture components and data flows from user stories.
    
    Args:
        stories: List of story dicts from parse_user_stories
        agent: Agent instance for model access
    
    Returns:
        Dict with 'components' and 'flows' lists.
    """
    model = agent.model
    stories_text = json.dumps(stories, indent=2)
    
    response = model.structured_output(
        ArchitectureResponse,
        prompt=f"""{ARCHITECTURE_SYNTHESIS_PROMPT}

Stories to analyze:
{stories_text}

Return a JSON object with 'components' and 'flows' arrays.""",
    )
    
    return {
        "components": [c.model_dump() for c in response.components],
        "flows": [f.model_dump() for f in response.flows],
    }


@tool
def render_diagram(
    components: list[dict], flows: list[dict], format: str = "mermaid", agent: Any = None
) -> str:
    """Generate a visual architecture diagram from components and flows.
    
    Args:
        components: List of component dicts
        flows: List of flow dicts
        format: Output format - one of: svg, png, drawio, mermaid
        agent: Agent instance for model access
    
    Returns:
        Diagram string in the requested format.
    """
    model = agent.model if agent else None
    components_text = json.dumps(components, indent=2)
    flows_text = json.dumps(flows, indent=2)
    
    if format == "mermaid":
        response = model.invoke(
            f"""{DIAGRAM_RENDER_PROMPT}

Components:
{components_text}

Data Flows:
{flows_text}

Return ONLY the raw Mermaid code without any markdown formatting."""
        )
        return str(response.content)
    
    elif format in ("svg", "png"):
        mermaid_response = model.invoke(
            f"""{DIAGRAM_RENDER_PROMPT}

Components:
{components_text}

Data Flows:
{flows_text}

Return ONLY the raw Mermaid code without any markdown formatting."""
        )
        mermaid_code = str(mermaid_response.content)
        return _convert_mermaid_to_image(mermaid_code, format)
    
    elif format == "drawio":
        mermaid_response = model.invoke(
            f"""{DIAGRAM_RENDER_PROMPT}

Components:
{components_text}

Data Flows:
{flows_text}

Return ONLY the raw Mermaid code without any markdown formatting."""
        )
        mermaid_code = str(mermaid_response.content)
        return _mermaid_to_drawio(mermaid_code, components, flows)
    
    return ""


def _convert_mermaid_to_image(mermaid_code: str, format: str) -> str:
    """Convert Mermaid syntax to SVG or PNG using mermaid-cli.
    
    This requires the @mermaid-js/mermaid-cli npm package to be installed.
    Falls back to returning the mermaid code if conversion fails.
    """
    import subprocess
    import tempfile
    import os
    
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_code)
            mmd_path = f.name
        
        output_path = mmd_path.replace(".mmd", f".{format}")
        
        result = subprocess.run(
            ["mmdc", "-i", mmd_path, "-o", output_path, "-b", "transparent"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            with open(output_path, "rb") as f:
                content = f.read()
            
            os.unlink(mmd_path)
            os.unlink(output_path)
            
            if format == "svg":
                return content.decode("utf-8")
            else:
                import base64
                return base64.b64encode(content).decode("utf-8")
        else:
            return mermaid_code
            
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return mermaid_code


def _mermaid_to_drawio(mermaid_code: str, components: list[dict], flows: list[dict]) -> str:
    """Convert Mermaid syntax to DrawIO XML format."""
    cells = []
    y_offset = 60
    x_offset = 60
    component_positions = {}
    
    for i, comp in enumerate(components):
        comp_id = f"comp_{i}"
        name = comp.get("name", "Unknown")
        comp_type = comp.get("type", "unknown")
        description = comp.get("description", "")
        
        x = x_offset + (i % 4) * 200
        y = y_offset + (i // 4) * 120
        
        component_positions[name] = comp_id
        
        if comp_type == "database":
            shape = "shape=cylinder3;whiteSpace=wrap;html=1;boundedL=1;h=40;flipH=0;size=20"
            cell_id = f"        <mxCell id=\"{comp_id}\" value=\"{name}\\n{description}\" style=\"{shape}\" vertex=\"1\" parent=\"1\">\n          <mxGeometry x=\"{x}\" y=\"{y}\" width=\"120\" height=\"80\" as=\"geometry\"/>\n        </mxCell>"
        elif comp_type in ("api", "service"):
            cell_id = f"        <mxCell id=\"{comp_id}\" value=\"{name}\\n{description}\" style=\"rounded=1;whiteSpace=wrap;html=1\" vertex=\"1\" parent=\"1\">\n          <mxGeometry x=\"{x}\" y=\"{y}\" width=\"120\" height=\"60\" as=\"geometry\"/>\n        </mxCell>"
        elif comp_type in ("client", "user"):
            cell_id = f"        <mxCell id=\"{comp_id}\" value=\"{name}\" style=\"shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0\" vertex=\"1\" parent=\"1\">\n          <mxGeometry x=\"{x}\" y=\"{y}\" width=\"40\" height=\"80\" as=\"geometry\"/>\n        </mxCell>"
        elif comp_type == "external":
            cell_id = f"        <mxCell id=\"{comp_id}\" value=\"{name}\\n{description}\" style=\"rounded=0;whiteSpace=wrap;html=1;dashed=1\" vertex=\"1\" parent=\"1\">\n          <mxGeometry x=\"{x}\" y=\"{y}\" width=\"120\" height=\"60\" as=\"geometry\"/>\n        </mxCell>"
        elif comp_type == "queue":
            cell_id = f"        <mxCell id=\"{comp_id}\" value=\"{name}\" style=\"ellipse;whiteSpace=wrap;html=1\" vertex=\"1\" parent=\"1\">\n          <mxGeometry x=\"{x}\" y=\"{y}\" width=\"100\" height=\"50\" as=\"geometry\"/>\n        </mxCell>"
        else:
            cell_id = f"        <mxCell id=\"{comp_id}\" value=\"{name}\\n{description}\" style=\"rounded=1;whiteSpace=wrap;html=1\" vertex=\"1\" parent=\"1\">\n          <mxGeometry x=\"{x}\" y=\"{y}\" width=\"120\" height=\"60\" as=\"geometry\"/>\n        </mxCell>"
        
        cells.append(cell_id)
    
    for i, flow in enumerate(flows):
        source = flow.get("source", "")
        target = flow.get("target", "")
        label = flow.get("label", "")
        
        flow_id = f"flow_{i}"
        
        source_pos = component_positions.get(source)
        target_pos = component_positions.get(target)
        
        source_id = component_positions.get(source, "comp_0")
        target_id = component_positions.get(target, "comp_0")
        edge = f"        <mxCell id=\"{flow_id}\" value=\"{label}\" style=\"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0\" edge=\"1\" parent=\"1\" source=\"{source_id}\" target=\"{target_id}\">\n          <mxGeometry relative=\"1\" as=\"geometry\"/>\n        </mxCell>"
        cells.append(edge)
    
    cells_str = "\n".join(cells)
    return DRAWIO_TEMPLATE.format(cells=cells_str)
