"""Tests for HERMES workflow-mutation models."""

import pytest

from hermes.mutation.models import MutationType, Workflow, WorkflowStep
from hermes.semantic.models import OperationType


def test_create_workflow_step() -> None:
    step = WorkflowStep(
        operation_type=OperationType.LOGIN,
        label="Sign In",
        source_state_id="home",
        target_state_id="dashboard",
        selector="#login",
    )

    assert step.operation_type is OperationType.LOGIN
    assert step.target_state_id == "dashboard"


def test_workflow_step_serialization() -> None:
    step = WorkflowStep(
        operation_type=OperationType.ADD_TO_CART,
        label="Add to Cart",
        source_state_id="product",
    )

    data = step.to_dict()

    assert data["operation_type"] == "add_to_cart"
    assert data["label"] == "Add to Cart"


def test_create_workflow() -> None:
    workflow = Workflow(
        workflow_id="checkout-flow",
        name="Checkout Flow",
        steps=(
            WorkflowStep(
                operation_type=OperationType.LOGIN,
                label="Login",
                source_state_id="home",
            ),
            WorkflowStep(
                operation_type=OperationType.CHECKOUT,
                label="Checkout",
                source_state_id="cart",
            ),
        ),
    )

    assert len(workflow) == 2
    assert workflow.steps[0].operation_type is OperationType.LOGIN


def test_workflow_serialization() -> None:
    workflow = Workflow(
        workflow_id="flow-1",
        name="Simple Flow",
        steps=(),
        metadata={"source": "test"},
    )

    data = workflow.to_dict()

    assert data["workflow_id"] == "flow-1"
    assert data["steps"] == []
    assert data["metadata"]["source"] == "test"


@pytest.mark.parametrize(
    ("workflow_id", "name", "message"),
    [
        ("", "Flow", "workflow_id must not be empty"),
        ("flow-1", "", "name must not be empty"),
    ],
)
def test_invalid_workflow_is_rejected(
    workflow_id: str,
    name: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        Workflow(
            workflow_id=workflow_id,
            name=name,
            steps=(),
        )


def test_empty_step_source_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="source_state_id must not be empty",
    ):
        WorkflowStep(
            operation_type=OperationType.UNKNOWN,
            label="Unknown",
            source_state_id="",
        )


def test_mutation_types_are_stable() -> None:
    assert MutationType.SKIP_STEP.value == "skip_step"
    assert MutationType.SWITCH_IDENTITY.value == "switch_identity"
