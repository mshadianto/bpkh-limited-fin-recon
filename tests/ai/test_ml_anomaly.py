"""Tests for aurix.ai.ml_anomaly — MLAnomalyDetector."""

import pandas as pd
import numpy as np
import pytest

from aurix.ai.ml_anomaly import MLAnomalyDetector


@pytest.fixture
def detector():
    return MLAnomalyDetector(contamination=0.1)


# ---------------------------------------------------------------------------
# Z-Score Detection
# ---------------------------------------------------------------------------

class TestZScoreAnomalies:
    def test_returns_list(self, detector, large_coa_recon_df):
        result = detector.detect_zscore_anomalies(large_coa_recon_df)
        assert isinstance(result, list)

    def test_anomaly_structure(self, detector, large_coa_recon_df):
        result = detector.detect_zscore_anomalies(large_coa_recon_df)
        if result:
            keys = set(result[0].keys())
            assert {"severity", "type", "coa", "description", "amount", "z_score", "method"}.issubset(keys)

    def test_method_field(self, detector, large_coa_recon_df):
        result = detector.detect_zscore_anomalies(large_coa_recon_df)
        for a in result:
            assert a["method"] == "z_score"

    def test_detects_outliers(self, detector, large_coa_recon_df):
        result = detector.detect_zscore_anomalies(large_coa_recon_df)
        assert len(result) > 0

    def test_severity_values(self, detector, large_coa_recon_df):
        result = detector.detect_zscore_anomalies(large_coa_recon_df)
        for a in result:
            assert a["severity"] in {"HIGH", "MEDIUM"}

    def test_higher_threshold_fewer_anomalies(self, detector, large_coa_recon_df):
        low = detector.detect_zscore_anomalies(large_coa_recon_df, threshold=2.0)
        high = detector.detect_zscore_anomalies(large_coa_recon_df, threshold=5.0)
        assert len(high) <= len(low)

    def test_too_few_rows(self, detector):
        df = pd.DataFrame({
            "COA": [1, 2],
            "Net_Variance": [100, 200],
            "Debit_Variance": [10, 20],
            "Credit_Variance": [5, 10],
        })
        result = detector.detect_zscore_anomalies(df)
        assert result == []

    def test_zero_std(self, detector):
        df = pd.DataFrame({
            "COA": [1, 2, 3, 4],
            "Net_Variance": [100.0, 100.0, 100.0, 100.0],
            "Debit_Variance": [50.0, 50.0, 50.0, 50.0],
            "Credit_Variance": [25.0, 25.0, 25.0, 25.0],
        })
        result = detector.detect_zscore_anomalies(df)
        assert result == []


# ---------------------------------------------------------------------------
# Isolation Forest Detection
# ---------------------------------------------------------------------------

class TestIsolationForestAnomalies:
    def test_returns_list(self, detector, large_coa_recon_df):
        result = detector.detect_isolation_forest_anomalies(large_coa_recon_df)
        assert isinstance(result, list)

    def test_anomaly_structure(self, detector, large_coa_recon_df):
        result = detector.detect_isolation_forest_anomalies(large_coa_recon_df)
        if result:
            keys = set(result[0].keys())
            assert {"severity", "type", "coa", "description", "amount", "anomaly_score", "method"}.issubset(keys)

    def test_method_field(self, detector, large_coa_recon_df):
        result = detector.detect_isolation_forest_anomalies(large_coa_recon_df)
        for a in result:
            assert a["method"] == "isolation_forest"

    def test_too_few_rows(self, detector):
        df = pd.DataFrame({
            "COA": [1, 2, 3],
            "Net_Variance": [100, 200, 300],
            "Debit_Variance": [10, 20, 30],
            "Credit_Variance": [5, 10, 15],
            "Manual_TxnCount": [1, 2, 3],
            "Daftra_TxnCount": [1, 2, 3],
            "Abs_Variance": [100, 200, 300],
        })
        result = detector.detect_isolation_forest_anomalies(df)
        assert result == []


# ---------------------------------------------------------------------------
# detect_all
# ---------------------------------------------------------------------------

class TestDetectAll:
    def test_merges_results(self, detector, large_coa_recon_df):
        result = detector.detect_all(large_coa_recon_df)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_max_15(self, detector, large_coa_recon_df):
        result = detector.detect_all(large_coa_recon_df)
        assert len(result) <= 15

    def test_sorted_by_severity(self, detector, large_coa_recon_df):
        result = detector.detect_all(large_coa_recon_df)
        severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        ranks = [severity_rank.get(a["severity"], 3) for a in result]
        assert ranks == sorted(ranks)

    def test_deduplicates(self, detector, large_coa_recon_df):
        result = detector.detect_all(large_coa_recon_df)
        seen = set()
        for a in result:
            key = (a["coa"], a["method"])
            assert key not in seen, f"Duplicate: {key}"
            seen.add(key)
