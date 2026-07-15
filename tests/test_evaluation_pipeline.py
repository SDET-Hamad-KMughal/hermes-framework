"""Tests for the HERMES evaluation pipeline."""

from unittest.mock import MagicMock

from hermes.comparator import BehaviorComparator
from hermes.evaluation.pipeline import EvaluationPipeline
from hermes.executor import WorkflowExecutionRunner
from hermes.mutation import Workflow, WorkflowStep
from hermes.semantic.models import OperationType


def make_workflow() -> Workflow:
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
                operation_type=OperationType.CHECKOUT,
                label="Checkout",
                source_state_id="cart",
                selector="#checkout",
            ),
        ),
    )


def test_pipeline_runs() -> None:
    context = MagicMock()
    context.current_url = "http://test"

    runner = WorkflowExecutionRunner()

    pipeline = EvaluationPipeline(
        runner=runner,
        comparator=BehaviorComparator(),
    )

    result = pipeline.evaluate(
        context,
        make_workflow(),
    )

    assert result.mutation_count > 0
    assert result.baseline_execution.workflow_id == "checkout-flow"


def test_pipeline_returns_summary() -> None:
    context = MagicMock()
    context.current_url = "http://test"

    result = EvaluationPipeline(
        WorkflowExecutionRunner(),
        BehaviorComparator(),
    ).evaluate(
        context,
        make_workflow(),
    )

    assert result.mutation_count == len(
        result.mutations
    )

    assert (
        result.anomaly_count
        + result.equivalent_count
        == result.mutation_count
    )
