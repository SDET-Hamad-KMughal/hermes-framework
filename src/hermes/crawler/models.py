"""Data models produced by the HERMES crawler."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Link:
    """A hyperlink discovered on a page."""

    text: str
    href: str
    internal: bool


@dataclass(frozen=True, slots=True)
class FormField:
    """An input field discovered inside a form."""

    name: str
    field_type: str
    value: str | None = None
    required: bool = False


@dataclass(frozen=True, slots=True)
class Form:
    """A form discovered on a page."""

    action: str
    method: str
    fields: tuple[FormField, ...] = ()


@dataclass(frozen=True, slots=True)
class Action:
    """An executable user-interface action."""

    action_type: str
    label: str
    selector: str
    target: str | None = None


@dataclass(slots=True)
class Page:
    """A web page and the crawlable elements discovered on it."""

    url: str
    title: str
    depth: int
    status_code: int | None = None
    links: list[Link] = field(default_factory=list)
    forms: list[Form] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the page and nested models into serializable data."""
        return asdict(self)


@dataclass(slots=True)
class CrawlResult:
    """Complete output of one crawler execution."""

    start_url: str
    pages: list[Page] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        """Return the number of successfully recorded pages."""
        return len(self.pages)

    @property
    def link_count(self) -> int:
        """Return the total number of discovered links."""
        return sum(len(page.links) for page in self.pages)

    @property
    def form_count(self) -> int:
        """Return the total number of discovered forms."""
        return sum(len(page.forms) for page in self.pages)

    @property
    def action_count(self) -> int:
        """Return the total number of discovered actions."""
        return sum(len(page.actions) for page in self.pages)

    def to_dict(self) -> dict[str, Any]:
        """Convert the crawl result into serializable data."""
        return asdict(self)