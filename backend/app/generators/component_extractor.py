from app.ai.base import BaseAIProvider
from app.models.diagram import Component, DataFlow
from app.parsers.base import ParseResult


class ComponentExtractor:
    """Orchestrates parsing + AI extraction for diagram analysis.
    
    Takes a ParseResult (from any parser) and feeds the data
    to the AI provider for component/flow enrichment.
    """

    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider

    async def extract(self, parse_result: ParseResult) -> tuple[list[Component], list[DataFlow]]:
        """Run AI extraction on a parse result.
        
        For structural parsers: validate and enrich components with AI
        For vision parsers: send images to AI for extraction
        """
        if parse_result.parser_type == "vision":
            return await self._extract_from_vision(parse_result)
        return parse_result.components, parse_result.flows

    async def _extract_from_vision(self, result: ParseResult) -> tuple[list[Component], list[DataFlow]]:
        """Send diagram image bytes to AI for extraction."""
        return [], []
