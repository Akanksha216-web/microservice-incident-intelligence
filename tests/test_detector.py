import pandas as pd
from src.rca.detector import RCADetector


def test_detector_initialization():
    """Verify default graph initialization in RCADetector."""
    detector = RCADetector()
    assert len(detector.graph.nodes) == 11
    assert len(detector.graph.edges) == 15


def test_rank_root_causes_max_zscore():
    """Verify services are ranked accurately based on maximum absolute Z-score."""
    mock_z_scores = pd.DataFrame(
        {
            "time": [100, 101],
            "checkoutservice_cpu": [150.0, 200.0],
            "frontend_latency": [10.0, 50.0],
            "emailservice_mem": [1.2, -5.0],
        }
    )

    detector = RCADetector()
    ranked = detector.rank_root_causes(mock_z_scores, top_k=3, method="max_zscore")

    assert len(ranked) == 3
    assert ranked[0] == ("checkoutservice", 200.0)
    assert ranked[1] == ("frontend", 50.0)
    assert ranked[2] == ("emailservice", 5.0)


def test_rank_root_causes_pagerank():
    """Verify PageRank ranking returns top candidates using dependency topology."""
    mock_z_scores = pd.DataFrame(
        {
            "time": [100],
            "checkoutservice_cpu": [200.0],
            "frontend_latency": [50.0],
            "emailservice_mem": [5.0],
        }
    )

    detector = RCADetector()
    ranked = detector.rank_root_causes(mock_z_scores, top_k=3, method="pagerank")

    assert len(ranked) == 3
    assert isinstance(ranked[0][0], str)
    assert isinstance(ranked[0][1], float)


def test_rank_root_causes_top_k():
    """Verify top_k parameter restricts result size correctly."""
    mock_z_scores = pd.DataFrame(
        {
            "time": [100],
            "checkoutservice_cpu": [200.0],
            "frontend_latency": [50.0],
            "emailservice_mem": [5.0],
        }
    )

    detector = RCADetector()
    ranked = detector.rank_root_causes(mock_z_scores, top_k=1)

    assert len(ranked) == 1
    assert ranked[0][0] == "checkoutservice"