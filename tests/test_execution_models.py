"""Tests for HERMES execution-result models."""

import pytest

from hermes.executor.models import (
    ExecutionStepResult,
    WorkflowExecutionResult,
)
from hermes.semantic.models import OperationType


def make_step(
    index: int,
    success: bool,
    duration: float,
) -> ExecutionStepResult:
    return ExecutionStepResult(
        step_index=index,
        operation_type=OperationType.LOGIN,
        label="Login",
        success=success,
        url_before="http://test/",
        url_after="http://test/dashboard",
        duration_seconds=duration,
    )


def test_create_execution_step_result() -> None:
    result = make_step(0, True, 0.25)

    assert result.success is True
    assert result.step_index == 0
    assert result.duration_seconds == 0.25


def test_execution_step_serialization() -> None:
    result = make_step(0, True, 0.25)

    data = result.to_dict()

    assert data["operation_type"] == "login"
    assert data["success"] is True


def test_workflow_execution_summary() -> None:
    result = WorkflowExecutionResult(
        workflow_id="checkout-flow",
        workflow_name="Checkout Flow",
        steps=(
            make_step(0, True, 0.2),
            make_step(1, False, 0.3),
        ),
        started_at="2026-07-15T10:00:00+00:00",
        finished_at="2026-07-15T10:00:01+00:00",
    )

    assert result.success is False
    assert result.successful_steps == 1
    assert result.failed_steps == 1
    assert result.total_duration_seconds == pytest.approx(0.5)


def test_workflow_execution_serialization() -> None:
    result = WorkflowExecutionResult(
        workflow_id="flow-1",
        workflow_name="Flow",
        steps=(make_step(0, True, 0.1),),
        started_at="start",
        finished_at="finish",
    )

    data = result.to_dict()

    assert data["workflow_id"] == "flow-1"
    assert data["success"] is True
    assert len(data["steps"]) == 1


@pytest.mark.parametrize(
    ("workflow_id", "workflow_name", "message"),
    [
        ("", "Flow", "workflow_id must not be empty"),
        ("flow-1", "", "workflow_name must not be empty"),
    ],
)
def test_invalid_execution_result_is_rejected(
    workflow_id: str,
    workflow_name: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        WorkflowExecutionResult(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            steps=(),
            started_at="start",
            finished_at="finish",
        )


@pytest.mark.parametrize(
    ("step_index", "duration_seconds", "message"),
    [
        (-1, 0.0, "step_index must not be negative"),
        (0, -0.1, "duration_seconds must not be negative"),
    ],
)
def test_invalid_step_result_is_rejected(
    step_index: int,
    duration_seconds: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ExecutionStepResult(
            step_index=step_index,
            operation_type=OperationType.UNKNOWN,
            label="Unknown",
            success=False,
            duration_seconds=duration_seconds,
        )
