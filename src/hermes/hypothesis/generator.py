"""Workflow hypothesis generation for HERMES."""

from __future__ import annotations

from hermes.hypothesis.models import WorkflowHypothesis
from hermes.hypothesis.templates import (
    DEFAULT_TEMPLATES,
    HypothesisTemplate,
)
from hermes.mutation.models import Workflow


class HypothesisGenerator:
    """Generate applicable hypotheses for semantic workflows."""

    def __init__(
        self,
        templates: tuple[HypothesisTemplate, ...] | None = None,
    ) -> None:
        self.templates = templates or DEFAULT_TEMPLATES

    def generate(
        self,
        workflow: Workflow,
    ) -> list[WorkflowHypothesis]:
        """Generate hypotheses applicable to one workflow."""

        operation_names = [
            step.operation_type.value
            for step in workflow.steps
        ]

        hypotheses = []

        for template in self.templates:
            if not self._is_applicable(
                template,
                operation_names,
            ):
                continue

            hypotheses.append(
                template.instantiate(
                    hypothesis_id=(
                        f"H{len(hypotheses) + 1:03d}"
                    ),
                    source_workflow_id=workflow.workflow_id,
                )
            )

        return hypotheses

    @staticmethod
    def _is_applicable(
        template: HypothesisTemplate,
        operation_names: list[str],
    ) -> bool:
        if template.target_operation not in operation_names:
            return False

        prerequisite = template.prerequisite_operation

        if prerequisite is None:
            return True

        return prerequisite in operation_names
