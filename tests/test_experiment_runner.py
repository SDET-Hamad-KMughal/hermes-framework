"""Tests for the HERMES scientific experiment runner."""

import json

import pytest

from hermes.evaluation.experiment_runner import (
    ExperimentRunner,
)


def valid_config() -> dict:
    return {
        "experiment_id": "experiment-1",
        "benchmark": "hermes-bench",
        "base_url": "http://127.0.0.1:5000",
        "workflows": [
            "configs/workflows/login.json"
        ],
        "groups": {
            "baseline": True,
            "generic_mutation": True,
            "hypothesis_mutation": True,
        },
        "runs_per_workflow": 3,
        "reset_browser_state": True,
        "headless": True,
        "outputs": {
            "raw_directory": "evaluation/raw",
            "aggregated_directory": (
                "evaluation/aggregated"
            ),
            "tables_directory": "evaluation/tables",
            "figures_directory": "evaluation/figures",
        },
    }


def write_config(tmp_path, payload: dict):
    path = tmp_path / "experiment.json"
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return path


def test_runner_loads_configuration(tmp_path) -> None:
    runner = ExperimentRunner(
        write_config(tmp_path, valid_config())
    )

    config = runner.load_configuration()

    assert config["experiment_id"] == "experiment-1"
    assert config["runs_per_workflow"] == 3
    assert runner.config == config


def test_runner_rejects_missing_file(tmp_path) -> None:
    runner = ExperimentRunner(
        tmp_path / "missing.json"
    )

    with pytest.raises(
        FileNotFoundError,
        match="experiment configuration not found",
    ):
        runner.load_configuration()


def test_runner_creates_output_directories(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    runner = ExperimentRunner(
        write_config(tmp_path, valid_config())
    )

    directories = runner.ensure_output_directories()

    assert directories["raw_directory"].exists()
    assert directories["aggregated_directory"].exists()
    assert directories["tables_directory"].exists()
    assert directories["figures_directory"].exists()


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        (
            "experiment_id",
            "missing experiment field: experiment_id",
        ),
        (
            "benchmark",
            "missing experiment field: benchmark",
        ),
        (
            "base_url",
            "missing experiment field: base_url",
        ),
        (
            "workflows",
            "missing experiment field: workflows",
        ),
        (
            "groups",
            "missing experiment field: groups",
        ),
        (
            "runs_per_workflow",
            "missing experiment field: runs_per_workflow",
        ),
        (
            "outputs",
            "missing experiment field: outputs",
        ),
    ],
)
def test_missing_required_field_is_rejected(
    tmp_path,
    field_name: str,
    message: str,
) -> None:
    payload = valid_config()
    del payload[field_name]

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    with pytest.raises(ValueError, match=message):
        runner.load_configuration()


def test_empty_workflows_are_rejected(
    tmp_path,
) -> None:
    payload = valid_config()
    payload["workflows"] = []

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    with pytest.raises(
        ValueError,
        match="workflows must contain at least one path",
    ):
        runner.load_configuration()


def test_invalid_run_count_is_rejected(
    tmp_path,
) -> None:
    payload = valid_config()
    payload["runs_per_workflow"] = 0

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    with pytest.raises(
        ValueError,
        match="runs_per_workflow must be at least 1",
    ):
        runner.load_configuration()


def test_missing_group_is_rejected(
    tmp_path,
) -> None:
    payload = valid_config()
    del payload["groups"]["hypothesis_mutation"]

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    with pytest.raises(
        ValueError,
        match=(
            "missing experiment group: "
            "hypothesis_mutation"
        ),
    ):
        runner.load_configuration()
