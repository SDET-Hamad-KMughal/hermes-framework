"""Tests for DOM extraction."""

from unittest.mock import MagicMock

from hermes.crawler.dom_extractor import DOMExtractor
from hermes.crawler.url_manager import URLManager


HTML = """
<!doctype html>
<html>
<head>
    <title>Products</title>
</head>
<body>
    <a id="cart-link" href="/cart">Cart</a>
    <a href="https://example.com/help">External Help</a>
    <a href="javascript:void(0)">Ignored</a>

    <form action="/login" method="post">
        <input
            id="email"
            name="email"
            type="email"
            value="user@example.com"
            required
        >
        <input name="password" type="password" required>
        <select name="role">
            <option value="customer">Customer</option>
        </select>
        <textarea name="notes"></textarea>
        <button id="login-button" type="submit">Login</button>
    </form>

    <input id="refresh-button" type="button" value="Refresh">
</body>
</html>
"""


def make_browser_page() -> MagicMock:
    page = MagicMock()
    page.url = "http://127.0.0.1:5000/products"
    page.title.return_value = "Products"
    page.content.return_value = HTML
    return page


def test_extract_page_metadata() -> None:
    manager = URLManager("http://127.0.0.1:5000/")
    extractor = DOMExtractor(manager)

    result = extractor.extract(make_browser_page(), depth=2)

    assert result.url == "http://127.0.0.1:5000/products"
    assert result.title == "Products"
    assert result.depth == 2


def test_extract_links() -> None:
    manager = URLManager("http://127.0.0.1:5000/")
    extractor = DOMExtractor(manager)

    result = extractor.extract(make_browser_page(), depth=0)

    assert len(result.links) == 2
    assert result.links[0].text == "Cart"
    assert result.links[0].href == "http://127.0.0.1:5000/cart"
    assert result.links[0].internal is True
    assert result.links[1].internal is False


def test_extract_form_and_fields() -> None:
    manager = URLManager("http://127.0.0.1:5000/")
    extractor = DOMExtractor(manager)

    result = extractor.extract(make_browser_page(), depth=0)

    assert len(result.forms) == 1

    form = result.forms[0]

    assert form.action == "http://127.0.0.1:5000/login"
    assert form.method == "POST"
    assert len(form.fields) == 4
    assert form.fields[0].name == "email"
    assert form.fields[0].field_type == "email"
    assert form.fields[0].value == "user@example.com"
    assert form.fields[0].required is True
    assert form.fields[2].field_type == "select"
    assert form.fields[3].field_type == "textarea"


def test_extract_actions() -> None:
    manager = URLManager("http://127.0.0.1:5000/")
    extractor = DOMExtractor(manager)

    result = extractor.extract(make_browser_page(), depth=0)

    assert len(result.actions) == 4

    login_action = result.actions[0]
    refresh_action = result.actions[1]
    cart_action = result.actions[2]

    assert login_action.action_type == "submit"
    assert login_action.label == "Login"
    assert login_action.selector == "#login-button"

    assert refresh_action.action_type == "click"
    assert refresh_action.selector == "#refresh-button"

    assert cart_action.action_type == "navigate"
    assert cart_action.target == "http://127.0.0.1:5000/cart"


def test_generated_selectors() -> None:
    manager = URLManager("http://127.0.0.1:5000/")
    extractor = DOMExtractor(manager)

    result = extractor.extract(make_browser_page(), depth=0)

    assert result.actions[0].selector == "#login-button"
    assert result.actions[1].selector == "#refresh-button"
    assert result.actions[2].selector == "#cart-link"
