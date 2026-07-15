"""Behavior comparison engine for HERMES."""

from __future__ import annotations

from dataclasses import dataclass

from hermes.comparator.models import (
    BehaviorComparisonResult,
    ComparisonStatus,
    SignalComparison,
)
from hermes.executor.models import WorkflowExecutionResult


@dataclass(frozen=True, slots=True)
class ComparatorConfig:
    """Configuration for workflow behavior comparison."""

    divergence_threshold: float = 0.30
    duration_tolerance_seconds: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.divergence_threshold <= 1.0:
            raise ValueError(
                "divergence_threshold must be between 0 and 1"
            )

        if self.duration_tolerance_seconds < 0:
            raise ValueError(
                "duration_tolerance_seconds must not be negative"
            )


class BehaviorComparator:
    """Compare baseline and mutated workflow executions."""

    def __init__(
        self,
        config: ComparatorConfig | None = None,
    ) -> None:
        self.config = config or ComparatorConfig()

    def compare(
        self,
        baseline: WorkflowExecutionResult,
        mutated: WorkflowExecutionResult,
    ) -> BehaviorComparisonResult:
        """Compare two workflow execution traces."""

        signals = (
            self._compare_success(baseline, mutated),
            self._compare_failed_steps(baseline, mutated),
            self._compare_final_url(baseline, mutated),
            self._compare_step_outcomes(baseline, mutated),
            self._compare_duration(baseline, mutated),
        )

        divergence_score = self._calculate_score(signals)

        status = (
            ComparisonStatus.DIVERGENT
            if divergence_score >= self.config.divergence_threshold
            else ComparisonStatus.EQUIVALENT
        )

        return BehaviorComparisonResult(
            baseline_workflow_id=baseline.workflow_id,
            mutated_workflow_id=mutated.workflow_id,
            status=status,
            signals=signals,
            divergence_score=divergence_score,
        )

    @staticmethod
    def _compare_success(
        baseline: WorkflowExecutionResult,
        mutated: WorkflowExecutionResult,
    ) -> SignalComparison:
        return SignalComparison(
            signal_name="workflow_success",
            baseline_value=baseline.success,
            mutated_value=mutated.success,
            equivalent=baseline.success == mutated.success,
            weight=2.0,
        )

    @staticmethod
    def _compare_failed_steps(
        baseline: WorkflowExecutionResult,
        mutated: WorkflowExecutionResult,
    ) -> SignalComparison:
        return SignalComparison(
            signal_name="failed_steps",
            baseline_value=baseline.failed_steps,
            mutated_value=mutated.failed_steps,
            equivalent=baseline.failed_steps == mutated.failed_steps,
            weight=1.5,
        )

    @staticmethod
    def _final_url(
        result: WorkflowExecutionResult,
    ) -> str | None:
        if not result.steps:
            return None

        return result.steps[-1].url_after

    def _compare_final_url(
        self,
        baseline: WorkflowExecutionResult,
        mutated: WorkflowExecutionResult,
    ) -> SignalComparison:
        baseline_url = self._final_url(baseline)
        mutated_url = self._final_url(mutated)

        return SignalComparison(
            signal_name="final_url",
            baseline_value=baseline_url,
            mutated_value=mutated_url,
            equivalent=baseline_url == mutated_url,
            weight=2.0,
        )

    @staticmethod
    def _compare_step_outcomes(
        baseline: WorkflowExecutionResult,
        mutated: WorkflowExecutionResult,
    ) -> SignalComparison:
        baseline_outcomes = tuple(
            step.success for step in baseline.steps
        )
        mutated_outcomes = tuple(
            step.success for step in mutated.steps
        )

        return SignalComparison(
            signal_name="step_outcomes",
            baseline_value=baseline_outcomes,
            mutated_value=mutated_outcomes,
            equivalent=baseline_outcomes == mutated_outcomes,
            weight=1.5,
        )

    def _compare_duration(
        self,
        baseline: WorkflowExecutionResult,
        mutated: WorkflowExecutionResult,
    ) -> SignalComparison:
        difference = abs(
            baseline.total_duration_seconds
            - mutated.total_duration_seconds
        )

        return SignalComparison(
            signal_name="execution_duration",
            baseline_value=baseline.total_duration_seconds,
            mutated_value=mutated.total_duration_seconds,
            equivalent=(
                difference
                <= self.config.duration_tolerance_seconds
            ),
            weight=0.5,
            details=f"difference_seconds={difference:.6f}",
        )

    @staticmethod
    def _calculate_score(
        signals: tuple[SignalComparison, ...],
    ) -> float:
        total_weight = sum(signal.weight for signal in signals)

        if total_weight == 0:
            return 0.0

        divergent_weight = sum(
            signal.weight
            for signal in signals
            if not signal.equivalent
        )

        return divergent_weight / total_weight
