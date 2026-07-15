"""Tests for HERMES workflow mutation operators."""

import pytest

from hermes.mutation.models import Workflow, WorkflowStep
from hermes.mutation.operators import WorkflowMutationOperators
from hermes.semantic.models import OperationType


def make_workflow() -> Workflow:
    return Workflow(
        workflow_id="checkout-flow",
        name="Checkout Flow",
        steps=(
            WorkflowStep(
                operation_type=OperationType.LOGIN,
                label="Login",
                source_state_id="home",
                target_state_id="products",
            ),
            WorkflowStep(
                operation_type=OperationType.ADD_TO_CART,
                label="Add to Cart",
                source_state_id="products",
                target_state_id="cart",
            ),
            WorkflowStep(
                operation_type=OperationType.CHECKOUT,
                label="Checkout",
                source_state_id="cart",
                target_state_id="success",
            ),
        ),
    )


def test_skip_step() -> None:
    mutated = WorkflowMutationOperators.skip_step(
        make_workflow(),
        1,
    )

    assert len(mutated) == 2
    assert mutated.steps[1].operation_type is OperationType.CHECKOUT
    assert mutated.metadata["mutation_type"] == "skip_step"


def test_duplicate_step() -> None:
    mutated = WorkflowMutationOperators.duplicate_step(
        make_workflow(),
        1,
    )

    assert len(mutated) == 4
    assert mutated.steps[1] == mutated.steps[2]


def test_swap_adjacent() -> None:
    mutated = WorkflowMutationOperators.swap_adjacent(
        make_workflow(),
        0,
    )

    assert mutated.steps[0].operation_type is OperationType.ADD_TO_CART
    assert mutated.steps[1].operation_type is OperationType.LOGIN


def test_reverse_workflow() -> None:
    mutated = WorkflowMutationOperators.reverse_workflow(
        make_workflow()
    )

    assert mutated.steps[0].operation_type is OperationType.CHECKOUT
    assert mutated.steps[-1].operation_type is OperationType.LOGIN


def test_insert_logout() -> None:
    mutated = WorkflowMutationOperators.insert_logout(
        make_workflow(),
        2,
    )

    assert len(mutated) == 4
    assert mutated.steps[2].operation_type is OperationType.LOGOUT
    assert mutated.steps[2].metadata["injected"] is True


@pytest.mark.parametrize(
    ("method", "index"),
    [
        (WorkflowMutationOperators.skip_step, -1),
        (WorkflowMutationOperators.skip_step, 3),
        (WorkflowMutationOperators.duplicate_step, 3),
        (WorkflowMutationOperators.swap_adjacent, 2),
        (WorkflowMutationOperators.insert_logout, 4),
    ],
)
def test_invalid_indices_are_rejected(
    method,
    index: int,
) -> None:
    with pytest.raises(IndexError):
        method(make_workflow(), index)
