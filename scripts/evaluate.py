import json
import logging
import time
from pathlib import Path
import pandas as pd

from src.data.loader import RCADatasetLoader
from src.data.processor import TelemetryProcessor
from src.rca.detector import RCADetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_evaluation(detector: RCADetector, cases: list, processor: TelemetryProcessor, method: str):
    top1_correct = 0
    top3_correct = 0
    mrr_sum = 0.0
    total = len(cases)

    for case in cases:
        csv_path = case["telemetry_path"]
        ground_truth = case["ground_truth_service"]

        try:
            df = pd.read_csv(csv_path)
            z_df = processor.compute_z_scores(df)
            rankings = detector.rank_root_causes(z_df, top_k=5, method=method)
            ranked_services = [s[0] for s in rankings]

            if ranked_services and ranked_services[0] == ground_truth:
                top1_correct += 1

            if ground_truth in ranked_services[:3]:
                top3_correct += 1

            if ground_truth in ranked_services:
                rank = ranked_services.index(ground_truth) + 1
                mrr_sum += 1.0 / rank

        except Exception as e:
            logger.error(f"Error evaluating case {case.get('case_id')}: {e}")

    acc1 = (top1_correct / total) * 100 if total > 0 else 0
    acc3 = (top3_correct / total) * 100 if total > 0 else 0
    mrr = mrr_sum / total if total > 0 else 0

    return {"Acc@1": acc1, "Acc@3": acc3, "MRR": mrr, "total": total}


def main():
    loader = RCADatasetLoader(data_dir="data")
    cases = loader.load_benchmark_cases()

    if not cases:
        logger.error("No test cases loaded. Check data path.")
        return

    processor = TelemetryProcessor(window_size=30)
    detector = RCADetector()

    logger.info(f"Starting evaluation across {len(cases)} incidents...")

    zscore_results = run_evaluation(detector, cases, processor, method="max_zscore")
    pagerank_results = run_evaluation(detector, cases, processor, method="pagerank")

    print("\n" + "=" * 62)
    print(f"{'RCA BENCHMARK EVALUATION COMPARISON':^62}")
    print("=" * 62)
    print(f"{'Metric':<25} | {'Max Z-Score':<15} | {'PageRank':<15}")
    print("-" * 62)
    print(f"{'Top-1 Accuracy (Acc@1)':<25} | {zscore_results['Acc@1']:>14.2f}% | {pagerank_results['Acc@1']:>14.2f}%")
    print(f"{'Top-3 Accuracy (Acc@3)':<25} | {zscore_results['Acc@3']:>14.2f}% | {pagerank_results['Acc@3']:>14.2f}%")
    print(f"{'Mean Reciprocal Rank (MRR)':<25} | {zscore_results['MRR']:>15.4f} | {pagerank_results['MRR']:>15.4f}")
    print("=" * 62)


if __name__ == "__main__":
    main()