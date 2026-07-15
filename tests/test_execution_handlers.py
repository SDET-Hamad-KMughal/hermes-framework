"""Tests for HERMES execution handlers."""

from unittest.mock import MagicMock

import pytest

from hermes.executor.handlers import ExecutionHandler
from hermes.mutation.models import WorkflowStep
from hermes.semantic.models import OperationType


def test_click_operation_uses_selector() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.ADD_TO_CART,
        label="Add to Cart",
        source_state_id="product",
        selector=".add-to-cart",
    )

    ExecutionHandler().execute(context, step)

    context.click.assert_called_once_with(".add-to-cart")
    context.goto.assert_not_called()


def test_click_operation_falls_back_to_target() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.LOGIN,
        label="Login",
        source_state_id="home",
        target_state_id="http://test/login",
    )

    ExecutionHandler().execute(context, step)

    context.goto.assert_called_once_with("http://test/login")


def test_search_operation_fills_query() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.SEARCH,
        label="Search",
        source_state_id="home",
        selector="#search",
        metadata={"query": "laptop"},
    )

    ExecutionHandler().execute(context, step)

    context.fill.assert_called_once_with(
        "#search",
        "laptop",
    )


def test_search_operation_submits_when_configured() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.SEARCH,
        label="Search",
        source_state_id="home",
        selector="#search",
        metadata={
            "query": "laptop",
            "submit_selector": "#search-button",
        },
    )

    ExecutionHandler().execute(context, step)

    context.fill.assert_called_once_with(
        "#search",
        "laptop",
    )
    context.click.assert_called_once_with(
        "#search-button",
    )


def test_missing_click_target_is_rejected() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.CHECKOUT,
        label="Checkout",
        source_state_id="cart",
    )

    with pytest.raises(
        ValueError,
        match="step requires either selector or target_state_id",
    ):
        ExecutionHandler().execute(context, step)


def test_search_without_query_is_rejected() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.SEARCH,
        label="Search",
        source_state_id="home",
    )

    with pytest.raises(
        ValueError,
        match="search step requires query metadata",
    ):
        ExecutionHandler().execute(context, step)


def test_unknown_operation_is_rejected() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.UNKNOWN,
        label="Unknown",
        source_state_id="home",
    )

    with pytest.raises(
        ValueError,
        match="unsupported operation type: unknown",
    ):
        ExecutionHandler().execute(context, step)


def test_login_operation_fills_credentials_and_submits() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.LOGIN,
        label="Authenticate Session",
        source_state_id="login",
        selector='button[type="submit"]',
        metadata={
            "credentials": {
                "username": "alice",
                "password": "secret",
            },
            "username_selector": 'input[name="username"]',
            "password_selector": 'input[name="password"]',
        },
    )

    ExecutionHandler().execute(context, step)

    context.fill.assert_any_call(
        'input[name="username"]',
        "alice",
    )
    context.fill.assert_any_call(
        'input[name="password"]',
        "secret",
    )



def test_login_operation_fills_credentials_and_submits() -> None:
    context = MagicMock()

    step = WorkflowStep(
        operation_type=OperationType.LOGIN,
        label="Authenticate Session",
        source_state_id="login",
        selector='button[type="submit"]',
        metadata={
            "credentials": {
                "username": "alice",
                "password": "secret",
            },
            "username_selector": 'input[name="username"]',
            "password_selector": 'input[name="password"]',
        },
    )

    ExecutionHandler().execute(context, step)

    context.fill.assert_any_call(
        'input[name="username"]',
        "alice",
    )
    context.fill.assert_any_call(
        'input[name="password"]',
        "secret",
    )
    context.click.assert_called_once_with(
        'button[type="submit"]'
    )
