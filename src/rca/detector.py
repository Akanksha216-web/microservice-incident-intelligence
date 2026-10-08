import networkx as nx
import numpy as np
import pandas as pd

from src.graph.builder import ServiceGraphBuilder
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RCADetector:
    """Root Cause Analysis engine combining telemetry Z-scores and dependency topology to rank fault candidates."""

    def __init__(self, graph: nx.DiGraph = None):
        self.graph = (
            graph
            if graph is not None
            else ServiceGraphBuilder.build_default_onlineboutique_graph()
        )
        logger.info(
            f"RCADetector initialized with dependency graph containing {len(self.graph)} nodes."
        )

    def extract_service_max_zscores(
        self, z_scores_df: pd.DataFrame
    ) -> dict[str, float]:
        service_scores: dict[str, float] = {}

        # Normalize graph node names for fuzzy key lookup (e.g. removing hyphens/underscores)
        graph_nodes = list(self.graph.nodes())

        for col in z_scores_df.columns:
            if col == "time":
                continue

            max_val = float(z_scores_df[col].abs().max())

            # Match telemetry column against graph node names
            matched_node = None
            col_clean = col.lower().replace("-", "").replace("_", "")

            for node in graph_nodes:
                node_clean = node.lower().replace("-", "").replace("_", "")
                if node_clean in col_clean or col_clean.startswith(node_clean):
                    matched_node = node
                    break

            # Fallback to prefix split if no direct graph node matched
            if not matched_node:
                parts = col.split("_")
                matched_node = parts[0] if len(parts) >= 2 else col

            if matched_node not in service_scores or max_val > service_scores[matched_node]:
                service_scores[matched_node] = max_val

        return service_scores

    def rank_root_causes(
        self,
        z_scores_df: pd.DataFrame,
        top_k: int = 5,
        method: str = "pagerank",
        alpha: float = 0.85,
    ) -> list[tuple[str, float]]:
        service_zscores = self.extract_service_max_zscores(z_scores_df)

        if not service_zscores:
            logger.warning("No valid service scores extracted from telemetry.")
            return []

        if method == "max_zscore":
            ranked_services = sorted(
                service_zscores.items(), key=lambda x: x[1], reverse=True
            )
            return ranked_services[:top_k]

        elif method == "pagerank":
            graph_nodes = set(self.graph.nodes())
            
            # Map personalization scores strictly over existing graph nodes
            personalization = {}
            total_score = 0.0

            for node in graph_nodes:
                score = service_zscores.get(node, 0.0)
                personalization[node] = score
                total_score += score

            # Normalize personalization vector
            if total_score > 0:
                personalization = {k: v / total_score for k, v in personalization.items()}
            else:
                personalization = {k: 1.0 / len(graph_nodes) for k in graph_nodes}

            try:
                # Reverse graph edges so propagation flows back to root cause nodes
                reversed_graph = self.graph.reverse(copy=True)
                
                pr_scores = nx.pagerank(
                    reversed_graph,
                    alpha=alpha,
                    personalization=personalization,
                    max_iter=500,
                )
            except Exception as e:
                logger.warning(
                    f"PageRank computation failed ({e}), falling back to max_zscore."
                )
                pr_scores = service_zscores

            ranked_services = sorted(
                pr_scores.items(), key=lambda x: x[1], reverse=True
            )
            return ranked_services[:top_k]

        else:
            raise ValueError(f"Unsupported ranking method: {method}")