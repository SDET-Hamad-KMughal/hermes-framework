"""Tests for the HERMES workflow mutation engine."""

import pytest

from hermes.mutation.engine import (
    MutationPlan,
    WorkflowMutationEngine,
)
from hermes.mutation.models import (
    MutationType,
    Workflow,
    WorkflowStep,
)
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


def test_engine_generates_mutations() -> None:
    mutations = WorkflowMutationEngine().generate(
        make_workflow()
    )

    assert mutations
    assert all(
        mutation.workflow_id != "checkout-flow"
        for mutation in mutations
    )


def test_engine_generates_expected_categories() -> None:
    engine = WorkflowMutationEngine()
    mutations = engine.generate(make_workflow())

    mutation_types = engine.mutation_types(mutations)

    assert MutationType.SKIP_STEP in mutation_types
    assert MutationType.DUPLICATE_STEP in mutation_types
    assert MutationType.SWAP_ADJACENT in mutation_types
    assert MutationType.REVERSE_WORKFLOW in mutation_types
    assert MutationType.INSERT_LOGOUT in mutation_types


def test_engine_respects_plan_flags() -> None:
    plan = MutationPlan(
        include_skip=True,
        include_duplicate=False,
        include_swap=False,
        include_reverse=False,
        include_logout=False,
    )

    mutations = WorkflowMutationEngine(plan).generate(
        make_workflow()
    )

    assert len(mutations) == 3
    assert all(
        item.metadata["mutation_type"] == "skip_step"
        for item in mutations
    )


def test_engine_respects_max_mutations() -> None:
    plan = MutationPlan(max_mutations=4)

    mutations = WorkflowMutationEngine(plan).generate(
        make_workflow()
    )

    assert len(mutations) == 4


def test_engine_handles_empty_workflow() -> None:
    workflow = Workflow(
        workflow_id="empty",
        name="Empty Workflow",
        steps=(),
    )

    mutations = WorkflowMutationEngine().generate(workflow)

    assert len(mutations) == 1
    assert mutations[0].steps[0].operation_type is OperationType.LOGOUT


def test_engine_deduplicates_identical_sequences() -> None:
    workflow = Workflow(
        workflow_id="duplicate-flow",
        name="Duplicate Flow",
        steps=(
            WorkflowStep(
                operation_type=OperationType.LOGIN,
                label="Login",
                source_state_id="home",
            ),
            WorkflowStep(
                operation_type=OperationType.LOGIN,
                label="Login",
                source_state_id="home",
            ),
        ),
    )

    mutations = WorkflowMutationEngine().generate(workflow)

    signatures = [
        tuple(
            step.operation_type.value
            for step in item.steps
        )
        for item in mutations
    ]

    assert len(signatures) == len(set(signatures))


@pytest.mark.parametrize(
    "max_mutations",
    [0, -1],
)
def test_invalid_max_mutations_is_rejected(
    max_mutations: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_mutations must be at least 1",
    ):
        MutationPlan(max_mutations=max_mutations)
