import pandas as pd
import pytest
from src.data.loader import RCADataLoader
from src.data.processor import TelemetryProcessor

RAW_DATA_DIR = "data/raw/RCAEval"
SAMPLE_INCIDENT = "re2ob_checkoutservice_cpu_1"


@pytest.fixture
def loaded_data():
    """Pytest fixture to load incident data once for test functions."""
    loader = RCADataLoader(RAW_DATA_DIR)
    return loader.load_incident_data(SAMPLE_INCIDENT)


def test_split_windows(loaded_data):
    """Verify window splitting partitions data correctly around inject_time."""
    metrics_df = loaded_data["metrics"]
    inject_time = loaded_data["inject_time"]

    baseline_df, fault_df = TelemetryProcessor.split_windows(
        metrics_df, inject_time
    )

    # Check total rows match
    assert len(baseline_df) + len(fault_df) == len(metrics_df)

    # Check boundary conditions
    assert (baseline_df["time"] < inject_time).all()
    assert (fault_df["time"] >= inject_time).all()


def test_compute_zscores(loaded_data):
    """Verify Z-score computation output shape and anomaly detection on fault column."""
    metrics_df = loaded_data["metrics"]
    inject_time = loaded_data["inject_time"]

    baseline_df, fault_df = TelemetryProcessor.split_windows(
        metrics_df, inject_time
    )
    z_df = TelemetryProcessor.compute_zscores(baseline_df, fault_df)

    # Output row count must match fault window row count
    assert len(z_df) == len(fault_df)

    # Column count must match original DataFrame
    assert len(z_df.columns) == len(metrics_df.columns)

    # Primary target metric (checkoutservice_cpu) must show significant anomaly
    assert z_df["checkoutservice_cpu"].max() > 3.0


def test_split_windows_missing_time_column():
    """Verify ValueError is raised if DataFrame lacks 'time' column."""
    invalid_df = pd.DataFrame({"cpu": [1.0, 2.0, 3.0]})

    with pytest.raises(ValueError):
        TelemetryProcessor.split_windows(invalid_df, inject_time=100)