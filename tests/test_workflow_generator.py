"""Tests for state-aware workflow generation."""

from hermes.semantic.models import (
    OperationType,
    SemanticOperation,
)
from hermes.workflow_generator.generator import (
    StateAwareWorkflowGenerator,
)
from hermes.workflow_generator.models import (
    WorkflowGenerationConfig,
)


def make_operations() -> list[SemanticOperation]:
    return [
        SemanticOperation(
            operation_type=OperationType.LOGIN,
            label="Login",
            source_state_id="home",
            target_state_id="login",
            selector="a",
            confidence=0.9,
        ),
        SemanticOperation(
            operation_type=OperationType.ADD_TO_CART,
            label="Add to Cart",
            source_state_id="login",
            target_state_id="cart",
            selector="button",
            confidence=0.9,
        ),
        SemanticOperation(
            operation_type=OperationType.CHECKOUT,
            label="Checkout",
            source_state_id="cart",
            target_state_id="success",
            selector="button",
            confidence=0.9,
        ),
        SemanticOperation(
            operation_type=OperationType.UNKNOWN,
            label="Unknown",
            source_state_id="home",
            target_state_id="unknown",
            confidence=0.0,
        ),
    ]


def test_generator_creates_connected_workflows() -> None:
    generated = StateAwareWorkflowGenerator().generate(
        make_operations(),
        "home",
    )

    operation_sequences = [
        tuple(
            step.operation_type
            for step in item.workflow.steps
        )
        for item in generated
    ]

    assert (OperationType.LOGIN,) in operation_sequences
    assert (
        OperationType.LOGIN,
        OperationType.ADD_TO_CART,
    ) in operation_sequences
    assert (
        OperationType.LOGIN,
        OperationType.ADD_TO_CART,
        OperationType.CHECKOUT,
    ) in operation_sequences


def test_generator_preserves_state_path() -> None:
    generated = StateAwareWorkflowGenerator().generate(
        make_operations(),
        "home",
    )

    longest = max(
        generated,
        key=lambda item: item.operation_count,
    )

    assert longest.state_path == (
        "home",
        "login",
        "cart",
        "success",
    )
    assert longest.terminal_state_id == "success"


def test_generator_excludes_unknown_by_default() -> None:
    generated = StateAwareWorkflowGenerator().generate(
        make_operations(),
        "home",
    )

    assert all(
        step.operation_type is not OperationType.UNKNOWN
        for item in generated
        for step in item.workflow.steps
    )


def test_generator_can_include_unknown() -> None:
    config = WorkflowGenerationConfig(
        include_unknown_operations=True,
    )

    generated = StateAwareWorkflowGenerator(config).generate(
        make_operations(),
        "home",
    )

    assert any(
        step.operation_type is OperationType.UNKNOWN
        for item in generated
        for step in item.workflow.steps
    )


def test_generator_respects_max_depth() -> None:
    config = WorkflowGenerationConfig(max_depth=2)

    generated = StateAwareWorkflowGenerator(config).generate(
        make_operations(),
        "home",
    )

    assert max(item.operation_count for item in generated) == 2


def test_generator_respects_minimum_steps() -> None:
    config = WorkflowGenerationConfig(
        max_depth=3,
        minimum_steps=2,
    )

    generated = StateAwareWorkflowGenerator(config).generate(
        make_operations(),
        "home",
    )

    assert generated
    assert all(
        item.operation_count >= 2
        for item in generated
    )


def test_generator_respects_workflow_limit() -> None:
    config = WorkflowGenerationConfig(max_workflows=2)

    generated = StateAwareWorkflowGenerator(config).generate(
        make_operations(),
        "home",
    )

    assert len(generated) == 2


def test_generator_returns_empty_for_unknown_start() -> None:
    generated = StateAwareWorkflowGenerator().generate(
        make_operations(),
        "missing",
    )

    assert generated == []
