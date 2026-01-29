"""Tests for aurix.engine — ReconciliationEngine."""

import pandas as pd
import numpy as np
import pytest

from aurix.config import ReconciliationConfig, ReconciliationStatus
from aurix.engine import ReconciliationEngine


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestEngineInit:
    def test_stores_config(self, engine, default_config):
        assert engine.config is default_config

    def test_creates_audit_log_on_init(self, engine):
        assert len(engine.audit_log) >= 1
        assert engine.audit_log[0].action == "ENGINE_INIT"


# ---------------------------------------------------------------------------
# clean_manual_data
# ---------------------------------------------------------------------------

class TestCleanManualData:
    def test_drops_nan_tanggal(self, engine, raw_manual_df):
        result = engine.clean_manual_data(raw_manual_df)
        # Original has 6 rows, 1 with NaN Tanggal → 5 remain
        assert len(result) == 5

    def test_numeric_conversion(self, engine, raw_manual_df):
        result = engine.clean_manual_data(raw_manual_df)
        assert pd.api.types.is_numeric_dtype(result["Debit-SAR"])
        assert pd.api.types.is_numeric_dtype(result["Kredit-SAR"])
        assert pd.api.types.is_numeric_dtype(result["COA Daftra"])

    def test_string_to_float_coercion(self, engine, raw_manual_df):
        result = engine.clean_manual_data(raw_manual_df)
        # Row with "200.00" string should become float 200.0
        assert 200.0 in result["Debit-SAR"].values

    def test_date_parsing(self, engine, raw_manual_df):
        result = engine.clean_manual_data(raw_manual_df)
        assert pd.api.types.is_datetime64_any_dtype(result["Tanggal"])

    def test_adds_source_column(self, engine, raw_manual_df):
        result = engine.clean_manual_data(raw_manual_df)
        assert "_source" in result.columns
        assert (result["_source"] == "MANUAL").all()

    def test_adds_row_id(self, engine, raw_manual_df):
        result = engine.clean_manual_data(raw_manual_df)
        assert "_row_id" in result.columns
        assert list(result["_row_id"]) == list(range(1, len(result) + 1))

    def test_logs_clean_actions(self, engine, raw_manual_df):
        engine.clean_manual_data(raw_manual_df)
        actions = [e.action for e in engine.audit_log]
        assert "CLEAN_MANUAL_START" in actions
        assert "CLEAN_MANUAL_END" in actions


# ---------------------------------------------------------------------------
# clean_daftra_data
# ---------------------------------------------------------------------------

class TestCleanDaftraData:
    def test_row_count(self, engine, raw_daftra_df):
        result = engine.clean_daftra_data(raw_daftra_df)
        # No NaN dates → all 4 rows kept
        assert len(result) == 4

    def test_numeric_conversion(self, engine, raw_daftra_df):
        result = engine.clean_daftra_data(raw_daftra_df)
        assert pd.api.types.is_numeric_dtype(result["Account Code"])
        assert pd.api.types.is_numeric_dtype(result["Debit"])
        assert pd.api.types.is_numeric_dtype(result["Credit"])

    def test_date_parsing(self, engine, raw_daftra_df):
        result = engine.clean_daftra_data(raw_daftra_df)
        assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_adds_source_and_row_id(self, engine, raw_daftra_df):
        result = engine.clean_daftra_data(raw_daftra_df)
        assert (result["_source"] == "DAFTRA").all()
        assert list(result["_row_id"]) == list(range(1, len(result) + 1))


# ---------------------------------------------------------------------------
# reconcile_coa_level
# ---------------------------------------------------------------------------

class TestReconcileCOALevel:
    def test_output_columns(self, coa_recon_df):
        expected = {
            "COA", "Account_Name",
            "Manual_Debit", "Manual_Credit", "Manual_Net", "Manual_TxnCount",
            "Daftra_Debit", "Daftra_Credit", "Daftra_Net", "Daftra_TxnCount",
            "Debit_Variance", "Credit_Variance", "Net_Variance", "Abs_Variance",
            "Status",
        }
        assert expected.issubset(set(coa_recon_df.columns))

    def test_coa_count(self, coa_recon_df):
        # COAs: 1001, 2001, 3001 (manual only), 4001 (daftra only) = 4
        assert len(coa_recon_df) == 4

    def test_matched_status(self, coa_recon_df):
        """COA 1001: manual debit=1700, credit=0, net=1700; daftra debit=1500, credit=0, net=1500.
        Actually manual has 3 rows (1000+500+200=1700 debit, 0 credit, 1700 net)
        and daftra has 2 rows (1000+500=1500 debit, 0 credit, 1500 net).
        Net variance = 1700-1500 = 200, which is > 1.0 tolerance → VARIANCE not MATCHED.

        Let me re-check: the fixture data for COA 1001:
        Manual rows: Debit-SAR=[1000,500,200], Kredit-SAR=[0,0,0], Nilai Mutasi=[1000,500,200]
        Daftra rows: Debit=[1000,500], Credit=[0,0], Nilai Mutasi=[1000,500]
        So manual net sum = 1700, daftra net sum = 1500, variance = 200 → VARIANCE.
        """
        row_1001 = coa_recon_df[coa_recon_df["COA"] == 1001].iloc[0]
        assert row_1001["Status"] == ReconciliationStatus.VARIANCE.value

    def test_variance_status(self, coa_recon_df):
        """COA 2001: manual net=-3000, daftra net=-2900, variance=-100, abs=100 > 1.0 → VARIANCE."""
        row = coa_recon_df[coa_recon_df["COA"] == 2001].iloc[0]
        assert row["Status"] == ReconciliationStatus.VARIANCE.value

    def test_unmatched_manual_status(self, coa_recon_df):
        """COA 3001: only in manual → UNMATCHED_MANUAL."""
        row = coa_recon_df[coa_recon_df["COA"] == 3001].iloc[0]
        assert row["Status"] == ReconciliationStatus.UNMATCHED_MANUAL.value

    def test_unmatched_daftra_status(self, coa_recon_df):
        """COA 4001: only in daftra → UNMATCHED_DAFTRA."""
        row = coa_recon_df[coa_recon_df["COA"] == 4001].iloc[0]
        assert row["Status"] == ReconciliationStatus.UNMATCHED_DAFTRA.value

    def test_tolerance_status_with_custom_config(self, cleaned_manual_df, cleaned_daftra_df):
        """With tolerance=200, COA 1001 variance=200 should be TOLERANCE (<=200)."""
        config = ReconciliationConfig(tolerance_amount=200.0)
        eng = ReconciliationEngine(config)
        recon = eng.reconcile_coa_level(cleaned_manual_df, cleaned_daftra_df)
        row_1001 = recon[recon["COA"] == 1001].iloc[0]
        # net variance = 200, tolerance = 200, so |200| <= 200 → TOLERANCE (not zero → not MATCHED)
        assert row_1001["Status"] == ReconciliationStatus.TOLERANCE.value

    def test_aggregation_sums(self, coa_recon_df):
        """COA 1001: 3 manual rows → Manual_TxnCount=3, Manual_Debit=1000+500+200=1700."""
        row = coa_recon_df[coa_recon_df["COA"] == 1001].iloc[0]
        assert row["Manual_TxnCount"] == 3
        assert row["Manual_Debit"] == pytest.approx(1700.0)

    def test_nan_filled_to_zero(self, coa_recon_df):
        """Unmatched rows should have 0 for missing-side numerics, not NaN."""
        row_3001 = coa_recon_df[coa_recon_df["COA"] == 3001].iloc[0]
        assert row_3001["Daftra_Debit"] == 0.0
        assert row_3001["Daftra_TxnCount"] == 0

    def test_sorted_by_abs_variance_desc(self, coa_recon_df):
        values = coa_recon_df["Abs_Variance"].tolist()
        assert values == sorted(values, reverse=True)

    def test_account_name_fallback(self, coa_recon_df):
        """COA 4001 (daftra only): Account_Name should fallback to Daftra_Account ('Receivable')."""
        row = coa_recon_df[coa_recon_df["COA"] == 4001].iloc[0]
        assert row["Account_Name"] == "Receivable"

    def test_empty_inputs(self, engine):
        """Empty DataFrames should not crash."""
        empty_m = pd.DataFrame(columns=[
            "Tanggal", "COA Daftra", "COA Daftra Name",
            "Debit-SAR", "Kredit-SAR", "Nilai Mutasi", "_row_id",
        ])
        empty_d = pd.DataFrame(columns=[
            "Date", "Account Code", "Account",
            "Debit", "Credit", "Nilai Mutasi", "_row_id",
        ])
        result = engine.reconcile_coa_level(empty_m, empty_d)
        assert len(result) == 0

    def test_variance_calculation(self, coa_recon_df):
        """Variance = Manual - Daftra for all rows."""
        for _, row in coa_recon_df.iterrows():
            assert row["Debit_Variance"] == pytest.approx(row["Manual_Debit"] - row["Daftra_Debit"])
            assert row["Credit_Variance"] == pytest.approx(row["Manual_Credit"] - row["Daftra_Credit"])
            assert row["Net_Variance"] == pytest.approx(row["Manual_Net"] - row["Daftra_Net"])


# ---------------------------------------------------------------------------
# reconcile_transaction_level
# ---------------------------------------------------------------------------

class TestReconcileTransactionLevel:
    def test_combines_both_sources(self, txn_detail_df):
        sources = set(txn_detail_df["Source"].unique())
        assert sources == {"MANUAL", "DAFTRA"}

    def test_output_columns(self, txn_detail_df):
        expected = {"Date", "COA", "Account_Name", "Description", "Debit", "Credit", "Net", "Reference", "RowID", "Source"}
        assert expected.issubset(set(txn_detail_df.columns))

    def test_total_row_count(self, txn_detail_df, cleaned_manual_df, cleaned_daftra_df):
        assert len(txn_detail_df) == len(cleaned_manual_df) + len(cleaned_daftra_df)

    def test_coa_filter(self, engine, cleaned_manual_df, cleaned_daftra_df):
        result = engine.reconcile_transaction_level(
            cleaned_manual_df, cleaned_daftra_df, selected_coa=1001
        )
        assert (result["COA"] == 1001).all()

    def test_sorted_by_coa_date_net(self, txn_detail_df):
        sorted_df = txn_detail_df.sort_values(["COA", "Date", "Net"])
        pd.testing.assert_frame_equal(txn_detail_df.reset_index(drop=True), sorted_df.reset_index(drop=True))


# ---------------------------------------------------------------------------
# generate_variance_summary
# ---------------------------------------------------------------------------

class TestGenerateVarianceSummary:
    EXPECTED_KEYS = {
        "total_coa_accounts", "matched_count", "tolerance_count", "variance_count",
        "unmatched_manual", "unmatched_daftra",
        "total_manual_debit", "total_manual_credit",
        "total_daftra_debit", "total_daftra_credit",
        "total_debit_variance", "total_credit_variance", "total_net_variance",
        "largest_variance_coa", "largest_variance_amount",
    }

    def test_has_all_keys(self, variance_summary):
        assert self.EXPECTED_KEYS == set(variance_summary.keys())

    def test_total_coa_accounts(self, variance_summary, coa_recon_df):
        assert variance_summary["total_coa_accounts"] == len(coa_recon_df)

    def test_status_counts_sum(self, variance_summary):
        total = (
            variance_summary["matched_count"]
            + variance_summary["tolerance_count"]
            + variance_summary["variance_count"]
            + variance_summary["unmatched_manual"]
            + variance_summary["unmatched_daftra"]
        )
        assert total == variance_summary["total_coa_accounts"]

    def test_debit_variance_calc(self, variance_summary):
        expected = variance_summary["total_manual_debit"] - variance_summary["total_daftra_debit"]
        assert variance_summary["total_debit_variance"] == pytest.approx(expected)

    def test_largest_variance_is_first_row(self, variance_summary, coa_recon_df):
        assert variance_summary["largest_variance_coa"] == coa_recon_df.iloc[0]["COA"]
        assert variance_summary["largest_variance_amount"] == coa_recon_df.iloc[0]["Abs_Variance"]

    def test_empty_df(self, engine):
        empty = pd.DataFrame(columns=[
            "COA", "Manual_Debit", "Manual_Credit", "Manual_Net",
            "Daftra_Debit", "Daftra_Credit", "Daftra_Net",
            "Net_Variance", "Abs_Variance", "Status",
        ])
        summary = engine.generate_variance_summary(empty)
        assert summary["total_coa_accounts"] == 0
        assert summary["largest_variance_coa"] is None
