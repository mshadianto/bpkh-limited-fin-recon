"""Tests for aurix.ai.analyzer — AIAnalyzer."""

import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from aurix.config import ReconciliationStatus
from aurix.ai.analyzer import AIAnalyzer


@pytest.fixture
def mock_analyzer():
    """AIAnalyzer with mocked LLMProvider (no real API calls)."""
    with patch("aurix.ai.analyzer.LLMProvider") as MockProvider:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "Mocked LLM response."
        MockProvider.return_value = mock_instance
        analyzer = AIAnalyzer(api_key="fake-test-key")
        yield analyzer, mock_instance


@pytest.fixture
def anomaly_coa_df():
    """COA recon DataFrame with variance rows for anomaly detection tests."""
    np.random.seed(99)
    n = 20
    net_var = np.random.normal(0, 100, n)
    # Inject an extreme outlier
    net_var[0] = 50000.0
    statuses = [ReconciliationStatus.VARIANCE.value] * n

    # Add some unmatched rows
    extra = pd.DataFrame({
        "COA": [9001, 9002],
        "Account_Name": ["Big Manual", "Big Daftra"],
        "Manual_Debit": [15000.0, 0.0],
        "Manual_Credit": [0.0, 0.0],
        "Manual_Net": [15000.0, 0.0],
        "Manual_TxnCount": [5, 0],
        "Daftra_Debit": [0.0, 20000.0],
        "Daftra_Credit": [0.0, 0.0],
        "Daftra_Net": [0.0, 20000.0],
        "Daftra_TxnCount": [0, 3],
        "Net_Variance": [15000.0, -20000.0],
        "Abs_Variance": [15000.0, 20000.0],
        "Status": [
            ReconciliationStatus.UNMATCHED_MANUAL.value,
            ReconciliationStatus.UNMATCHED_DAFTRA.value,
        ],
    })

    main = pd.DataFrame({
        "COA": list(range(1000, 1000 + n)),
        "Account_Name": [f"Acc_{i}" for i in range(n)],
        "Manual_Debit": np.abs(net_var) + 100,
        "Manual_Credit": [100.0] * n,
        "Manual_Net": net_var,
        "Manual_TxnCount": [5] * n,
        "Daftra_Debit": [100.0] * n,
        "Daftra_Credit": [100.0] * n,
        "Daftra_Net": [0.0] * n,
        "Daftra_TxnCount": [5] * n,
        "Net_Variance": net_var,
        "Abs_Variance": np.abs(net_var),
        "Status": statuses,
    })

    return pd.concat([main, extra], ignore_index=True)


@pytest.fixture
def sample_summary():
    return {
        "total_coa_accounts": 22,
        "matched_count": 5,
        "tolerance_count": 3,
        "variance_count": 10,
        "unmatched_manual": 2,
        "unmatched_daftra": 2,
        "total_manual_debit": 100000.0,
        "total_manual_credit": 80000.0,
        "total_daftra_debit": 95000.0,
        "total_daftra_credit": 78000.0,
        "total_debit_variance": 5000.0,
        "total_credit_variance": 2000.0,
        "total_net_variance": 3000.0,
        "largest_variance_coa": 1000,
        "largest_variance_amount": 50000.0,
    }


# ---------------------------------------------------------------------------
# detect_anomalies (rule-based, no LLM)
# ---------------------------------------------------------------------------

class TestDetectAnomalies:
    def test_returns_list(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        assert isinstance(result, list)

    def test_max_10_results(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        assert len(result) <= 10

    def test_sorted_by_severity(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        ranks = [severity_rank.get(a["severity"], 3) for a in result]
        assert ranks == sorted(ranks)

    def test_detects_extreme_variance(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        types = [a["type"] for a in result]
        assert "Extreme Variance" in types

    def test_detects_large_unmatched_manual(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        types = [a["type"] for a in result]
        assert "Large Unmatched (Manual)" in types

    def test_detects_large_unmatched_daftra(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        types = [a["type"] for a in result]
        assert "Large Unmatched (Daftra)" in types

    def test_anomaly_structure(self, mock_analyzer, anomaly_coa_df, sample_summary):
        analyzer, _ = mock_analyzer
        result = analyzer.detect_anomalies(anomaly_coa_df, sample_summary)
        for a in result:
            assert "severity" in a
            assert "type" in a
            assert "coa" in a
            assert "description" in a
            assert "amount" in a


# ---------------------------------------------------------------------------
# generate_insights (mocked LLM)
# ---------------------------------------------------------------------------

class TestGenerateInsights:
    def test_returns_string(self, mock_analyzer, sample_summary, anomaly_coa_df):
        analyzer, _ = mock_analyzer
        result = analyzer.generate_insights(sample_summary, anomaly_coa_df)
        assert isinstance(result, str)

    def test_calls_llm(self, mock_analyzer, sample_summary, anomaly_coa_df):
        analyzer, mock_llm = mock_analyzer
        analyzer.generate_insights(sample_summary, anomaly_coa_df)
        mock_llm.invoke.assert_called_once()


# ---------------------------------------------------------------------------
# chat (mocked LLM)
# ---------------------------------------------------------------------------

class TestChat:
    def test_returns_string(self, mock_analyzer, sample_summary, anomaly_coa_df):
        analyzer, _ = mock_analyzer
        result = analyzer.chat("Apa COA terbesar?", sample_summary, anomaly_coa_df)
        assert isinstance(result, str)

    def test_calls_llm(self, mock_analyzer, sample_summary, anomaly_coa_df):
        analyzer, mock_llm = mock_analyzer
        analyzer.chat("Apa COA terbesar?", sample_summary, anomaly_coa_df)
        mock_llm.invoke.assert_called_once()
