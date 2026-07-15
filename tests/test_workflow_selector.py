"""Tests for generated-workflow selection."""

import pytest

from hermes.mutation.models import Workflow, WorkflowStep
from hermes.semantic.models import OperationType
from hermes.workflow_generator.models import GeneratedWorkflow
from hermes.workflow_generator.selector import (
    WorkflowSelectionConfig,
    WorkflowSelector,
)


def make_generated(
    workflow_id: str,
    operation_types: tuple[OperationType, ...],
) -> GeneratedWorkflow:
    steps = tuple(
        WorkflowStep(
            operation_type=operation_type,
            label=operation_type.value,
            source_state_id=f"state-{index}",
            target_state_id=f"state-{index + 1}",
        )
        for index, operation_type in enumerate(
            operation_types
        )
    )

    workflow = Workflow(
        workflow_id=workflow_id,
        name=workflow_id,
        steps=steps,
    )

    state_path = tuple(
        f"state-{index}"
        for index in range(len(steps) + 1)
    )

    return GeneratedWorkflow(
        workflow=workflow,
        state_path=state_path,
        operation_count=len(steps),
        terminal_state_id=state_path[-1],
    )


def test_selector_prefers_business_workflows() -> None:
    workflows = [
        make_generated(
            "search-only",
            (OperationType.SEARCH,),
        ),
        make_generated(
            "checkout",
            (
                OperationType.LOGIN,
                OperationType.ADD_TO_CART,
                OperationType.CHECKOUT,
            ),
        ),
    ]

    selected = WorkflowSelector().select(workflows)

    assert len(selected) == 1
    assert selected[0].workflow.workflow_id == "checkout"


def test_selector_prefers_longer_workflows() -> None:
    workflows = [
        make_generated(
            "short",
            (OperationType.LOGIN,),
        ),
        make_generated(
            "long",
            (
                OperationType.LOGIN,
                OperationType.ADD_TO_CART,
                OperationType.CHECKOUT,
            ),
        ),
    ]

    selected = WorkflowSelector().select(workflows)

    assert selected[0].workflow.workflow_id == "long"


def test_selector_respects_limit() -> None:
    workflows = [
        make_generated(
            f"workflow-{index}",
            (OperationType.LOGIN,),
        )
        for index in range(5)
    ]

    selector = WorkflowSelector(
        WorkflowSelectionConfig(maximum_selected=2)
    )

    selected = selector.select(workflows)

    assert len(selected) == 2


def test_selector_can_allow_non_business_workflows() -> None:
    selector = WorkflowSelector(
        WorkflowSelectionConfig(
            require_business_operation=False
        )
    )

    selected = selector.select(
        [
            make_generated(
                "search",
                (OperationType.SEARCH,),
            )
        ]
    )

    assert len(selected) == 1


def test_selector_can_prefer_shorter_workflows() -> None:
    selector = WorkflowSelector(
        WorkflowSelectionConfig(
            prefer_longer_workflows=False
        )
    )

    workflows = [
        make_generated(
            "short",
            (OperationType.LOGIN,),
        ),
        make_generated(
            "long",
            (
                OperationType.LOGIN,
                OperationType.CHECKOUT,
            ),
        ),
    ]

    selected = selector.select(workflows)

    assert selected[0].workflow.workflow_id == "long"


def test_selector_handles_empty_input() -> None:
    assert WorkflowSelector().select([]) == []


def test_invalid_selection_limit() -> None:
    with pytest.raises(
        ValueError,
        match="maximum_selected must be at least 1",
    ):
        WorkflowSelectionConfig(maximum_selected=0)
