"""Ground-truth anomaly loader for HERMES."""

from __future__ import annotations

import json
from pathlib import Path

from hermes.evaluation.ground_truth.models import (
    GroundTruthAnomaly,
)


def load_ground_truth(
    path: str | Path,
) -> list[GroundTruthAnomaly]:
    """Load seeded anomalies from a JSON file."""

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"ground-truth file not found: {file_path}"
        )

    payload = json.loads(
        file_path.read_text(encoding="utf-8")
    )

    anomalies = payload.get("anomalies", [])

    return [
        GroundTruthAnomaly(**item)
        for item in anomalies
    ]
