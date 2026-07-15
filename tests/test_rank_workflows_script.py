"""Tests for the workflow-ranking script."""

import json

from scripts.rank_workflows import (
    load_generated_workflows,
    save_ranked,
)
from hermes.mutation.models import Workflow, WorkflowStep
from hermes.prioritizer import WorkflowScorer
from hermes.semantic.models import OperationType
from hermes.workflow_generator.models import GeneratedWorkflow


def make_generated() -> GeneratedWorkflow:
    workflow = Workflow(
        workflow_id="generated-login",
        name="Generated Login",
        steps=(
            WorkflowStep(
                operation_type=OperationType.LOGIN,
                label="Login",
                source_state_id="home",
                target_state_id="login",
            ),
        ),
    )

    return GeneratedWorkflow(
        workflow=workflow,
        state_path=("home", "login"),
        operation_count=1,
        terminal_state_id="login",
    )


def test_load_generated_workflows(tmp_path) -> None:
    directory = tmp_path / "generated"
    directory.mkdir()

    payload = make_generated().to_dict()

    (directory / "workflow_01.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    workflows = load_generated_workflows(directory)

    assert len(workflows) == 1
    assert (
        workflows[0].workflow.workflow_id
        == "generated-login"
    )
    assert workflows[0].state_path == ("home", "login")


def test_save_ranked(tmp_path) -> None:
    scores = WorkflowScorer().rank(
        [make_generated()],
        maximum_depth=4,
        total_state_count=4,
    )

    output = tmp_path / "ranked" / "ranked.json"
    save_ranked(scores, output)

    assert output.exists()

    payload = json.loads(
        output.read_text(encoding="utf-8")
    )

    assert len(payload) == 1
    assert payload[0]["metadata"]["rank"] == 1
    assert payload[0]["total_score"] > 0
