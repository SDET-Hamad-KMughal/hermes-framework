"""Tests for workflow mutation report generation."""

import json

from scripts.generate_mutation_report import (
    generate_report,
    load_workflow,
)
from hermes.mutation import MutationPlan
from hermes.semantic.models import OperationType


def write_baseline_workflow(tmp_path):
    path = tmp_path / "baseline_workflow.json"

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
                        "operation_type": "add_to_cart",
                        "label": "Add to Cart",
                        "source_state_id": "products",
                        "target_state_id": "cart",
                        "selector": ".add-to-cart",
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
                "metadata": {
                    "source": "test",
                },
            }
        ),
        encoding="utf-8",
    )

    return path


def test_load_workflow(tmp_path) -> None:
    workflow = load_workflow(
        write_baseline_workflow(tmp_path)
    )

    assert workflow.workflow_id == "checkout-flow"
    assert workflow.name == "Checkout Flow"
    assert len(workflow) == 3
    assert (
        workflow.steps[0].operation_type
        is OperationType.LOGIN
    )
    assert (
        workflow.steps[1].operation_type
        is OperationType.ADD_TO_CART
    )


def test_generate_report(tmp_path) -> None:
    workflow = load_workflow(
        write_baseline_workflow(tmp_path)
    )

    report = generate_report(workflow)

    assert report["summary"]["baseline_steps"] == 3
    assert report["summary"]["generated_mutations"] > 0
    assert report["mutations"]
    assert report["baseline"]["workflow_id"] == "checkout-flow"


def test_generate_report_counts_mutation_types(
    tmp_path,
) -> None:
    workflow = load_workflow(
        write_baseline_workflow(tmp_path)
    )

    report = generate_report(workflow)

    mutation_types = report["summary"]["mutation_types"]

    assert mutation_types["skip_step"] == 3
    assert mutation_types["duplicate_step"] == 3
    assert mutation_types["swap_adjacent"] == 2
    assert mutation_types["reverse_workflow"] == 1
    assert mutation_types["insert_logout"] == 4


def test_generate_report_respects_limit(
    tmp_path,
) -> None:
    workflow = load_workflow(
        write_baseline_workflow(tmp_path)
    )

    report = generate_report(
        workflow,
        MutationPlan(max_mutations=3),
    )

    assert report["summary"]["generated_mutations"] == 3
    assert len(report["mutations"]) == 3
