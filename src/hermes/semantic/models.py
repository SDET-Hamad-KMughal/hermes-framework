"""Semantic-operation models for HERMES."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class OperationType(str, Enum):
    """Supported semantic business-operation categories."""

    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    SEARCH = "search"
    VIEW_PRODUCT = "view_product"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    CHECKOUT = "checkout"
    PAYMENT = "payment"
    TOP_UP_WALLET = "top_up_wallet"
    VIEW_ORDERS = "view_orders"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SemanticOperation:
    """A business-level operation discovered from a low-level action."""

    operation_type: OperationType
    label: str
    source_state_id: str
    target_state_id: str | None = None
    selector: str | None = None
    confidence: float = 0.0
    evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate semantic-operation data."""

        if not self.source_state_id.strip():
            raise ValueError("source_state_id must not be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        """Convert the operation into serializable data."""

        data = asdict(self)
        data["operation_type"] = self.operation_type.value
        return data
