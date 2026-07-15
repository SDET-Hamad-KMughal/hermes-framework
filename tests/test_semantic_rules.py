"""Tests for rule-based semantic classification."""

import pytest

from hermes.semantic.models import OperationType
from hermes.semantic.rules import SemanticRuleClassifier


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Sign In Here", OperationType.LOGIN),
        ("Create Account", OperationType.REGISTER),
        ("Add to Cart", OperationType.ADD_TO_CART),
        ("Proceed to Checkout", OperationType.CHECKOUT),
        ("Top Up Wallet", OperationType.TOP_UP_WALLET),
        ("My Orders", OperationType.VIEW_ORDERS),
        ("Search Products", OperationType.SEARCH),
    ],
)
def test_classifier_recognizes_operations(
    text: str,
    expected: OperationType,
) -> None:
    result = SemanticRuleClassifier().classify(text)

    assert result.operation_type is expected
    assert result.confidence >= 0.7
    assert result.evidence


def test_classifier_combines_multiple_evidence_fields() -> None:
    result = SemanticRuleClassifier().classify(
        "button",
        "#login-submit",
        "Sign In",
    )

    assert result.operation_type is OperationType.LOGIN


def test_unknown_operation() -> None:
    result = SemanticRuleClassifier().classify(
        "Continue",
        "#generic-button",
    )

    assert result.operation_type is OperationType.UNKNOWN
    assert result.confidence == 0.0
    assert result.evidence == ()
