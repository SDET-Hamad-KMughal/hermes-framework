"""Build HERMES state graphs from crawler results."""

from __future__ import annotations

from hermes.crawler.models import CrawlResult, Page
from hermes.state_graph.graph import StateGraph
from hermes.state_graph.state import ApplicationState
from hermes.state_graph.transition import StateTransition


class StateGraphBuilder:
    """Convert crawler output into a directed state graph."""

    def build(self, result: CrawlResult) -> StateGraph:
        """Build a state graph from one crawl result."""
        graph = StateGraph()
        states_by_url: dict[str, ApplicationState] = {}

        for page in result.pages:
            state = self._state_from_page(page)
            graph.add_state(state)
            states_by_url[page.url] = state

        for page in result.pages:
            self._add_transitions(
                graph,
                page,
                states_by_url[page.url],
                states_by_url,
            )

        return graph

    @staticmethod
    def _state_from_page(page: Page) -> ApplicationState:
        """Convert one crawled page into an application state."""
        return ApplicationState.create(
            url=page.url,
            title=page.title,
            depth=page.depth,
            action_count=len(page.actions),
            form_count=len(page.forms),
            metadata={
                "status_code": page.status_code,
                "link_count": len(page.links),
            },
        )

    @staticmethod
    def _add_transitions(
        graph: StateGraph,
        page: Page,
        source_state: ApplicationState,
        states_by_url: dict[str, ApplicationState],
    ) -> None:
        """Add transitions to crawler-discovered target states."""
        for action in page.actions:
            target_state = (
                states_by_url.get(action.target)
                if action.target
                else source_state
            )

            if target_state is None:
                continue

            graph.add_transition(
                StateTransition(
                    source_state_id=source_state.state_id,
                    target_state_id=target_state.state_id,
                    action_type=action.action_type,
                    label=action.label,
                    selector=action.selector,
                    semantic_target=action.target,
                    metadata={
                        "source_url": page.url,
                        "target_url": action.target,
                    },
                )
            )
