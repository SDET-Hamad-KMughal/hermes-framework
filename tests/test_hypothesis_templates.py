"""Tests for HERMES hypothesis templates."""

import pytest

from hermes.hypothesis.models import (
    ExpectedBehavior,
    HypothesisCategory,
)
from hermes.hypothesis.templates import (
    AUTHENTICATION_REQUIRED,
    DEFAULT_TEMPLATES,
    HypothesisTemplate,
)


def test_template_instantiation() -> None:
    hypothesis = AUTHENTICATION_REQUIRED.instantiate(
        hypothesis_id="H001",
        source_workflow_id="checkout-workflow",
    )

    assert hypothesis.hypothesis_id == "H001"
    assert hypothesis.source_workflow_id == "checkout-workflow"
    assert hypothesis.target_operation == "checkout"
    assert hypothesis.prerequisite_operation == "login"
    assert hypothesis.expected_behavior is ExpectedBehavior.REJECT
    assert (
        hypothesis.metadata["template_id"]
        == "authentication-required"
    )


def test_template_formats_description() -> None:
    hypothesis = AUTHENTICATION_REQUIRED.instantiate(
        hypothesis_id="H001",
        source_workflow_id="checkout-workflow",
    )

    assert "checkout" in hypothesis.description
    assert "login" in hypothesis.description


def test_default_templates_are_unique() -> None:
    template_ids = [
        template.template_id
        for template in DEFAULT_TEMPLATES
    ]

    assert len(template_ids) == len(set(template_ids))


def test_default_templates_cover_core_categories() -> None:
    categories = {
        template.category
        for template in DEFAULT_TEMPLATES
    }

    assert HypothesisCategory.AUTHENTICATION in categories
    assert HypothesisCategory.ORDERING in categories
    assert HypothesisCategory.IDEMPOTENCY in categories
    assert HypothesisCategory.AUTHORIZATION in categories
    assert HypothesisCategory.STATE_DEPENDENCY in categories


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        ("template_id", "template_id must not be empty"),
        ("title", "title must not be empty"),
        (
            "description_template",
            "description_template must not be empty",
        ),
        (
            "mutation_strategy",
            "mutation_strategy must not be empty",
        ),
        (
            "target_operation",
            "target_operation must not be empty",
        ),
    ],
)
def test_empty_template_fields_are_rejected(
    field_name: str,
    message: str,
) -> None:
    values = {
        "template_id": "template",
        "title": "Title",
        "description_template": "{target_operation}",
        "category": HypothesisCategory.ORDERING,
        "mutation_strategy": "swap",
        "expected_behavior": ExpectedBehavior.REJECT,
        "target_operation": "checkout",
    }

    values[field_name] = ""

    with pytest.raises(ValueError, match=message):
        HypothesisTemplate(**values)


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1],
)
def test_invalid_template_confidence(
    confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 1",
    ):
        HypothesisTemplate(
            template_id="template",
            title="Title",
            description_template="{target_operation}",
            category=HypothesisCategory.ORDERING,
            mutation_strategy="swap",
            expected_behavior=ExpectedBehavior.REJECT,
            target_operation="checkout",
            confidence=confidence,
        )
