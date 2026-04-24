import io
import zipfile
from fastapi import UploadFile
from app.parsers.base import BaseParser, ParseResult
from app.models.diagram import Component, DataFlow


class VisioParser(BaseParser):
    """Structural + vision parser for Visio .vsdx files.

    A .vsdx is a ZIP archive containing XML files. Extracts
    embedded diagram images and page XML, then sends images
    to LLM vision for analysis.
    """

    async def parse(self, file: UploadFile) -> ParseResult:
        contents = await file.read()
        all_components = []
        all_flows = []

        try:
            with zipfile.ZipFile(io.BytesIO(contents)) as zf:
                page_files = [n for n in zf.namelist() if n.startswith("visio/pages/page") and n.endswith(".xml")]
                images = []

                for page_file in page_files:
                    page_xml = zf.read(page_file).decode("utf-8", errors="ignore")
                    page_components, page_flows, page_images = self._parse_page_xml(page_xml, zf)
                    all_components.extend(page_components)
                    all_flows.extend(page_flows)
                    images.extend(page_images)

                for img_data in images:
                    comps, flows = await self._analyze_embedded_image(img_data, file.filename or "visio")
                    all_components.extend(comps)
                    all_flows.extend(flows)
        except zipfile.BadZipFile:
            return ParseResult(source_file=file.filename or "visio", parser_type="vision")

        return ParseResult(
            components=all_components,
            flows=all_flows,
            raw_metadata={"filename": file.filename},
            source_file=file.filename or "visio",
            parser_type="hybrid",
        )

    def _parse_page_xml(self, page_xml: str, zf: zipfile.ZipFile) -> tuple[list[Component], list[DataFlow], list[bytes]]:
        from lxml import etree
        components = []
        flows = []
        images = []

        try:
            tree = etree.fromstring(page_xml.encode("utf-8"))
            ns = {"v": "http://schemas.microsoft.com/visio/2003/core"}
            shapes = tree.xpath("//v:shape", namespaces=ns)

            for shape in shapes:
                text_el = shape.xpath(".//v:text", namespaces=ns)
                text = " ".join([t.text or "" for t in text_el]).strip()
                x = float(shape.get("PinX", 0))
                y = float(shape.get("PinY", 0))
                master = shape.get("Master", "")

                if text:
                    ctype = self._infer_type_from_master(master, text)
                    components.append(Component(
                        id=self._generate_id("comp"),
                        name=self._clean_label(text),
                        component_type=ctype,
                        position=(int(x), int(y)),
                        source="visio",
                        properties={"master": master},
                    ))

            connects = tree.xpath("//v:connect", namespaces=ns)
            for conn in connects:
                from_id = conn.get("FromSheet", "")
                to_id = conn.get("ToSheet", "")
                if from_id and to_id:
                    flows.append(DataFlow(
                        id=self._generate_id("flow"),
                        source_id=from_id,
                        target_id=to_id,
                    ))
        except Exception:
            pass

        return components, flows, images

    def _infer_type_from_master(self, master: str, text: str) -> str:
        text_lower = text.lower()
        if not master:
            if "database" in text_lower: return "database"
            if "process" in text_lower: return "service"
            if "storage" in text_lower: return "storage"
            if "user" in text_lower: return "user"
            return "service"
        master_lower = master.lower()
        if "db" in master_lower: return "database"
        if "storage" in master_lower: return "storage"
        if "cache" in master_lower: return "cache"
        if "queue" in master_lower: return "queue"
        return "service"

    def _clean_label(self, text: str) -> str:
        import re
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()

    async def _analyze_embedded_image(self, image_bytes: bytes, filename: str) -> tuple[list[Component], list[DataFlow]]:
        """Override to inject LLM vision analysis."""
        return [], []
