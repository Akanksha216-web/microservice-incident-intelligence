import pandas as pd
import pytest
from src.data.loader import RCADataLoader

# Test Constants
RAW_DATA_DIR = "data/raw/RCAEval"
SAMPLE_INCIDENT = "re2ob_checkoutservice_cpu_1"


def test_data_loader_initialization():
    """Verify loader initializes successfully with valid path and raises error for invalid path."""
    loader = RCADataLoader(RAW_DATA_DIR)
    assert loader.raw_data_dir.exists()

    with pytest.raises(FileNotFoundError):
        RCADataLoader("data/raw/non_existent_folder")


def test_load_inject_time():
    """Verify inject_time is loaded as an integer."""
    loader = RCADataLoader(RAW_DATA_DIR)
    inject_time = loader.load_inject_time(SAMPLE_INCIDENT)

    assert isinstance(inject_time, int)
    assert inject_time > 0


def test_load_metrics():
    """Verify metrics DataFrame is loaded correctly with required columns."""
    loader = RCADataLoader(RAW_DATA_DIR)
    metrics_df = loader.load_metrics(SAMPLE_INCIDENT)

    assert isinstance(metrics_df, pd.DataFrame)
    assert not metrics_df.empty
    assert "time" in metrics_df.columns


def test_load_incident_data():
    """Verify full incident data loader returns complete dictionary structure."""
    loader = RCADataLoader(RAW_DATA_DIR)
    data = loader.load_incident_data(SAMPLE_INCIDENT)

    assert "incident_name" in data
    assert "inject_time" in data
    assert "metrics" in data
    assert isinstance(data["metrics"], pd.DataFrame)