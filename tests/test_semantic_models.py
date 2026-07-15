"""Tests for semantic-operation models."""

import pytest

from hermes.semantic.models import (
    OperationType,
    SemanticOperation,
)


def test_create_semantic_operation() -> None:
    operation = SemanticOperation(
        operation_type=OperationType.LOGIN,
        label="Sign In",
        source_state_id="home",
        target_state_id="login",
        selector="#login",
        confidence=0.95,
        evidence=("sign in",),
    )

    assert operation.operation_type is OperationType.LOGIN
    assert operation.confidence == 0.95
    assert operation.target_state_id == "login"


def test_to_dict() -> None:
    operation = SemanticOperation(
        operation_type=OperationType.ADD_TO_CART,
        label="Add",
        source_state_id="product",
    )

    data = operation.to_dict()

    assert data["operation_type"] == "add_to_cart"
    assert data["label"] == "Add"


def test_empty_source_state_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="source_state_id must not be empty",
    ):
        SemanticOperation(
            operation_type=OperationType.LOGIN,
            label="Login",
            source_state_id="",
        )


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1],
)
def test_invalid_confidence(confidence: float) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 1",
    ):
        SemanticOperation(
            operation_type=OperationType.UNKNOWN,
            label="Unknown",
            source_state_id="home",
            confidence=confidence,
        )
