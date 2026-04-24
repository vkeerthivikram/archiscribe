from app.models.diagram import Component, DataFlow, ComponentType
from app.models.story import AcceptanceCriterion


CRITERIA_TEMPLATES: dict[ComponentType, list[str]] = {
    "database": [
        "Database schema supports all required entity types",
        "Connection pooling is configured with appropriate pool size",
        "Migration scripts are versioned and reversible",
        "Backup and restore procedures are documented",
    ],
    "api": [
        "API endpoints respond within acceptable latency thresholds",
        "API versioning strategy is defined",
        "Request/response schemas are documented",
        "Authentication and authorization are enforced",
    ],
    "service": [
        "Service health check endpoint is exposed",
        "Service can be scaled horizontally",
        "Service logs are structured and centralized",
        "Service registers with service discovery",
    ],
    "storage": [
        "Storage bucket has appropriate access policies",
        "Data retention policy is defined and enforced",
        "Storage costs are monitored and optimized",
    ],
    "cache": [
        "Cache invalidation strategy is defined",
        "Cache TTL values are appropriate for use case",
        "Cache hit rate meets performance requirements",
    ],
    "load_balancer": [
        "Load balancer health checks are configured",
        "Traffic distribution algorithm is appropriate",
        "SSL termination is handled correctly",
    ],
    "queue": [
        "Message durability is configured",
        "Dead letter queue handles failed messages",
        "Consumer groups are properly scaled",
    ],
    "gateway": [
        "Rate limiting is configured appropriately",
        "Request routing rules are documented",
        "Gateway logs all traffic for auditing",
    ],
}


class AcceptanceCriteriaGenerator:
    """Generates testable acceptance criteria from components."""

    def generate_for_component(self, component: Component) -> list[AcceptanceCriterion]:
        """Generate ACs based on component type."""
        from app.models.story import AcceptanceCriterion
        templates = CRITERIA_TEMPLATES.get(component.component_type, [])
        return [AcceptanceCriterion.make(tmpl.format(name=component.name)) for tmpl in templates]

    def generate_for_story(
        self,
        story_components: list[Component],
        story_flows: list[DataFlow],
    ) -> list[AcceptanceCriterion]:
        """Generate ACs covering all components and flows in a story."""
        criteria = []
        for comp in story_components:
            criteria.extend(self.generate_for_component(comp))
        return criteria
