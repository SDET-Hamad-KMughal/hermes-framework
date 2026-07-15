"""Tests for workflow execution runner."""

from unittest.mock import MagicMock

from hermes.executor.runner import WorkflowExecutionRunner
from hermes.mutation.models import Workflow
from hermes.mutation.models import WorkflowStep
from hermes.semantic.models import OperationType


def build_workflow():

    return Workflow(
        workflow_id="checkout-flow",
        name="Checkout Flow",
        steps=(
            WorkflowStep(
                operation_type=OperationType.LOGIN,
                label="Login",
                source_state_id="home",
                selector="#login",
            ),
            WorkflowStep(
                operation_type=OperationType.ADD_TO_CART,
                label="Cart",
                source_state_id="products",
                selector=".cart",
            ),
        ),
    )


def test_execute_workflow():

    context = MagicMock()

    context.current_url = "http://test"

    runner = WorkflowExecutionRunner()

    result = runner.execute(
        context,
        build_workflow(),
    )

    assert result.success
    assert result.successful_steps == 2
    assert result.failed_steps == 0


def test_runner_returns_step_results():

    context = MagicMock()

    context.current_url = "http://test"

    runner = WorkflowExecutionRunner()

    result = runner.execute(
        context,
        build_workflow(),
    )

    assert len(result.steps) == 2
    assert result.steps[0].success
    assert result.steps[1].success


def test_runner_records_failure():

    context = MagicMock()

    context.current_url = "http://test"

    handler = MagicMock()

    handler.execute.side_effect = RuntimeError("boom")

    runner = WorkflowExecutionRunner(handler)

    result = runner.execute(
        context,
        build_workflow(),
    )

    assert not result.success
    assert result.failed_steps == 2
