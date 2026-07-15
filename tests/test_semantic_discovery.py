"""Tests for semantic-operation discovery."""

from hermes.semantic.discovery import SemanticOperationDiscovery
from hermes.semantic.models import OperationType
from hermes.state_graph.graph import StateGraph
from hermes.state_graph.state import ApplicationState
from hermes.state_graph.transition import StateTransition


def make_graph() -> StateGraph:
    graph = StateGraph()

    home = ApplicationState.create(
        "http://127.0.0.1:5000/",
        "Home",
        0,
    )
    login = ApplicationState.create(
        "http://127.0.0.1:5000/login",
        "Login",
        1,
    )
    products = ApplicationState.create(
        "http://127.0.0.1:5000/products",
        "Products",
        1,
    )
    cart = ApplicationState.create(
        "http://127.0.0.1:5000/cart",
        "Cart",
        2,
    )

    for state in (home, login, products, cart):
        graph.add_state(state)

    graph.add_transition(
        StateTransition(
            source_state_id=home.state_id,
            target_state_id=login.state_id,
            action_type="navigate",
            label="Sign In Here",
            selector="#login-link",
            semantic_target=login.url,
        )
    )

    graph.add_transition(
        StateTransition(
            source_state_id=products.state_id,
            target_state_id=cart.state_id,
            action_type="submit",
            label="Add to Cart",
            selector=".add-to-cart",
            semantic_target=cart.url,
        )
    )

    return graph


def test_discovery_creates_operation_per_transition() -> None:
    graph = make_graph()

    operations = SemanticOperationDiscovery().discover(graph)

    assert len(operations) == 2


def test_discovery_classifies_login() -> None:
    operations = SemanticOperationDiscovery().discover(
        make_graph()
    )

    login = next(
        item
        for item in operations
        if item.operation_type is OperationType.LOGIN
    )

    assert login.label == "Sign In Here"
    assert login.confidence >= 0.7
    assert login.evidence


def test_discovery_classifies_add_to_cart() -> None:
    operations = SemanticOperationDiscovery().discover(
        make_graph()
    )

    add_to_cart = next(
        item
        for item in operations
        if item.operation_type is OperationType.ADD_TO_CART
    )

    assert add_to_cart.label == "Add to Cart"
    assert add_to_cart.selector == ".add-to-cart"


def test_discovery_preserves_transition_metadata() -> None:
    operations = SemanticOperationDiscovery().discover(
        make_graph()
    )

    operation = operations[0]

    assert operation.metadata["action_type"] == "navigate"
    assert operation.metadata["semantic_target"]


def test_discovery_handles_empty_graph() -> None:
    operations = SemanticOperationDiscovery().discover(
        StateGraph()
    )

    assert operations == []
