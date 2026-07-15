"""Tests for the HERMES scientific experiment runner."""

import json
from pathlib import Path

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


def test_runner_loads_workflow_objects(
    tmp_path,
) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "login-flow",
                "name": "Login Flow",
                "steps": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    payload = valid_config()
    payload["workflows"] = [str(workflow_path)]

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    workflows = runner.load_workflows()

    assert len(workflows) == 1
    assert workflows[0].workflow_id == "login-flow"
    assert workflows[0].name == "Login Flow"


def test_run_baselines_executes_and_persists_results(
    tmp_path,
    monkeypatch,
) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "login-flow",
                "name": "Login Flow",
                "steps": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    payload = valid_config()
    payload["workflows"] = [str(workflow_path)]
    payload["runs_per_workflow"] = 2
    payload["outputs"] = {
        "raw_directory": str(tmp_path / "raw"),
        "aggregated_directory": str(
            tmp_path / "aggregated"
        ),
        "tables_directory": str(tmp_path / "tables"),
        "figures_directory": str(tmp_path / "figures"),
    }

    class FakeExecution:
        success = True
        successful_steps = 2
        failed_steps = 0
        total_duration_seconds = 0.25

        def to_dict(self) -> dict:
            return {
                "workflow_id": "login-flow",
                "workflow_name": "Login Flow",
                "success": True,
                "successful_steps": 2,
                "failed_steps": 0,
                "total_duration_seconds": 0.25,
                "steps": [],
            }

    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner.execute_workflow",
        lambda **kwargs: FakeExecution(),
    )

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    records = runner.run_baselines()

    assert len(records) == 2
    assert all(record["success"] is True for record in records)
    assert all(record["group"] == "baseline" for record in records)
    assert records[0]["run_index"] == 1
    assert records[1]["run_index"] == 2
    assert all(
        Path(record["output"]).exists()
        for record in records
    )


def test_generic_mutations_can_be_disabled(
    tmp_path,
) -> None:
    payload = valid_config()
    payload["groups"]["generic_mutation"] = False

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    assert runner.run_generic_mutations() == []


def test_run_generic_mutations_persists_records(
    tmp_path,
    monkeypatch,
) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "checkout-flow",
                "name": "Checkout Flow",
                "steps": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    payload = valid_config()
    payload["workflows"] = [str(workflow_path)]
    payload["runs_per_workflow"] = 1
    payload["outputs"] = {
        "raw_directory": str(tmp_path / "raw"),
        "aggregated_directory": str(
            tmp_path / "aggregated"
        ),
        "tables_directory": str(tmp_path / "tables"),
        "figures_directory": str(tmp_path / "figures"),
    }

    class FakeExecution:
        success = True
        successful_steps = 1
        failed_steps = 0
        total_duration_seconds = 0.10
        workflow_id = "workflow"

        def to_dict(self) -> dict:
            return {
                "workflow_id": self.workflow_id,
                "success": self.success,
                "successful_steps": self.successful_steps,
                "failed_steps": self.failed_steps,
                "total_duration_seconds": (
                    self.total_duration_seconds
                ),
                "steps": [],
            }

    class FakeMutation:
        workflow_id = "checkout-flow--skip-step--0"
        metadata = {
            "mutation_type": "skip_step",
        }

    class FakeMutationEngine:
        def __init__(self, plan) -> None:
            self.plan = plan

        def generate(self, workflow):
            return [FakeMutation()]

    class FakeComparisonStatus:
        value = "divergent"

    class FakeComparison:
        status = FakeComparisonStatus()
        divergence_score = 0.75

        def to_dict(self) -> dict:
            return {
                "status": "divergent",
                "divergence_score": 0.75,
                "signals": [],
            }

    class FakeComparator:
        def compare(self, baseline, mutated):
            return FakeComparison()

    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "WorkflowMutationEngine",
        FakeMutationEngine,
    )
    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "BehaviorComparator",
        FakeComparator,
    )
    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "execute_workflow",
        lambda **kwargs: FakeExecution(),
    )

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    records = runner.run_generic_mutations()

    assert len(records) == 1
    assert records[0]["group"] == "generic_mutation"
    assert records[0]["mutation_strategy"] == "skip_step"
    assert records[0]["comparison_status"] == "divergent"
    assert records[0]["anomaly_detected"] is True
    assert Path(records[0]["output"]).exists()


def test_hypothesis_mutations_can_be_disabled(
    tmp_path,
) -> None:
    payload = valid_config()
    payload["groups"]["hypothesis_mutation"] = False

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    assert runner.run_hypothesis_mutations() == []


def test_run_hypothesis_mutations_persists_records(
    tmp_path,
    monkeypatch,
) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "workflow_id": "checkout-flow",
                "name": "Checkout Flow",
                "steps": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    payload = valid_config()
    payload["workflows"] = [str(workflow_path)]
    payload["runs_per_workflow"] = 1
    payload["outputs"] = {
        "raw_directory": str(tmp_path / "raw"),
        "aggregated_directory": str(
            tmp_path / "aggregated"
        ),
        "tables_directory": str(tmp_path / "tables"),
        "figures_directory": str(tmp_path / "figures"),
    }

    class FakeExecution:
        success = False
        successful_steps = 0
        failed_steps = 1
        total_duration_seconds = 0.15
        workflow_id = "workflow"

        def to_dict(self) -> dict:
            return {
                "workflow_id": self.workflow_id,
                "success": self.success,
                "successful_steps": self.successful_steps,
                "failed_steps": self.failed_steps,
                "total_duration_seconds": (
                    self.total_duration_seconds
                ),
                "steps": [],
            }

    class FakeCategory:
        value = "authentication"

    class FakeExpectedBehavior:
        value = "reject"

    class FakeHypothesis:
        hypothesis_id = "H001"
        title = "Checkout requires login"
        category = FakeCategory()
        mutation_strategy = "remove_prerequisite"
        expected_behavior = FakeExpectedBehavior()
        target_operation = "checkout"
        prerequisite_operation = "login"
        confidence = 0.95

        def to_dict(self) -> dict:
            return {
                "hypothesis_id": "H001",
                "title": self.title,
                "category": "authentication",
                "mutation_strategy": (
                    "remove_prerequisite"
                ),
                "expected_behavior": "reject",
            }

    class FakeMutation:
        workflow_id = "checkout-flow--h001"

    class FakeHypothesisGenerator:
        def generate(self, workflow):
            return [FakeHypothesis()]

    class FakeHypothesisMutator:
        def mutate(self, workflow, hypothesis):
            return FakeMutation()

    class FakeComparisonStatus:
        value = "divergent"

    class FakeComparison:
        status = FakeComparisonStatus()
        divergence_score = 0.80

        def to_dict(self) -> dict:
            return {
                "status": "divergent",
                "divergence_score": 0.80,
                "signals": [],
            }

    class FakeComparator:
        def compare(self, baseline, mutated):
            return FakeComparison()

    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "HypothesisGenerator",
        FakeHypothesisGenerator,
    )
    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "HypothesisMutator",
        FakeHypothesisMutator,
    )
    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "BehaviorComparator",
        FakeComparator,
    )
    monkeypatch.setattr(
        "hermes.evaluation.experiment_runner."
        "execute_workflow",
        lambda **kwargs: FakeExecution(),
    )

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    records = runner.run_hypothesis_mutations()

    assert len(records) == 1
    assert records[0]["group"] == "hypothesis_mutation"
    assert records[0]["hypothesis_id"] == "H001"
    assert (
        records[0]["mutation_strategy"]
        == "remove_prerequisite"
    )
    assert (
        records[0]["hypothesis_category"]
        == "authentication"
    )
    assert records[0]["comparison_status"] == "divergent"
    assert records[0]["anomaly_detected"] is True
    assert Path(records[0]["output"]).exists()


def test_run_executes_enabled_groups(
    tmp_path,
    monkeypatch,
) -> None:
    payload = valid_config()
    payload["outputs"] = {
        "raw_directory": str(tmp_path / "raw"),
        "aggregated_directory": str(
            tmp_path / "aggregated"
        ),
        "tables_directory": str(tmp_path / "tables"),
        "figures_directory": str(tmp_path / "figures"),
    }

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    monkeypatch.setattr(
        runner,
        "run_baselines",
        lambda: [{"group": "baseline"}],
    )
    monkeypatch.setattr(
        runner,
        "run_generic_mutations",
        lambda: [{"group": "generic_mutation"}],
    )
    monkeypatch.setattr(
        runner,
        "run_hypothesis_mutations",
        lambda: [{"group": "hypothesis_mutation"}],
    )

    summary = runner.run()

    assert summary["baseline_record_count"] == 1
    assert summary["generic_mutation_record_count"] == 1
    assert summary["hypothesis_mutation_record_count"] == 1
    assert summary["total_record_count"] == 3
    assert Path(summary["summary_path"]).exists()


def test_run_skips_disabled_baseline_group(
    tmp_path,
    monkeypatch,
) -> None:
    payload = valid_config()
    payload["groups"]["baseline"] = False
    payload["outputs"] = {
        "raw_directory": str(tmp_path / "raw"),
        "aggregated_directory": str(
            tmp_path / "aggregated"
        ),
        "tables_directory": str(tmp_path / "tables"),
        "figures_directory": str(tmp_path / "figures"),
    }

    runner = ExperimentRunner(
        write_config(tmp_path, payload)
    )

    monkeypatch.setattr(
        runner,
        "run_baselines",
        lambda: (_ for _ in ()).throw(
            AssertionError(
                "baseline group should not run"
            )
        ),
    )
    monkeypatch.setattr(
        runner,
        "run_generic_mutations",
        lambda: [],
    )
    monkeypatch.setattr(
        runner,
        "run_hypothesis_mutations",
        lambda: [],
    )

    summary = runner.run()

    assert summary["baseline_record_count"] == 0
    assert summary["total_record_count"] == 0
