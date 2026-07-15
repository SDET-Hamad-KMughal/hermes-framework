"""Semantic workflow-step handlers for HERMES."""

from __future__ import annotations

from typing import Protocol

from hermes.mutation.models import WorkflowStep
from hermes.semantic.models import OperationType


class BrowserExecutionContext(Protocol):
    """Minimal browser interface required by execution handlers."""

    @property
    def current_url(self) -> str:
        """Return the currently loaded URL."""

    def goto(self, url: str) -> None:
        """Navigate to a URL."""

    def click(self, selector: str) -> None:
        """Click an element."""

    def fill(self, selector: str, value: str) -> None:
        """Fill a form field."""


class ExecutionHandler:
    """Execute one semantic workflow step."""

    def execute(
        self,
        context: BrowserExecutionContext,
        step: WorkflowStep,
    ) -> None:
        """Execute a semantic step using browser primitives."""

        if step.operation_type in {
            OperationType.LOGIN,
            OperationType.LOGOUT,
            OperationType.REGISTER,
            OperationType.VIEW_PRODUCT,
            OperationType.ADD_TO_CART,
            OperationType.REMOVE_FROM_CART,
            OperationType.CHECKOUT,
            OperationType.PAYMENT,
            OperationType.TOP_UP_WALLET,
            OperationType.VIEW_ORDERS,
        }:
            self._click_step(context, step)
            return

        if step.operation_type is OperationType.SEARCH:
            self._search(context, step)
            return

        raise ValueError(
            f"unsupported operation type: "
            f"{step.operation_type.value}"
        )

    @staticmethod
    def _click_step(
        context: BrowserExecutionContext,
        step: WorkflowStep,
    ) -> None:
        if step.selector:
            context.click(step.selector)
            return

        if step.target_state_id:
            context.goto(step.target_state_id)
            return

        raise ValueError(
            "step requires either selector or target_state_id"
        )

    @staticmethod
    def _search(
        context: BrowserExecutionContext,
        step: WorkflowStep,
    ) -> None:
        selector = step.selector or 'input[type="search"]'
        query = str(step.metadata.get("query", ""))

        if not query.strip():
            raise ValueError("search step requires query metadata")

        context.fill(selector, query)

        submit_selector = step.metadata.get("submit_selector")
        if submit_selector:
            context.click(str(submit_selector))
