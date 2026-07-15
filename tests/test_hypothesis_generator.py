"""Tests for HERMES hypothesis generation."""

from hermes.hypothesis.generator import HypothesisGenerator
from hermes.hypothesis.models import HypothesisCategory
from hermes.hypothesis.templates import (
    AUTHENTICATION_REQUIRED,
    TOP_UP_IDEMPOTENCY,
)
from hermes.mutation.models import Workflow, WorkflowStep
from hermes.semantic.models import OperationType


def make_workflow(
    workflow_id: str,
    operation_types: tuple[OperationType, ...],
) -> Workflow:
    return Workflow(
        workflow_id=workflow_id,
        name=workflow_id,
        steps=tuple(
            WorkflowStep(
                operation_type=operation_type,
                label=operation_type.value,
                source_state_id=f"state-{index}",
                target_state_id=f"state-{index + 1}",
            )
            for index, operation_type in enumerate(
                operation_types
            )
        ),
    )


def test_checkout_workflow_generates_relevant_hypotheses() -> None:
    workflow = make_workflow(
        "checkout-flow",
        (
            OperationType.LOGIN,
            OperationType.ADD_TO_CART,
            OperationType.CHECKOUT,
        ),
    )

    hypotheses = HypothesisGenerator().generate(workflow)

    categories = {
        hypothesis.category
        for hypothesis in hypotheses
    }

    assert HypothesisCategory.AUTHENTICATION in categories
    assert HypothesisCategory.ORDERING in categories
    assert HypothesisCategory.STATE_DEPENDENCY in categories


def test_login_only_workflow_generates_no_hypotheses() -> None:
    workflow = make_workflow(
        "login-flow",
        (OperationType.LOGIN,),
    )

    hypotheses = HypothesisGenerator().generate(workflow)

    assert hypotheses == []


def test_wallet_workflow_generates_idempotency_hypothesis() -> None:
    workflow = make_workflow(
        "wallet-flow",
        (
            OperationType.LOGIN,
            OperationType.TOP_UP_WALLET,
        ),
    )

    hypotheses = HypothesisGenerator().generate(workflow)

    assert len(hypotheses) == 1
    assert hypotheses[0].category is HypothesisCategory.IDEMPOTENCY
    assert hypotheses[0].target_operation == "top_up_wallet"


def test_order_history_generates_authorization_hypothesis() -> None:
    workflow = make_workflow(
        "orders-flow",
        (
            OperationType.LOGIN,
            OperationType.VIEW_ORDERS,
        ),
    )

    hypotheses = HypothesisGenerator().generate(workflow)

    assert len(hypotheses) == 1
    assert hypotheses[0].category is HypothesisCategory.AUTHORIZATION


def test_generator_assigns_sequential_ids() -> None:
    workflow = make_workflow(
        "checkout-flow",
        (
            OperationType.LOGIN,
            OperationType.ADD_TO_CART,
            OperationType.CHECKOUT,
        ),
    )

    hypotheses = HypothesisGenerator().generate(workflow)

    assert [
        hypothesis.hypothesis_id
        for hypothesis in hypotheses
    ] == [
        f"H{index:03d}"
        for index in range(1, len(hypotheses) + 1)
    ]


def test_generator_uses_custom_templates() -> None:
    workflow = make_workflow(
        "checkout-flow",
        (
            OperationType.LOGIN,
            OperationType.CHECKOUT,
        ),
    )

    generator = HypothesisGenerator(
        templates=(AUTHENTICATION_REQUIRED,)
    )

    hypotheses = generator.generate(workflow)

    assert len(hypotheses) == 1
    assert (
        hypotheses[0].metadata["template_id"]
        == "authentication-required"
    )


def test_missing_prerequisite_blocks_template() -> None:
    workflow = make_workflow(
        "checkout-only",
        (OperationType.CHECKOUT,),
    )

    generator = HypothesisGenerator(
        templates=(AUTHENTICATION_REQUIRED,)
    )

    assert generator.generate(workflow) == []


def test_target_only_template_is_applicable() -> None:
    workflow = make_workflow(
        "topup-only",
        (OperationType.TOP_UP_WALLET,),
    )

    generator = HypothesisGenerator(
        templates=(TOP_UP_IDEMPOTENCY,)
    )

    hypotheses = generator.generate(workflow)

    assert len(hypotheses) == 1
