"""Tests for hypothesis-driven workflow mutation."""

import pytest

from hermes.hypothesis.models import (
    ExpectedBehavior,
    HypothesisCategory,
    WorkflowHypothesis,
)
from hermes.hypothesis.mutator import HypothesisMutator
from hermes.mutation.models import Workflow, WorkflowStep
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
                target_state_id="authenticated",
            ),
            WorkflowStep(
                operation_type=OperationType.ADD_TO_CART,
                label="Add to Cart",
                source_state_id="authenticated",
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


def make_hypothesis(
    *,
    strategy: str,
    target: str | None,
    prerequisite: str | None,
) -> WorkflowHypothesis:
    return WorkflowHypothesis(
        hypothesis_id="H001",
        title="Test Hypothesis",
        description="Test hypothesis description.",
        category=HypothesisCategory.STATE_DEPENDENCY,
        source_workflow_id="checkout-flow",
        mutation_strategy=strategy,
        expected_behavior=ExpectedBehavior.REJECT,
        target_operation=target,
        prerequisite_operation=prerequisite,
    )


def operation_values(workflow: Workflow) -> list[str]:
    return [
        step.operation_type.value
        for step in workflow.steps
    ]


def test_remove_prerequisite() -> None:
    hypothesis = make_hypothesis(
        strategy="remove_prerequisite",
        target="checkout",
        prerequisite="login",
    )

    mutated = HypothesisMutator().mutate(
        make_workflow(),
        hypothesis,
    )

    assert operation_values(mutated) == [
        "add_to_cart",
        "checkout",
    ]


def test_duplicate_operation() -> None:
    hypothesis = make_hypothesis(
        strategy="duplicate_operation",
        target="add_to_cart",
        prerequisite=None,
    )

    mutated = HypothesisMutator().mutate(
        make_workflow(),
        hypothesis,
    )

    assert operation_values(mutated) == [
        "login",
        "add_to_cart",
        "add_to_cart",
        "checkout",
    ]

    assert (
        mutated.steps[2].metadata["hypothesis_duplicate"]
        is True
    )


def test_swap_operations() -> None:
    hypothesis = make_hypothesis(
        strategy="swap_operations",
        target="checkout",
        prerequisite="add_to_cart",
    )

    mutated = HypothesisMutator().mutate(
        make_workflow(),
        hypothesis,
    )

    assert operation_values(mutated) == [
        "login",
        "checkout",
        "add_to_cart",
    ]


def test_mutated_workflow_contains_hypothesis_metadata() -> None:
    hypothesis = make_hypothesis(
        strategy="remove_prerequisite",
        target="checkout",
        prerequisite="login",
    )

    mutated = HypothesisMutator().mutate(
        make_workflow(),
        hypothesis,
    )

    assert mutated.workflow_id == "checkout-flow--h001"
    assert mutated.metadata["hypothesis_id"] == "H001"
    assert (
        mutated.metadata["mutation_strategy"]
        == "remove_prerequisite"
    )


def test_unsupported_strategy_is_rejected() -> None:
    hypothesis = make_hypothesis(
        strategy="unsupported",
        target="checkout",
        prerequisite="login",
    )

    with pytest.raises(
        ValueError,
        match="unsupported hypothesis mutation strategy",
    ):
        HypothesisMutator().mutate(
            make_workflow(),
            hypothesis,
        )


def test_missing_prerequisite_operation_is_rejected() -> None:
    hypothesis = make_hypothesis(
        strategy="remove_prerequisite",
        target="checkout",
        prerequisite="register",
    )

    with pytest.raises(
        ValueError,
        match="prerequisite operation not found: register",
    ):
        HypothesisMutator().mutate(
            make_workflow(),
            hypothesis,
        )


def test_missing_target_operation_is_rejected() -> None:
    hypothesis = make_hypothesis(
        strategy="duplicate_operation",
        target="payment",
        prerequisite=None,
    )

    with pytest.raises(
        ValueError,
        match="target operation not found: payment",
    ):
        HypothesisMutator().mutate(
            make_workflow(),
            hypothesis,
        )
