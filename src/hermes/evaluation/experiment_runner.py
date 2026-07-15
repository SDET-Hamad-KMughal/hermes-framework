"""Scientific experiment orchestration for HERMES."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_workflow import (
    execute_workflow,
    load_workflow,
)

from hermes.comparator import BehaviorComparator
from hermes.hypothesis import (
    HypothesisGenerator,
    HypothesisMutator,
)
from hermes.mutation import MutationPlan, WorkflowMutationEngine


from datetime import UTC, datetime


class ExperimentRunner:
    """Coordinate the complete HERMES scientific evaluation."""

    REQUIRED_GROUPS = (
        "baseline",
        "generic_mutation",
        "hypothesis_mutation",
    )

    def __init__(
        self,
        config_path: str | Path,
    ) -> None:
        self.config_path = Path(config_path)
        self.config: dict[str, Any] | None = None

    def load_configuration(self) -> dict[str, Any]:
        """Load and validate the experiment configuration."""

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"experiment configuration not found: "
                f"{self.config_path}"
            )

        payload = json.loads(
            self.config_path.read_text(
                encoding="utf-8"
            )
        )

        self._validate_configuration(payload)
        self.config = payload

        return payload

    @classmethod
    def _validate_configuration(
        cls,
        payload: dict[str, Any],
    ) -> None:
        required_fields = (
            "experiment_id",
            "benchmark",
            "base_url",
            "workflows",
            "groups",
            "runs_per_workflow",
            "outputs",
        )

        for field_name in required_fields:
            if field_name not in payload:
                raise ValueError(
                    f"missing experiment field: {field_name}"
                )

        if not str(payload["experiment_id"]).strip():
            raise ValueError(
                "experiment_id must not be empty"
            )

        if not str(payload["benchmark"]).strip():
            raise ValueError(
                "benchmark must not be empty"
            )

        if not str(payload["base_url"]).strip():
            raise ValueError(
                "base_url must not be empty"
            )

        workflows = payload["workflows"]

        if not isinstance(workflows, list) or not workflows:
            raise ValueError(
                "workflows must contain at least one path"
            )

        if int(payload["runs_per_workflow"]) < 1:
            raise ValueError(
                "runs_per_workflow must be at least 1"
            )

        groups = payload["groups"]

        if not isinstance(groups, dict):
            raise ValueError("groups must be an object")

        for group_name in cls.REQUIRED_GROUPS:
            if group_name not in groups:
                raise ValueError(
                    f"missing experiment group: {group_name}"
                )

            if not isinstance(groups[group_name], bool):
                raise ValueError(
                    f"experiment group must be boolean: "
                    f"{group_name}"
                )

        outputs = payload["outputs"]

        if not isinstance(outputs, dict):
            raise ValueError("outputs must be an object")

        required_outputs = (
            "raw_directory",
            "aggregated_directory",
            "tables_directory",
            "figures_directory",
        )

        for output_name in required_outputs:
            if not str(outputs.get(output_name, "")).strip():
                raise ValueError(
                    f"missing output directory: {output_name}"
                )

    def ensure_output_directories(
        self,
    ) -> dict[str, Path]:
        """Create and return configured output directories."""

        config = self.config or self.load_configuration()
        outputs = config["outputs"]

        directories = {
            name: Path(path)
            for name, path in outputs.items()
        }

        for directory in directories.values():
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        return directories

    # ============================================================
    # Phase 13.3
    # ============================================================

    def load_workflows(self) -> list:
        """Load all configured baseline workflows."""

        config = self.config or self.load_configuration()

        return [
            load_workflow(Path(workflow_path))
            for workflow_path in config["workflows"]
        ]

    def run_baselines(self) -> list[dict[str, Any]]:
        """Execute every baseline workflow repeatedly."""

        config = self.config or self.load_configuration()
        output_dirs = self.ensure_output_directories()

        run_count = int(config["runs_per_workflow"])
        base_url = str(config["base_url"])
        headless = bool(config.get("headless", True))

        records: list[dict[str, Any]] = []

        for workflow in self.load_workflows():
            for run_index in range(1, run_count + 1):
                started_at = datetime.now(UTC).isoformat()

                execution = execute_workflow(
                    workflow=workflow,
                    start_url=base_url,
                    headless=headless,
                )

                record = {
                    "group": "baseline",
                    "workflow_id": workflow.workflow_id,
                    "workflow_name": workflow.name,
                    "run_index": run_index,
                    "started_at": started_at,
                    "success": execution.success,
                    "successful_steps": execution.successful_steps,
                    "failed_steps": execution.failed_steps,
                    "total_duration_seconds": (
                        execution.total_duration_seconds
                    ),
                    "execution": execution.to_dict(),
                }

                filename = (
                    f"baseline__{workflow.workflow_id}"
                    f"__run_{run_index:02d}.json"
                )

                output = (
                    output_dirs["raw_directory"]
                    / filename
                )

                output.write_text(
                    json.dumps(record, indent=2),
                    encoding="utf-8",
                )

                record["output"] = str(output)
                records.append(record)

        return records

    def run_generic_mutations(
        self,
    ) -> list[dict[str, Any]]:
        """Execute and compare generic workflow mutations."""

        config = self.config or self.load_configuration()

        if not config["groups"]["generic_mutation"]:
            return []

        output_dirs = self.ensure_output_directories()

        run_count = int(config["runs_per_workflow"])
        base_url = str(config["base_url"])
        headless = bool(config.get("headless", True))

        mutation_engine = WorkflowMutationEngine(
            MutationPlan()
        )
        comparator = BehaviorComparator()

        records: list[dict[str, Any]] = []

        for workflow in self.load_workflows():
            mutations = mutation_engine.generate(workflow)

            for run_index in range(1, run_count + 1):
                baseline_execution = execute_workflow(
                    workflow=workflow,
                    start_url=base_url,
                    headless=headless,
                )

                for mutation in mutations:
                    started_at = datetime.now(UTC).isoformat()

                    execution = execute_workflow(
                        workflow=mutation,
                        start_url=base_url,
                        headless=headless,
                    )

                    comparison = comparator.compare(
                        baseline_execution,
                        execution,
                    )

                    record = {
                        "group": "generic_mutation",
                        "source_workflow_id": (
                            workflow.workflow_id
                        ),
                        "mutation_workflow_id": (
                            mutation.workflow_id
                        ),
                        "mutation_strategy": (
                            mutation.metadata.get(
                                "mutation_type",
                                mutation.metadata.get(
                                    "mutation_strategy",
                                    "generic",
                                ),
                            )
                        ),
                        "run_index": run_index,
                        "started_at": started_at,
                        "execution_success": execution.success,
                        "successful_steps": (
                            execution.successful_steps
                        ),
                        "failed_steps": execution.failed_steps,
                        "total_duration_seconds": (
                            execution.total_duration_seconds
                        ),
                        "comparison_status": (
                            comparison.status.value
                        ),
                        "divergence_score": (
                            comparison.divergence_score
                        ),
                        "anomaly_detected": (
                            comparison.status.value
                            == "divergent"
                        ),
                        "execution": execution.to_dict(),
                        "comparison": comparison.to_dict(),
                    }

                    safe_mutation_id = (
                        mutation.workflow_id.replace(
                            "/",
                            "_",
                        )
                    )

                    filename = (
                        f"generic__{safe_mutation_id}"
                        f"__run_{run_index:02d}.json"
                    )

                    output = (
                        output_dirs["raw_directory"]
                        / filename
                    )

                    output.write_text(
                        json.dumps(record, indent=2),
                        encoding="utf-8",
                    )

                    record["output"] = str(output)
                    records.append(record)

        return records

    def run_hypothesis_mutations(
        self,
    ) -> list[dict[str, Any]]:
        """Execute and compare hypothesis-driven mutations."""

        config = self.config or self.load_configuration()

        if not config["groups"]["hypothesis_mutation"]:
            return []

        output_dirs = self.ensure_output_directories()

        run_count = int(config["runs_per_workflow"])
        base_url = str(config["base_url"])
        headless = bool(config.get("headless", True))

        hypothesis_generator = HypothesisGenerator()
        hypothesis_mutator = HypothesisMutator()
        comparator = BehaviorComparator()

        records: list[dict[str, Any]] = []

        for workflow in self.load_workflows():
            hypotheses = hypothesis_generator.generate(
                workflow
            )

            for run_index in range(1, run_count + 1):
                baseline_execution = execute_workflow(
                    workflow=workflow,
                    start_url=base_url,
                    headless=headless,
                )

                for hypothesis in hypotheses:
                    mutation = hypothesis_mutator.mutate(
                        workflow,
                        hypothesis,
                    )

                    started_at = datetime.now(
                        UTC
                    ).isoformat()

                    execution = execute_workflow(
                        workflow=mutation,
                        start_url=base_url,
                        headless=headless,
                    )

                    comparison = comparator.compare(
                        baseline_execution,
                        execution,
                    )

                    record = {
                        "group": "hypothesis_mutation",
                        "source_workflow_id": (
                            workflow.workflow_id
                        ),
                        "hypothesis_id": (
                            hypothesis.hypothesis_id
                        ),
                        "hypothesis_title": (
                            hypothesis.title
                        ),
                        "hypothesis_category": (
                            hypothesis.category.value
                        ),
                        "mutation_strategy": (
                            hypothesis.mutation_strategy
                        ),
                        "expected_behavior": (
                            hypothesis.expected_behavior.value
                        ),
                        "target_operation": (
                            hypothesis.target_operation
                        ),
                        "prerequisite_operation": (
                            hypothesis.prerequisite_operation
                        ),
                        "confidence": hypothesis.confidence,
                        "mutation_workflow_id": (
                            mutation.workflow_id
                        ),
                        "run_index": run_index,
                        "started_at": started_at,
                        "execution_success": (
                            execution.success
                        ),
                        "successful_steps": (
                            execution.successful_steps
                        ),
                        "failed_steps": (
                            execution.failed_steps
                        ),
                        "total_duration_seconds": (
                            execution.total_duration_seconds
                        ),
                        "comparison_status": (
                            comparison.status.value
                        ),
                        "divergence_score": (
                            comparison.divergence_score
                        ),
                        "anomaly_detected": (
                            comparison.status.value
                            == "divergent"
                        ),
                        "execution": execution.to_dict(),
                        "comparison": comparison.to_dict(),
                        "hypothesis": hypothesis.to_dict(),
                    }

                    safe_mutation_id = (
                        mutation.workflow_id.replace(
                            "/",
                            "_",
                        )
                    )

                    filename = (
                        f"hypothesis__{safe_mutation_id}"
                        f"__run_{run_index:02d}.json"
                    )

                    output = (
                        output_dirs["raw_directory"]
                        / filename
                    )

                    output.write_text(
                        json.dumps(record, indent=2),
                        encoding="utf-8",
                    )

                    record["output"] = str(output)
                    records.append(record)

        return records

    def run(self) -> dict[str, Any]:
        """Execute all enabled scientific evaluation groups."""

        config = self.config or self.load_configuration()
        self.ensure_output_directories()

        baseline_records = (
            self.run_baselines()
            if config["groups"]["baseline"]
            else []
        )

        generic_records = self.run_generic_mutations()

        hypothesis_records = (
            self.run_hypothesis_mutations()
        )

        summary = {
            "experiment_id": config["experiment_id"],
            "benchmark": config["benchmark"],
            "baseline_record_count": len(
                baseline_records
            ),
            "generic_mutation_record_count": len(
                generic_records
            ),
            "hypothesis_mutation_record_count": len(
                hypothesis_records
            ),
            "total_record_count": (
                len(baseline_records)
                + len(generic_records)
                + len(hypothesis_records)
            ),
            "records": {
                "baseline": baseline_records,
                "generic_mutation": generic_records,
                "hypothesis_mutation": hypothesis_records,
            },
        }

        output_dirs = self.ensure_output_directories()

        summary_path = (
            output_dirs["aggregated_directory"]
            / "experiment_summary.json"
        )

        summary_path.write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8",
        )

        summary["summary_path"] = str(summary_path)

        return summary

