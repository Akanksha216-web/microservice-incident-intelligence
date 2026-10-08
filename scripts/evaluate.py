import sys
from pathlib import Path

# Add project root to path for direct script execution
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data.loader import RCADataLoader
from src.data.processor import TelemetryProcessor
from src.rca.detector import RCADetector
from src.utils.logger import setup_logger

logger = setup_logger("RCAEvaluation")


def run_evaluation(data_dir: str = "data/raw/RCAEval") -> dict[str, float]:
    """Runs end-to-end RCA evaluation over all incident dataset directories.

    Args:
        data_dir (str): Base raw data path containing incident folders.

    Returns:
        dict[str, float]: Evaluation metrics summary dictionary.
    """
    raw_path = Path(data_dir)
    if not raw_path.exists():
        logger.error(f"Dataset path not found: {raw_path}")
        return {}

    loader = RCADataLoader(raw_path)
    detector = RCADetector()

    # Discover all incident folders
    incident_folders = [
        f.name for f in raw_path.iterdir() if f.is_dir() and (f / "inject_time.txt").exists()
    ]

    if not incident_folders:
        logger.warning("No valid incident folders found in raw data directory.")
        return {}

    logger.info(f"Discovered {len(incident_folders)} evaluation incident(s).")

    top1_hits = 0
    top3_hits = 0
    mrr_total = 0.0

    for incident in incident_folders:
        logger.info(f"--- Evaluating Incident: {incident} ---")
        
        # Load incident data
        data = loader.load_incident_data(incident)
        
        # Split windowing & Z-score normalization
        baseline_df, fault_df = TelemetryProcessor.split_windows(data["metrics"], data["inject_time"])
        z_df = TelemetryProcessor.compute_zscores(baseline_df, fault_df)

        # Predict top candidate root cause rankings
        rankings = detector.rank_root_causes(z_df, top_k=5)
        ranked_services = [service for service, _ in rankings]

        # Extract actual injected service target from incident name convention
        # Format pattern: {dataset}_{target_service}_{fault_type}_{id}
        parts = incident.split("_")
        ground_truth_service = parts[1] if len(parts) >= 2 else ""

        # Compute accuracy scores
        rank = -1
        if ground_truth_service in ranked_services:
            rank = ranked_services.index(ground_truth_service) + 1
            mrr_total += 1.0 / rank

            if rank == 1:
                top1_hits += 1
            if rank <= 3:
                top3_hits += 1

        logger.info(
            f"Ground Truth: '{ground_truth_service}' | Rank: {rank if rank != -1 else 'Not in Top 5'} | Top 3 Predictions: {ranked_services[:3]}"
        )

    total_incidents = len(incident_folders)
    acc_top1 = (top1_hits / total_incidents) * 100
    acc_top3 = (top3_hits / total_incidents) * 100
    mrr = mrr_total / total_incidents

    print("\n==================================================")
    print("           RCA BENCHMARK EVALUATION RESULTS       ")
    print("==================================================")
    print(f"Total Evaluated Incidents: {total_incidents}")
    print(f"Top-1 Accuracy (Acc@1):    {acc_top1:.2f}%")
    print(f"Top-3 Accuracy (Acc@3):    {acc_top3:.2f}%")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")
    print("==================================================\n")

    return {"acc_top1": acc_top1, "acc_top3": acc_top3, "mrr": mrr}


if __name__ == "__main__":
    run_evaluation()