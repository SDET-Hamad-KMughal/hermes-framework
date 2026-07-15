"""Tests for automatic workflow generation CLI."""

import json

from scripts.generate_workflows import (
    generate_workflows,
    load_operations,
    save_workflows,
)


def write_operations(tmp_path):
    path = tmp_path / "operations.json"

    path.write_text(
        json.dumps(
            [
                {
                    "operation_type": "login",
                    "label": "Login",
                    "source_state_id": "home",
                    "target_state_id": "login",
                    "selector": "a",
                    "confidence": 0.95,
                    "evidence": [],
                    "metadata": {},
                },
                {
                    "operation_type": "add_to_cart",
                    "label": "Add",
                    "source_state_id": "login",
                    "target_state_id": "cart",
                    "selector": "button",
                    "confidence": 0.90,
                    "evidence": [],
                    "metadata": {},
                },
            ]
        ),
        encoding="utf-8",
    )

    return path


def test_load_operations(tmp_path):
    operations = load_operations(
        write_operations(tmp_path)
    )

    assert len(operations) == 2
    assert operations[0].label == "Login"


def test_generate_workflows(tmp_path):
    workflows = generate_workflows(
        load_operations(write_operations(tmp_path)),
        start_state_id="home",
    )

    assert workflows
    assert workflows[0].operation_count >= 1


def test_save_workflows(tmp_path):
    workflows = generate_workflows(
        load_operations(write_operations(tmp_path)),
        start_state_id="home",
    )

    summary = save_workflows(
        workflows,
        tmp_path / "generated",
    )

    assert summary.exists()

    data = json.loads(
        summary.read_text(encoding="utf-8")
    )

    assert data["workflow_count"] >= 1
