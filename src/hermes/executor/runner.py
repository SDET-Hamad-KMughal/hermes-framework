"""Workflow execution engine."""

from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from hermes.executor.handlers import (
    BrowserExecutionContext,
    ExecutionHandler,
)
from hermes.executor.models import (
    ExecutionStepResult,
    WorkflowExecutionResult,
)
from hermes.mutation.models import Workflow


class WorkflowExecutionRunner:
    """Execute a workflow step by step."""

    def __init__(
        self,
        handler: ExecutionHandler | None = None,
    ) -> None:
        self.handler = handler or ExecutionHandler()

    def execute(
        self,
        context: BrowserExecutionContext,
        workflow: Workflow,
    ) -> WorkflowExecutionResult:

        started = datetime.now(UTC).isoformat()

        results = []

        for index, step in enumerate(workflow.steps):

            start = perf_counter()

            try:
                before = context.current_url

                self.handler.execute(
                    context,
                    step,
                )

                after = context.current_url

                success = True
                error = None

            except Exception as exc:

                before = context.current_url
                after = context.current_url

                success = False
                error = str(exc)

            duration = perf_counter() - start

            results.append(
                ExecutionStepResult(
                    step_index=index,
                    operation_type=step.operation_type,
                    label=step.label,
                    success=success,
                    url_before=before,
                    url_after=after,
                    duration_seconds=duration,
                    error=error,
                )
            )

        finished = datetime.now(UTC).isoformat()

        return WorkflowExecutionResult(
            workflow_id=workflow.workflow_id,
            workflow_name=workflow.name,
            steps=tuple(results),
            started_at=started,
            finished_at=finished,
        )
