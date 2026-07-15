"""Reusable hypothesis templates for HERMES."""

from __future__ import annotations

from dataclasses import dataclass

from hermes.hypothesis.models import (
    ExpectedBehavior,
    HypothesisCategory,
    WorkflowHypothesis,
)


@dataclass(frozen=True, slots=True)
class HypothesisTemplate:
    """Template used to instantiate workflow hypotheses."""

    template_id: str
    title: str
    description_template: str
    category: HypothesisCategory
    mutation_strategy: str
    expected_behavior: ExpectedBehavior
    target_operation: str
    prerequisite_operation: str | None = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.template_id.strip():
            raise ValueError("template_id must not be empty")

        if not self.title.strip():
            raise ValueError("title must not be empty")

        if not self.description_template.strip():
            raise ValueError(
                "description_template must not be empty"
            )

        if not self.mutation_strategy.strip():
            raise ValueError(
                "mutation_strategy must not be empty"
            )

        if not self.target_operation.strip():
            raise ValueError(
                "target_operation must not be empty"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )

    def instantiate(
        self,
        *,
        hypothesis_id: str,
        source_workflow_id: str,
    ) -> WorkflowHypothesis:
        """Create a concrete hypothesis from the template."""

        description = self.description_template.format(
            target_operation=self.target_operation,
            prerequisite_operation=(
                self.prerequisite_operation or ""
            ),
        )

        return WorkflowHypothesis(
            hypothesis_id=hypothesis_id,
            title=self.title,
            description=description,
            category=self.category,
            source_workflow_id=source_workflow_id,
            mutation_strategy=self.mutation_strategy,
            expected_behavior=self.expected_behavior,
            target_operation=self.target_operation,
            prerequisite_operation=(
                self.prerequisite_operation
            ),
            confidence=self.confidence,
            metadata={
                "template_id": self.template_id,
            },
        )


AUTHENTICATION_REQUIRED = HypothesisTemplate(
    template_id="authentication-required",
    title="Authentication prerequisite required",
    description_template=(
        "{target_operation} should be rejected when "
        "{prerequisite_operation} is removed."
    ),
    category=HypothesisCategory.AUTHENTICATION,
    mutation_strategy="remove_prerequisite",
    expected_behavior=ExpectedBehavior.REJECT,
    target_operation="checkout",
    prerequisite_operation="login",
    confidence=0.95,
)


CART_REQUIRED_FOR_CHECKOUT = HypothesisTemplate(
    template_id="cart-required-for-checkout",
    title="Cart state required before checkout",
    description_template=(
        "{target_operation} should be rejected when "
        "{prerequisite_operation} is removed."
    ),
    category=HypothesisCategory.STATE_DEPENDENCY,
    mutation_strategy="remove_prerequisite",
    expected_behavior=ExpectedBehavior.REJECT,
    target_operation="checkout",
    prerequisite_operation="add_to_cart",
    confidence=0.95,
)


TOP_UP_IDEMPOTENCY = HypothesisTemplate(
    template_id="top-up-idempotency",
    title="Repeated wallet top-up preserves expected semantics",
    description_template=(
        "Repeating {target_operation} should not create an "
        "unexpected state transition."
    ),
    category=HypothesisCategory.IDEMPOTENCY,
    mutation_strategy="duplicate_operation",
    expected_behavior=ExpectedBehavior.PRESERVE_STATE,
    target_operation="top_up_wallet",
    confidence=0.85,
)


CHECKOUT_ORDERING = HypothesisTemplate(
    template_id="checkout-ordering",
    title="Checkout ordering dependency",
    description_template=(
        "{target_operation} before "
        "{prerequisite_operation} should be rejected."
    ),
    category=HypothesisCategory.ORDERING,
    mutation_strategy="swap_operations",
    expected_behavior=ExpectedBehavior.REJECT,
    target_operation="checkout",
    prerequisite_operation="add_to_cart",
    confidence=0.90,
)


ORDER_HISTORY_AUTHORIZATION = HypothesisTemplate(
    template_id="order-history-authorization",
    title="Order history requires authentication",
    description_template=(
        "{target_operation} should be rejected when "
        "{prerequisite_operation} is removed."
    ),
    category=HypothesisCategory.AUTHORIZATION,
    mutation_strategy="remove_prerequisite",
    expected_behavior=ExpectedBehavior.REJECT,
    target_operation="view_orders",
    prerequisite_operation="login",
    confidence=0.95,
)


DEFAULT_TEMPLATES = (
    AUTHENTICATION_REQUIRED,
    CART_REQUIRED_FOR_CHECKOUT,
    TOP_UP_IDEMPOTENCY,
    CHECKOUT_ORDERING,
    ORDER_HISTORY_AUTHORIZATION,
)
