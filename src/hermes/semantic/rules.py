"""Rule-based semantic classification for HERMES."""

from __future__ import annotations

from dataclasses import dataclass

from hermes.semantic.models import OperationType


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """Result of classifying low-level action text."""

    operation_type: OperationType
    confidence: float
    evidence: tuple[str, ...]


class SemanticRuleClassifier:
    """Classify actions using interpretable keyword rules."""

    _RULES: tuple[tuple[OperationType, tuple[str, ...]], ...] = (
        (OperationType.LOGOUT, ("logout", "log out", "sign out")),
        (OperationType.LOGIN, ("login", "log in", "sign in")),
        (OperationType.REGISTER, ("register", "sign up", "create account")),
        (OperationType.ADD_TO_CART, ("add to cart", "add cart")),
        (
            OperationType.REMOVE_FROM_CART,
            ("remove from cart", "delete from cart", "remove item"),
        ),
        (OperationType.CHECKOUT, ("checkout", "place order")),
        (OperationType.TOP_UP_WALLET, ("top up", "top-up", "add funds")),
        (OperationType.VIEW_ORDERS, ("order history", "my orders")),
        (OperationType.SEARCH, ("search", "find")),
        (OperationType.VIEW_PRODUCT, ("view product", "product details")),
        (OperationType.PAYMENT, ("pay", "payment")),
    )

    def classify(self, *values: str | None) -> ClassificationResult:
        """Classify combined action evidence."""

        normalized = " ".join(
            value.strip().lower()
            for value in values
            if value and value.strip()
        )

        for operation_type, keywords in self._RULES:
            matched = tuple(
                keyword for keyword in keywords if keyword in normalized
            )

            if matched:
                confidence = min(1.0, 0.70 + (0.10 * len(matched)))
                return ClassificationResult(
                    operation_type=operation_type,
                    confidence=confidence,
                    evidence=matched,
                )

        return ClassificationResult(
            operation_type=OperationType.UNKNOWN,
            confidence=0.0,
            evidence=(),
        )
