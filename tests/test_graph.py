import networkx as nx
import pandas as pd
from src.graph.builder import ServiceGraphBuilder


def test_extract_service_names():
    """Verify service names are correctly parsed from telemetry metric headers."""
    mock_df = pd.DataFrame(
        columns=["time", "checkoutservice_cpu", "frontend_latency-50", "cartservice_mem"]
    )
    services = ServiceGraphBuilder.extract_service_names(mock_df)

    assert "time" not in services
    assert services == {"checkoutservice", "frontend", "cartservice"}


def test_build_default_onlineboutique_graph():
    """Verify default graph topology structure, node counts, and directional relationships."""
    graph = ServiceGraphBuilder.build_default_onlineboutique_graph()

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 11
    assert graph.number_of_edges() == 15

    # Check key architectural edges
    assert graph.has_edge("frontend", "checkoutservice")
    assert graph.has_edge("checkoutservice", "paymentservice")
    assert graph.has_edge("cartservice", "redis")

    # Ensure direction is not bidirectional for single call path
    assert not graph.has_edge("checkoutservice", "frontend")