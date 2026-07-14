"""DOM extraction for pages visited by the HERMES crawler."""

from __future__ import annotations

from bs4 import BeautifulSoup
from playwright.sync_api import Page as BrowserPage

from hermes.crawler.models import (
    Action,
    Form,
    FormField,
    Link,
    Page as CrawledPage,
)
from hermes.crawler.url_manager import URLManager


class DOMExtractor:
    """Extract crawl-relevant elements from a loaded browser page."""

    def __init__(self, url_manager: URLManager) -> None:
        self.url_manager = url_manager

    def extract(self, browser_page: BrowserPage, depth: int) -> CrawledPage:
        """Extract a structured page model from a Playwright page."""

        current_url = self.url_manager.normalize(browser_page.url)
        html = browser_page.content()
        soup = BeautifulSoup(html, "lxml")

        return CrawledPage(
            url=current_url,
            title=browser_page.title(),
            depth=depth,
            links=self._extract_links(soup, current_url),
            forms=self._extract_forms(soup, current_url),
            actions=self._extract_actions(soup, current_url),
        )

    def _extract_links(
        self,
        soup: BeautifulSoup,
        current_url: str,
    ) -> list[Link]:
        """Extract hyperlinks from the document."""

        links: list[Link] = []

        for element in soup.find_all("a", href=True):
            raw_href = str(element.get("href", ""))
            normalized_href = self.url_manager.normalize(
                raw_href,
                base_url=current_url,
            )

            if not normalized_href:
                continue

            links.append(
                Link(
                    text=element.get_text(" ", strip=True),
                    href=normalized_href,
                    internal=self.url_manager.is_internal(normalized_href),
                )
            )

        return links

    def _extract_forms(
        self,
        soup: BeautifulSoup,
        current_url: str,
    ) -> list[Form]:
        """Extract forms and their input fields."""

        forms: list[Form] = []

        for form_element in soup.find_all("form"):
            raw_action = str(form_element.get("action", ""))
            action = self.url_manager.normalize(
                raw_action or current_url,
                base_url=current_url,
            )
            method = str(form_element.get("method", "GET")).upper()

            fields: list[FormField] = []

            for field_element in form_element.find_all(
                ["input", "textarea", "select"]
            ):
                field_type = self._field_type(field_element)
                field_name = str(
                    field_element.get("name")
                    or field_element.get("id")
                    or ""
                )

                fields.append(
                    FormField(
                        name=field_name,
                        field_type=field_type,
                        value=self._field_value(field_element),
                        required=field_element.has_attr("required"),
                    )
                )

            forms.append(
                Form(
                    action=action,
                    method=method,
                    fields=tuple(fields),
                )
            )

        return forms

    def _extract_actions(
        self,
        soup: BeautifulSoup,
        current_url: str,
    ) -> list[Action]:
        """Extract clickable and form-submission actions."""

        actions: list[Action] = []

        for button in soup.find_all("button"):
            action_type = (
                "submit"
                if str(button.get("type", "submit")).lower() == "submit"
                else "click"
            )

            actions.append(
                Action(
                    action_type=action_type,
                    label=button.get_text(" ", strip=True),
                    selector=self._selector(button),
                )
            )

        for input_element in soup.find_all(
            "input",
            attrs={"type": ["submit", "button"]},
        ):
            input_type = str(input_element.get("type", "")).lower()

            actions.append(
                Action(
                    action_type=(
                        "submit" if input_type == "submit" else "click"
                    ),
                    label=str(input_element.get("value", "")),
                    selector=self._selector(input_element),
                )
            )

        for link_element in soup.find_all("a", href=True):
            target = self.url_manager.normalize(
                str(link_element.get("href", "")),
                base_url=current_url,
            )

            if not target:
                continue

            actions.append(
                Action(
                    action_type="navigate",
                    label=link_element.get_text(" ", strip=True),
                    selector=self._selector(link_element),
                    target=target,
                )
            )

        return actions

    @staticmethod
    def _field_type(field_element) -> str:
        """Return a normalized field type."""

        if field_element.name == "textarea":
            return "textarea"

        if field_element.name == "select":
            return "select"

        return str(field_element.get("type", "text")).lower()

    @staticmethod
    def _field_value(field_element) -> str | None:
        """Return the current value associated with a field."""

        value = field_element.get("value")

        if value is None:
            return None

        return str(value)

    @staticmethod
    def _selector(element) -> str:
        """Generate a simple deterministic CSS selector."""

        element_id = element.get("id")

        if element_id:
            return f"#{element_id}"

        name = element.get("name")

        if name:
            return f'{element.name}[name="{name}"]'

        element_type = element.get("type")

        if element_type:
            return f'{element.name}[type="{element_type}"]'

        return str(element.name)
