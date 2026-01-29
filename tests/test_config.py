"""Tests for aurix.config — dataclasses and enums."""

import pandas as pd

from aurix.config import (
    ReconciliationStatus,
    ReconciliationConfig,
    AuditLogEntry,
    ReconciliationResult,
)


class TestReconciliationStatus:
    def test_has_five_members(self):
        assert len(ReconciliationStatus) == 5

    def test_member_names(self):
        names = {s.name for s in ReconciliationStatus}
        assert names == {"MATCHED", "VARIANCE", "UNMATCHED_MANUAL", "UNMATCHED_DAFTRA", "TOLERANCE"}

    def test_matched_value_contains_emoji(self):
        assert "✅" in ReconciliationStatus.MATCHED.value

    def test_variance_value_contains_emoji(self):
        assert "⚠️" in ReconciliationStatus.VARIANCE.value

    def test_unmatched_manual_value(self):
        assert "Only in Manual" in ReconciliationStatus.UNMATCHED_MANUAL.value

    def test_unmatched_daftra_value(self):
        assert "Only in Daftra" in ReconciliationStatus.UNMATCHED_DAFTRA.value

    def test_tolerance_value(self):
        assert "Within Tolerance" in ReconciliationStatus.TOLERANCE.value


class TestReconciliationConfig:
    def test_default_tolerance_amount(self):
        config = ReconciliationConfig()
        assert config.tolerance_amount == 1.0

    def test_default_tolerance_percentage(self):
        config = ReconciliationConfig()
        assert config.tolerance_percentage == 0.001

    def test_default_column_mappings(self):
        config = ReconciliationConfig()
        assert config.date_column_manual == "Tanggal"
        assert config.date_column_daftra == "Date"
        assert config.coa_column_manual == "COA Daftra"
        assert config.coa_column_daftra == "Account Code"
        assert config.debit_column_manual == "Debit-SAR"
        assert config.credit_column_manual == "Kredit-SAR"
        assert config.debit_column_daftra == "Debit"
        assert config.credit_column_daftra == "Credit"

    def test_custom_tolerance_overrides(self):
        config = ReconciliationConfig(tolerance_amount=5.0)
        assert config.tolerance_amount == 5.0
        # Other defaults still intact
        assert config.coa_column_manual == "COA Daftra"


class TestAuditLogEntry:
    def test_checksum_is_generated(self):
        entry = AuditLogEntry(
            timestamp="2024-01-01T00:00:00",
            action="TEST_ACTION",
            details={"key": "value"},
        )
        assert entry.checksum != ""
        assert len(entry.checksum) == 16

    def test_checksum_is_hex(self):
        entry = AuditLogEntry(
            timestamp="2024-01-01T00:00:00",
            action="TEST",
            details={},
        )
        int(entry.checksum, 16)  # Should not raise

    def test_checksum_deterministic(self):
        kwargs = dict(timestamp="2024-01-01T00:00:00", action="TEST", details={"a": 1})
        a = AuditLogEntry(**kwargs)
        b = AuditLogEntry(**kwargs)
        assert a.checksum == b.checksum

    def test_checksum_changes_on_different_action(self):
        base = dict(timestamp="2024-01-01T00:00:00", details={})
        a = AuditLogEntry(action="ACTION_A", **base)
        b = AuditLogEntry(action="ACTION_B", **base)
        assert a.checksum != b.checksum

    def test_checksum_changes_on_different_details(self):
        base = dict(timestamp="2024-01-01T00:00:00", action="TEST")
        a = AuditLogEntry(details={"x": 1}, **base)
        b = AuditLogEntry(details={"x": 2}, **base)
        assert a.checksum != b.checksum

    def test_default_user(self):
        entry = AuditLogEntry(timestamp="t", action="a", details={})
        assert entry.user == "System"


class TestReconciliationResult:
    def test_defaults(self):
        result = ReconciliationResult(
            summary_df=pd.DataFrame(),
            detail_df=pd.DataFrame(),
        )
        assert result.matched_count == 0
        assert result.variance_count == 0
        assert result.unmatched_manual == 0
        assert result.unmatched_daftra == 0
        assert result.total_variance_amount == 0.0
        assert result.audit_log == []

    def test_audit_log_lists_are_independent(self):
        a = ReconciliationResult(summary_df=pd.DataFrame(), detail_df=pd.DataFrame())
        b = ReconciliationResult(summary_df=pd.DataFrame(), detail_df=pd.DataFrame())
        a.audit_log.append("item")
        assert len(b.audit_log) == 0
