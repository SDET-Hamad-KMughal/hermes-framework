"""Tests for HERMES workflow-prioritization models."""

import pytest

from hermes.mutation.models import Workflow
from hermes.prioritizer.models import (
    PrioritizationConfig,
    WorkflowScore,
)
from hermes.workflow_generator.models import GeneratedWorkflow


def make_generated() -> GeneratedWorkflow:
    workflow = Workflow(
        workflow_id="generated-login",
        name="Generated Login",
        steps=(),
    )

    return GeneratedWorkflow(
        workflow=workflow,
        state_path=("home",),
        operation_count=0,
        terminal_state_id="home",
    )


def test_default_prioritization_config() -> None:
    config = PrioritizationConfig()

    assert config.length_weight == 0.20
    assert config.operation_diversity_weight == 0.30


def test_custom_prioritization_config() -> None:
    config = PrioritizationConfig(
        length_weight=1.0,
        state_coverage_weight=0.0,
        operation_diversity_weight=0.0,
        business_operation_weight=0.0,
    )

    assert config.length_weight == 1.0


def test_negative_weight_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="prioritization weights must not be negative",
    ):
        PrioritizationConfig(length_weight=-0.1)


def test_all_zero_weights_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "at least one prioritization weight "
            "must be positive"
        ),
    ):
        PrioritizationConfig(
            length_weight=0.0,
            state_coverage_weight=0.0,
            operation_diversity_weight=0.0,
            business_operation_weight=0.0,
        )


def test_workflow_score_serialization() -> None:
    score = WorkflowScore(
        generated_workflow=make_generated(),
        total_score=0.8,
        length_score=0.5,
        state_coverage_score=0.7,
        operation_diversity_score=1.0,
        business_operation_score=1.0,
        metadata={"rank": 1},
    )

    data = score.to_dict()

    assert data["total_score"] == 0.8
    assert data["metadata"]["rank"] == 1
    assert (
        data["workflow"]["workflow"]["workflow_id"]
        == "generated-login"
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "total_score",
        "length_score",
        "state_coverage_score",
        "operation_diversity_score",
        "business_operation_score",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [-0.1, 1.1],
)
def test_invalid_score_is_rejected(
    field_name: str,
    invalid_value: float,
) -> None:
    values = {
        "total_score": 0.5,
        "length_score": 0.5,
        "state_coverage_score": 0.5,
        "operation_diversity_score": 0.5,
        "business_operation_score": 0.5,
    }
    values[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match="workflow scores must be between 0 and 1",
    ):
        WorkflowScore(
            generated_workflow=make_generated(),
            **values,
        )
