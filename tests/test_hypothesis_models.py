"""Tests for HERMES hypothesis models."""

import pytest

from hermes.hypothesis.models import (
    ExpectedBehavior,
    HypothesisCategory,
    WorkflowHypothesis,
)


def make_hypothesis() -> WorkflowHypothesis:
    return WorkflowHypothesis(
        hypothesis_id="H001",
        title="Checkout requires login",
        description=(
            "Checkout should be rejected when authentication "
            "is removed."
        ),
        category=HypothesisCategory.AUTHENTICATION,
        source_workflow_id="checkout-workflow",
        mutation_strategy="remove_prerequisite",
        expected_behavior=ExpectedBehavior.REJECT,
        target_operation="checkout",
        prerequisite_operation="login",
        confidence=0.95,
    )


def test_create_hypothesis() -> None:
    hypothesis = make_hypothesis()

    assert hypothesis.hypothesis_id == "H001"
    assert (
        hypothesis.category
        is HypothesisCategory.AUTHENTICATION
    )
    assert hypothesis.confidence == 0.95


def test_hypothesis_serialization() -> None:
    data = make_hypothesis().to_dict()

    assert data["category"] == "authentication"
    assert data["expected_behavior"] == "reject"
    assert data["target_operation"] == "checkout"


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        (
            "hypothesis_id",
            "hypothesis_id must not be empty",
        ),
        ("title", "title must not be empty"),
        (
            "description",
            "description must not be empty",
        ),
        (
            "source_workflow_id",
            "source_workflow_id must not be empty",
        ),
        (
            "mutation_strategy",
            "mutation_strategy must not be empty",
        ),
    ],
)
def test_empty_required_fields_are_rejected(
    field_name: str,
    message: str,
) -> None:
    values = {
        "hypothesis_id": "H001",
        "title": "Title",
        "description": "Description",
        "category": HypothesisCategory.ORDERING,
        "source_workflow_id": "workflow",
        "mutation_strategy": "swap",
        "expected_behavior": ExpectedBehavior.DIVERGE,
    }
    values[field_name] = ""

    with pytest.raises(ValueError, match=message):
        WorkflowHypothesis(**values)


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1],
)
def test_invalid_confidence_is_rejected(
    confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 1",
    ):
        WorkflowHypothesis(
            hypothesis_id="H001",
            title="Title",
            description="Description",
            category=HypothesisCategory.ORDERING,
            source_workflow_id="workflow",
            mutation_strategy="swap",
            expected_behavior=ExpectedBehavior.DIVERGE,
            confidence=confidence,
        )
