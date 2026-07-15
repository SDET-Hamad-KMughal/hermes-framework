"""Tests for automatic workflow-generation models."""

import pytest

from hermes.mutation.models import Workflow
from hermes.workflow_generator.models import (
    GeneratedWorkflow,
    WorkflowGenerationConfig,
)


def test_default_generation_config() -> None:
    config = WorkflowGenerationConfig()

    assert config.max_depth == 6
    assert config.max_workflows == 50
    assert config.minimum_steps == 1


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"max_depth": 0},
            "max_depth must be at least 1",
        ),
        (
            {"max_workflows": 0},
            "max_workflows must be at least 1",
        ),
        (
            {"minimum_steps": 0},
            "minimum_steps must be at least 1",
        ),
        (
            {
                "max_depth": 2,
                "minimum_steps": 3,
            },
            "minimum_steps must not exceed max_depth",
        ),
    ],
)
def test_invalid_generation_config(
    kwargs,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        WorkflowGenerationConfig(**kwargs)


def test_generated_workflow_serialization() -> None:
    workflow = Workflow(
        workflow_id="generated-1",
        name="Generated Workflow",
        steps=(),
    )

    generated = GeneratedWorkflow(
        workflow=workflow,
        state_path=("home", "login"),
        operation_count=1,
        terminal_state_id="login",
        metadata={"source": "state_graph"},
    )

    data = generated.to_dict()

    assert data["workflow"]["workflow_id"] == "generated-1"
    assert data["state_path"] == ["home", "login"]
    assert data["operation_count"] == 1
    assert data["terminal_state_id"] == "login"


@pytest.mark.parametrize(
    ("state_path", "operation_count", "terminal", "message"),
    [
        (
            (),
            0,
            "home",
            "state_path must not be empty",
        ),
        (
            ("home",),
            -1,
            "home",
            "operation_count must not be negative",
        ),
        (
            ("home",),
            0,
            "",
            "terminal_state_id must not be empty",
        ),
    ],
)
def test_invalid_generated_workflow(
    state_path,
    operation_count: int,
    terminal: str,
    message: str,
) -> None:
    workflow = Workflow(
        workflow_id="generated",
        name="Generated",
        steps=(),
    )

    with pytest.raises(ValueError, match=message):
        GeneratedWorkflow(
            workflow=workflow,
            state_path=state_path,
            operation_count=operation_count,
            terminal_state_id=terminal,
        )
