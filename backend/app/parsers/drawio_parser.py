from fastapi import UploadFile
from lxml import etree
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class DrawioParser(BaseParser):
    """Structural parser for Draw.io XML format.

    Parses the XML to extract mxCell elements (nodes/edges),
    their labels, styles, and connection geometry.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        tree = etree.fromstring(contents)
        source = file.filename or "drawio"
        components, flows = self._extract_elements(tree, source)
        return ParseResult(
            components=components,
            flows=flows,
            raw_metadata={"filename": file.filename},
            source_file=source,
            parser_type="structural",
        )

    def _extract_elements(self, tree, source: str) -> tuple[list[Component], list[DataFlow]]:
        components = []
        flows = []
        cells = tree.xpath("//mxCell")
        for cell in cells:
            cell_id = cell.get("id", "")
            parent_id = cell.get("parent", "")
            style = cell.get("style", "")
            value = cell.get("value", "") or ""

            if self._is_edge(style, cell.get("edge")):
                source_id = cell.get("source", "")
                target_id = cell.get("target", "")
                if source_id and target_id:
                    flows.append(DataFlow(
                        id=self._generate_id("flow"),
                        source_id=source_id,
                        target_id=target_id,
                        label=value if value else None,
                        flow_type=self._infer_flow_type(style),
                    ))
            elif parent_id not in ("0", None) and value:
                ctype = self._infer_component_type(style, value)
                geo = cell.find("mxGeometry")
                x, y = self._get_position(geo)
                components.append(Component(
                    id=cell_id,
                    name=self._clean_label(value),
                    component_type=ctype,
                    description=f"Draw.io cell: {value}",
                    position=(x, y) if x and y else None,
                    source=source,
                    properties={"style": style},
                ))
        return components, flows

    def _is_edge(self, style: str, edge_attr: str | None = None) -> bool:
        return edge_attr == "1" or "endArrow" in style or "edge" in style

    def _infer_component_type(self, style: str, label: str) -> str:
        label_lower = label.lower()
        if "database" in style or "db" in label_lower:
            return "database"
        if "queue" in style or "mq" in label_lower:
            return "queue"
        if "cloud" in style or "aws" in label_lower or "azure" in label_lower:
            return "storage"
        if "load" in style or "lb" in label_lower:
            return "load_balancer"
        if "cache" in style or "redis" in label_lower:
            return "cache"
        if "api" in label_lower or "gateway" in style:
            return "api"
        if "user" in label_lower or "actor" in label_lower:
            return "user"
        if "storage" in style or "s3" in label_lower:
            return "storage"
        return "service"

    def _infer_flow_type(self, style: str) -> str:
        if "dashed" in style:
            return "async"
        if "edgeStyle=orthogonal" in style:
            return "api_call"
        return "data"

    def _get_position(self, geo) -> tuple[int | None, int | None]:
        if geo is None:
            return None, None
        x = geo.get("x")
        y = geo.get("y")
        return int(x) if x else None, int(y) if y else None

    def _clean_label(self, label: str) -> str:
        import re
        label = re.sub(r"<[^>]+>", "", label)
        return label.strip()
