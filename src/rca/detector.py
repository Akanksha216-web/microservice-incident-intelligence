import networkx as nx
import pandas as pd

from src.graph.builder import ServiceGraphBuilder
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RCADetector:
    """Root Cause Analysis engine combining telemetry Z-scores and dependency topology to rank fault candidates."""

    def __init__(self, graph: nx.DiGraph = None):
        """Initializes the RCA engine with a service dependency graph.

        Args:
            graph (nx.DiGraph, optional): Service call dependency graph.
        """
        self.graph = (
            graph
            if graph is not None
            else ServiceGraphBuilder.build_default_onlineboutique_graph()
        )
        logger.info(
            f"RCADetector initialized with dependency graph containing {len(self.graph)} nodes."
        )

    def rank_root_causes(
        self, z_scores_df: pd.DataFrame, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Ranks microservices by maximum anomalous feature deviation.

        Args:
            z_scores_df (pd.DataFrame): DataFrame containing Z-scores for all telemetry columns.
            top_k (int): Number of top root cause candidate services to return.

        Returns:
            list[tuple[str, float]]: Ranked list of (service_name, max_z_score) tuples.
        """
        service_scores: dict[str, float] = {}

        # Iterate through metric columns (excluding time)
        for col in z_scores_df.columns:
            if col == "time":
                continue

            # Parse service name from metric string (e.g. 'checkoutservice_cpu' -> 'checkoutservice')
            parts = col.split("_")
            if len(parts) < 2:
                continue

            service_name = parts[0]
            max_val = float(z_scores_df[col].abs().max())

            # Track maximum anomaly intensity per service
            if (
                service_name not in service_scores
                or max_val > service_scores[service_name]
            ):
                service_scores[service_name] = max_val

        # Sort services in descending order of maximum anomaly score
        ranked_services = sorted(
            service_scores.items(), key=lambda item: item[1], reverse=True
        )

        logger.info(
            f"Evaluated {len(service_scores)} services. Top root cause: {ranked_services[0] if ranked_services else 'None'}"
        )
        return ranked_services[:top_k]