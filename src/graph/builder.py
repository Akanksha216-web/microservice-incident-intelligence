import networkx as nx
import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ServiceGraphBuilder:
    """Builder class responsible for extracting microservice nodes and constructing directed call topology graphs."""

    @staticmethod
    def extract_service_names(df: pd.DataFrame) -> set[str]:
        """Extracts unique microservice names from telemetry metric column names.

        Args:
            df (pd.DataFrame): Telemetry DataFrame from metrics.parquet.

        Returns:
            set[str]: Set of unique microservice node identifiers.
        """
        services = set()
        for col in df.columns:
            if col == "time":
                continue

            # Metric names follow pattern: {service_name}_{metric_type}
            # e.g., 'checkoutservice_cpu', 'frontend-external_workload'
            parts = col.split("_")
            if len(parts) >= 2:
                service_name = parts[0]
                services.add(service_name)

        logger.info(
            f"Extracted {len(services)} unique microservices from telemetry metrics."
        )
        return services

    @staticmethod
    def build_default_onlineboutique_graph() -> nx.DiGraph:
        """Constructs the ground truth directed dependency graph for OnlineBoutique microservices.

        Direction convention: A -> B means Service A calls / depends on Service B.

        Returns:
            nx.DiGraph: Directed graph representing service invocation paths.
        """
        graph = nx.DiGraph()

        # Define call edges (Caller -> Callee) based on OnlineBoutique architecture
        edges = [
            ("frontend", "checkoutservice"),
            ("frontend", "recommendationservice"),
            ("frontend", "productcatalogservice"),
            ("frontend", "cartservice"),
            ("frontend", "shippingservice"),
            ("frontend", "currencyservice"),
            ("frontend", "adservice"),
            ("checkoutservice", "paymentservice"),
            ("checkoutservice", "emailservice"),
            ("checkoutservice", "currencyservice"),
            ("checkoutservice", "shippingservice"),
            ("checkoutservice", "productcatalogservice"),
            ("checkoutservice", "cartservice"),
            ("recommendationservice", "productcatalogservice"),
            ("cartservice", "redis"),
        ]

        graph.add_edges_from(edges)
        logger.info(
            f"Constructed OnlineBoutique graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} directed edges."
        )
        return graph