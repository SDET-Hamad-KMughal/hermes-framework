"""Tests for the workflow execution CLI."""

import json

from scripts.run_workflow import load_workflow
from hermes.semantic.models import OperationType


def write_workflow(tmp_path):
    path = tmp_path / "workflow.json"

    path.write_text(
        json.dumps(
            {
                "workflow_id": "checkout-flow",
                "name": "Checkout Flow",
                "steps": [
                    {
                        "operation_type": "login",
                        "label": "Login",
                        "source_state_id": "home",
                        "target_state_id": "products",
                        "selector": "#login",
                        "metadata": {},
                    },
                    {
                        "operation_type": "checkout",
                        "label": "Checkout",
                        "source_state_id": "cart",
                        "target_state_id": "success",
                        "selector": "#checkout",
                        "metadata": {},
                    },
                ],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    return path


def test_load_workflow(tmp_path):
    workflow = load_workflow(
        write_workflow(tmp_path)
    )

    assert workflow.workflow_id == "checkout-flow"
    assert workflow.name == "Checkout Flow"
    assert len(workflow) == 2

    assert (
        workflow.steps[0].operation_type
        is OperationType.LOGIN
    )

    assert (
        workflow.steps[1].operation_type
        is OperationType.CHECKOUT
    )


def test_workflow_metadata_loaded(tmp_path):
    workflow = load_workflow(
        write_workflow(tmp_path)
    )

    assert workflow.metadata == {}
