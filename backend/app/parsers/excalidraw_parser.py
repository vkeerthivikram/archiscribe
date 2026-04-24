import json
from fastapi import UploadFile
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class ExcalidrawParser(BaseParser):
    """Structural parser for Excalidraw JSON format.

    Parses the JSON to extract elements (rectangles, diamonds, etc.),
    their labels, and arrow connections.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        data = json.loads(contents)
        components, flows = self._extract_elements(data)
        return ParseResult(
            components=components,
            flows=flows,
            raw_metadata={"filename": file.filename},
            source_file=file.filename or "excalidraw",
            parser_type="structural",
        )

    def _extract_elements(self, data: dict) -> tuple[list[Component], list[DataFlow]]:
        components = []
        flows = []
        elements = data.get("elements", [])

        for el in elements:
            el_id = el.get("id", "")
            el_type = el.get("type", "")
            text = el.get("text", "") or ""
            if isinstance(text, dict):
                text = text.get("text", "")

            x = el.get("x", 0)
            y = el.get("y", 0)

            if el_type == "arrow":
                start_binding = el.get("startBinding", {}) or {}
                end_binding = el.get("endBinding", {}) or {}
                source_id = start_binding.get("elementId", "") if isinstance(start_binding, dict) else ""
                target_id = end_binding.get("elementId", "") if isinstance(end_binding, dict) else ""

                if source_id and target_id:
                    flows.append(DataFlow(
                        id=self._generate_id("flow"),
                        source_id=source_id,
                        target_id=target_id,
                        label=text or None,
                        flow_type="data",
                    ))
            elif el_type in ("rectangle", "diamond", "ellipse", "text"):
                ctype = self._infer_type(el_type, text)
                components.append(Component(
                    id=el_id,
                    name=self._clean_label(text) or f"Element-{el_id[:8]}",
                    component_type=ctype,
                    description=f"Excalidraw {el_type}",
                    position=(int(x), int(y)),
                    source="excalidraw",
                    properties={"el_type": el_type},
                ))

        return components, flows

    def _infer_type(self, el_type: str, text: str) -> str:
        text_lower = text.lower()
        if el_type == "diamond":
            return "gateway"
        if "database" in text_lower or "db" in text_lower:
            return "database"
        if "queue" in text_lower:
            return "queue"
        if "storage" in text_lower or "bucket" in text_lower:
            return "storage"
        if "cache" in text_lower or "redis" in text_lower:
            return "cache"
        if "load" in text_lower:
            return "load_balancer"
        if "api" in text_lower:
            return "api"
        if "user" in text_lower or "actor" in text_lower:
            return "user"
        if "service" in text_lower or "microservice" in text_lower:
            return "service"
        if "external" in text_lower:
            return "external"
        return "service"

    def _clean_label(self, text: str) -> str:
        if not text:
            return ""
        import re
        text = re.sub(r"<[^>]+>", "", str(text))
        return text.strip()
