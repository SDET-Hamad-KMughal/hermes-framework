"""Tests for ground-truth anomaly models."""

import pytest

from hermes.evaluation.ground_truth.models import (
    GroundTruthAnomaly,
)


def make() -> GroundTruthAnomaly:
    return GroundTruthAnomaly(
        anomaly_id="GT001",
        workflow_id="checkout",
        mutation_strategy="remove_login",
        expected_behavior="reject",
        description="Checkout without login.",
        oracle="checkout denied",
    )


def test_create():
    gt = make()

    assert gt.anomaly_id == "GT001"
    assert gt.workflow_id == "checkout"


def test_to_dict():
    d = make().to_dict()

    assert d["oracle"] == "checkout denied"


@pytest.mark.parametrize(
    "field",
    [
        "anomaly_id",
        "workflow_id",
        "mutation_strategy",
        "expected_behavior",
        "description",
        "oracle",
    ],
)
def test_empty(field):
    values = make().to_dict()
    values[field] = ""

    with pytest.raises(ValueError):
        GroundTruthAnomaly(**values)
