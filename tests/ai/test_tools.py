"""Tests for aurix.ai.tools — LangChain tool functions."""

import pandas as pd
import pytest

from aurix.config import ReconciliationStatus
from aurix.ai.tools import (
    _DATA_STORE,
    set_data_context,
    get_reconciliation_summary,
    get_top_variances,
    get_coa_detail,
    get_anomalies,
    get_unmatched_entries,
    get_transaction_details,
)


@pytest.fixture(autouse=True)
def reset_data_store():
    """Reset the data store before each test."""
    for key in _DATA_STORE:
        _DATA_STORE[key] = None
    yield
    for key in _DATA_STORE:
        _DATA_STORE[key] = None


@pytest.fixture
def sample_coa_df():
    return pd.DataFrame({
        "COA": [1001.0, 2001.0, 3001.0],
        "Account_Name": ["Cash", "Revenue", "Expense"],
        "Manual_Debit": [1000.0, 0.0, 500.0],
        "Manual_Credit": [0.0, 2000.0, 0.0],
        "Manual_Net": [1000.0, -2000.0, 500.0],
        "Manual_TxnCount": [3, 2, 1],
        "Daftra_Debit": [1000.0, 0.0, 0.0],
        "Daftra_Credit": [0.0, 1900.0, 0.0],
        "Daftra_Net": [1000.0, -1900.0, 0.0],
        "Daftra_TxnCount": [3, 2, 0],
        "Debit_Variance": [0.0, 0.0, 500.0],
        "Credit_Variance": [0.0, -100.0, 0.0],
        "Net_Variance": [0.0, -100.0, 500.0],
        "Abs_Variance": [0.0, 100.0, 500.0],
        "Status": [
            ReconciliationStatus.MATCHED.value,
            ReconciliationStatus.VARIANCE.value,
            ReconciliationStatus.UNMATCHED_MANUAL.value,
        ],
    })


@pytest.fixture
def sample_txn_df():
    return pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-15", "2024-01-16", "2024-01-15"]),
        "COA": [1001.0, 1001.0, 2001.0],
        "Account_Name": ["Cash", "Cash", "Revenue"],
        "Description": ["Deposit A", "Deposit B", "Sales"],
        "Debit": [1000.0, 500.0, 0.0],
        "Credit": [0.0, 0.0, 2000.0],
        "Net": [1000.0, 500.0, -2000.0],
        "Reference": ["MJ-001", "DE-001", "MJ-002"],
        "RowID": [1, 1, 2],
        "Source": ["MANUAL", "DAFTRA", "MANUAL"],
    })


@pytest.fixture
def sample_summary():
    return {
        "total_coa_accounts": 3,
        "matched_count": 1,
        "tolerance_count": 0,
        "variance_count": 1,
        "unmatched_manual": 1,
        "unmatched_daftra": 0,
        "total_manual_debit": 1500.0,
        "total_manual_credit": 2000.0,
        "total_daftra_debit": 1000.0,
        "total_daftra_credit": 1900.0,
        "total_debit_variance": 500.0,
        "total_credit_variance": -100.0,
        "total_net_variance": 400.0,
        "largest_variance_coa": 3001,
        "largest_variance_amount": 500.0,
    }


@pytest.fixture
def populated_store(sample_coa_df, sample_txn_df, sample_summary):
    set_data_context(sample_coa_df, sample_txn_df, sample_summary)


# ---------------------------------------------------------------------------
# set_data_context
# ---------------------------------------------------------------------------

class TestSetDataContext:
    def test_populates_store(self, sample_coa_df, sample_txn_df, sample_summary):
        set_data_context(sample_coa_df, sample_txn_df, sample_summary)
        assert _DATA_STORE["coa_recon"] is not None
        assert _DATA_STORE["txn_detail"] is not None
        assert _DATA_STORE["summary"] is not None

    def test_ml_anomalies_default_none(self, sample_coa_df, sample_txn_df, sample_summary):
        set_data_context(sample_coa_df, sample_txn_df, sample_summary)
        assert _DATA_STORE["ml_anomalies"] is None


# ---------------------------------------------------------------------------
# get_reconciliation_summary
# ---------------------------------------------------------------------------

class TestGetReconciliationSummary:
    def test_no_data(self):
        result = get_reconciliation_summary.invoke({})
        assert result == "No reconciliation data available."

    def test_with_data(self, populated_store):
        result = get_reconciliation_summary.invoke({})
        assert "Total COA: 3" in result
        assert "Match Rate:" in result


# ---------------------------------------------------------------------------
# get_top_variances
# ---------------------------------------------------------------------------

class TestGetTopVariances:
    def test_no_data(self):
        result = get_top_variances.invoke({"n": 5})
        assert result == "No data available."

    def test_with_data(self, populated_store):
        result = get_top_variances.invoke({"n": 3})
        assert "COA" in result
        assert len(result.strip().split("\n")) == 3


# ---------------------------------------------------------------------------
# get_coa_detail
# ---------------------------------------------------------------------------

class TestGetCOADetail:
    def test_found(self, populated_store):
        result = get_coa_detail.invoke({"coa_code": 1001})
        assert "COA: 1001" in result
        assert "Manual" in result
        assert "Daftra" in result

    def test_not_found(self, populated_store):
        result = get_coa_detail.invoke({"coa_code": 9999})
        assert "not found" in result


# ---------------------------------------------------------------------------
# get_anomalies
# ---------------------------------------------------------------------------

class TestGetAnomalies:
    def test_no_anomalies(self, populated_store):
        result = get_anomalies.invoke({})
        assert result == "No anomalies detected."

    def test_with_anomalies(self, sample_coa_df, sample_txn_df, sample_summary):
        anomalies = [
            {"severity": "HIGH", "type": "Test", "coa": 1001, "description": "Test anomaly"}
        ]
        set_data_context(sample_coa_df, sample_txn_df, sample_summary, ml_anomalies=anomalies)
        result = get_anomalies.invoke({})
        assert "[HIGH]" in result
        assert "Test anomaly" in result


# ---------------------------------------------------------------------------
# get_unmatched_entries
# ---------------------------------------------------------------------------

class TestGetUnmatchedEntries:
    def test_with_unmatched(self, populated_store):
        result = get_unmatched_entries.invoke({})
        assert "3001" in result
        assert "Only in Manual" in result

    def test_all_matched(self, sample_txn_df, sample_summary):
        all_matched = pd.DataFrame({
            "COA": [1001.0],
            "Account_Name": ["Cash"],
            "Manual_Net": [1000.0],
            "Daftra_Net": [1000.0],
            "Status": [ReconciliationStatus.MATCHED.value],
        })
        set_data_context(all_matched, sample_txn_df, sample_summary)
        result = get_unmatched_entries.invoke({})
        assert result == "No unmatched entries."


# ---------------------------------------------------------------------------
# get_transaction_details
# ---------------------------------------------------------------------------

class TestGetTransactionDetails:
    def test_all_source(self, populated_store):
        result = get_transaction_details.invoke({"coa_code": 1001, "source": "ALL"})
        assert "MANUAL" in result
        assert "DAFTRA" in result

    def test_filtered_source(self, populated_store):
        result = get_transaction_details.invoke({"coa_code": 1001, "source": "MANUAL"})
        assert "MANUAL" in result
        assert "DAFTRA" not in result

    def test_no_transactions(self, populated_store):
        result = get_transaction_details.invoke({"coa_code": 9999, "source": "ALL"})
        assert "No transactions found" in result
