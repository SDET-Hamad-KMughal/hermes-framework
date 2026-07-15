"""Scientific experiment orchestration for HERMES."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
