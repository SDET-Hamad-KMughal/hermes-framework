"""Semantic-operation discovery for HERMES."""

from __future__ import annotations

from hermes.semantic.models import SemanticOperation
from hermes.semantic.rules import SemanticRuleClassifier
from hermes.state_graph.graph import StateGraph


class SemanticOperationDiscovery:
    """Discover business-level operations from graph transitions."""

    def __init__(
        self,
        classifier: SemanticRuleClassifier | None = None,
    ) -> None:
        self.classifier = classifier or SemanticRuleClassifier()

    def discover(
        self,
        graph: StateGraph,
    ) -> list[SemanticOperation]:
        """Discover semantic operations from all graph transitions."""

        operations: list[SemanticOperation] = []

        for transition in graph.transitions:
            source_state = graph.get_state(
                transition.source_state_id
            )
            target_state = graph.get_state(
                transition.target_state_id
            )

            result = self.classifier.classify(
                transition.label,
                transition.selector,
                transition.semantic_target,
            )

            operations.append(
                SemanticOperation(
                    operation_type=result.operation_type,
                    label=transition.label,
                    source_state_id=transition.source_state_id,
                    target_state_id=transition.target_state_id,
                    selector=transition.selector,
                    confidence=result.confidence,
                    evidence=result.evidence,
                    metadata={
                        "action_type": transition.action_type,
                        "semantic_target": transition.semantic_target,
                    },
                )
            )

        return operations
