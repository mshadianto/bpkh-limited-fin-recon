"""Core reconciliation engine for AURIX."""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

from aurix.config import ReconciliationConfig, ReconciliationStatus, AuditLogEntry


class ReconciliationEngine:
    """
    Core engine for performing multi-level reconciliation between
    Daftra accounting system exports and manual journal entries.
    """

    def __init__(self, config: ReconciliationConfig):
        self.config = config
        self.audit_log: List[AuditLogEntry] = []
        self._log_action("ENGINE_INIT", {"config": str(config)})

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Add entry to audit log with timestamp and checksum."""
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            details=details
        )
        self.audit_log.append(entry)

    def clean_manual_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize manual journal data."""
        self._log_action("CLEAN_MANUAL_START", {"rows": len(df)})

        cols_to_keep = [
            'Rekening', 'Tanggal', 'Ref. No', 'Uraian', 'COA Manual',
            'Debit-SAR', 'Kredit-SAR', 'Nilai Mutasi', 'Month', 'Year',
            'COA Daftra', 'COA Daftra Name'
        ]

        available_cols = [c for c in cols_to_keep if c in df.columns]
        df_clean = df[available_cols].copy()
        df_clean = df_clean.dropna(subset=['Tanggal'])

        for col in ['Debit-SAR', 'Kredit-SAR', 'Nilai Mutasi', 'COA Daftra']:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        df_clean['Tanggal'] = pd.to_datetime(df_clean['Tanggal'])
        df_clean['_source'] = 'MANUAL'
        df_clean['_row_id'] = range(1, len(df_clean) + 1)

        self._log_action("CLEAN_MANUAL_END", {
            "rows_cleaned": len(df_clean),
            "columns": list(df_clean.columns)
        })
        return df_clean

    def clean_daftra_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize Daftra export data."""
        self._log_action("CLEAN_DAFTRA_START", {"rows": len(df)})

        cols_to_keep = [
            'Date', 'Month', 'Year', 'Number', 'Account',
            'Account Code', 'Description', 'Source', 'Debit',
            'Credit', 'Nilai Mutasi'
        ]

        available_cols = [c for c in cols_to_keep if c in df.columns]
        df_clean = df[available_cols].copy()
        df_clean = df_clean.dropna(subset=['Date'])

        for col in ['Debit', 'Credit', 'Nilai Mutasi', 'Account Code']:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        df_clean['Date'] = pd.to_datetime(df_clean['Date'])
        df_clean['_source'] = 'DAFTRA'
        df_clean['_row_id'] = range(1, len(df_clean) + 1)

        self._log_action("CLEAN_DAFTRA_END", {
            "rows_cleaned": len(df_clean),
            "columns": list(df_clean.columns)
        })
        return df_clean

    def reconcile_coa_level(
        self,
        df_manual: pd.DataFrame,
        df_daftra: pd.DataFrame
    ) -> pd.DataFrame:
        """Perform COA-level (aggregate) reconciliation."""
        self._log_action("COA_RECON_START", {
            "manual_rows": len(df_manual),
            "daftra_rows": len(df_daftra)
        })

        manual_agg = df_manual.groupby('COA Daftra').agg({
            'Debit-SAR': 'sum',
            'Kredit-SAR': 'sum',
            'Nilai Mutasi': 'sum',
            'COA Daftra Name': 'first',
            '_row_id': 'count'
        }).reset_index()
        manual_agg.columns = [
            'COA', 'Manual_Debit', 'Manual_Credit',
            'Manual_Net', 'COA_Name', 'Manual_TxnCount'
        ]

        daftra_agg = df_daftra.groupby('Account Code').agg({
            'Debit': 'sum',
            'Credit': 'sum',
            'Nilai Mutasi': 'sum',
            'Account': 'first',
            '_row_id': 'count'
        }).reset_index()
        daftra_agg.columns = [
            'COA', 'Daftra_Debit', 'Daftra_Credit',
            'Daftra_Net', 'Daftra_Account', 'Daftra_TxnCount'
        ]

        recon = pd.merge(manual_agg, daftra_agg, on='COA', how='outer')

        numeric_cols = [
            'Manual_Debit', 'Manual_Credit', 'Manual_Net', 'Manual_TxnCount',
            'Daftra_Debit', 'Daftra_Credit', 'Daftra_Net', 'Daftra_TxnCount'
        ]
        for col in numeric_cols:
            recon[col] = recon[col].fillna(0)

        recon['Debit_Variance'] = recon['Manual_Debit'] - recon['Daftra_Debit']
        recon['Credit_Variance'] = recon['Manual_Credit'] - recon['Daftra_Credit']
        recon['Net_Variance'] = recon['Manual_Net'] - recon['Daftra_Net']
        recon['Abs_Variance'] = recon['Net_Variance'].abs()

        def determine_status(row):
            if pd.isna(row['Manual_Net']) or row['Manual_TxnCount'] == 0:
                return ReconciliationStatus.UNMATCHED_DAFTRA.value
            elif pd.isna(row['Daftra_Net']) or row['Daftra_TxnCount'] == 0:
                return ReconciliationStatus.UNMATCHED_MANUAL.value
            elif abs(row['Net_Variance']) <= self.config.tolerance_amount:
                if row['Net_Variance'] == 0:
                    return ReconciliationStatus.MATCHED.value
                return ReconciliationStatus.TOLERANCE.value
            else:
                return ReconciliationStatus.VARIANCE.value

        recon['Status'] = recon.apply(determine_status, axis=1)
        recon = recon.sort_values('Abs_Variance', ascending=False)
        recon['Account_Name'] = recon['COA_Name'].fillna(recon['Daftra_Account'])

        self._log_action("COA_RECON_END", {
            "total_coa": len(recon),
            "matched": len(recon[recon['Status'] == ReconciliationStatus.MATCHED.value]),
            "variance": len(recon[recon['Status'] == ReconciliationStatus.VARIANCE.value])
        })
        return recon

    def reconcile_transaction_level(
        self,
        df_manual: pd.DataFrame,
        df_daftra: pd.DataFrame,
        selected_coa: Optional[float] = None
    ) -> pd.DataFrame:
        """Perform transaction-level (detail) reconciliation."""
        self._log_action("TXN_RECON_START", {"coa_filter": selected_coa})

        if selected_coa is not None:
            df_manual = df_manual[df_manual['COA Daftra'] == selected_coa].copy()
            df_daftra = df_daftra[df_daftra['Account Code'] == selected_coa].copy()

        manual_txn = df_manual[[
            'Tanggal', 'COA Daftra', 'COA Daftra Name', 'Uraian',
            'Debit-SAR', 'Kredit-SAR', 'Nilai Mutasi', 'Ref. No', '_row_id'
        ]].copy()
        manual_txn.columns = [
            'Date', 'COA', 'Account_Name', 'Description',
            'Debit', 'Credit', 'Net', 'Reference', 'RowID'
        ]
        manual_txn['Source'] = 'MANUAL'

        daftra_txn = df_daftra[[
            'Date', 'Account Code', 'Account', 'Description',
            'Debit', 'Credit', 'Nilai Mutasi', 'Number', '_row_id'
        ]].copy()
        daftra_txn.columns = [
            'Date', 'COA', 'Account_Name', 'Description',
            'Debit', 'Credit', 'Net', 'Reference', 'RowID'
        ]
        daftra_txn['Source'] = 'DAFTRA'

        combined = pd.concat([manual_txn, daftra_txn], ignore_index=True)
        combined = combined.sort_values(['COA', 'Date', 'Net'])

        self._log_action("TXN_RECON_END", {"total_transactions": len(combined)})
        return combined

    def generate_variance_summary(self, coa_recon: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for variance analysis."""
        total_manual_debit = coa_recon['Manual_Debit'].sum()
        total_manual_credit = coa_recon['Manual_Credit'].sum()
        total_daftra_debit = coa_recon['Daftra_Debit'].sum()
        total_daftra_credit = coa_recon['Daftra_Credit'].sum()

        status_counts = coa_recon['Status'].value_counts().to_dict()

        summary = {
            "total_coa_accounts": len(coa_recon),
            "matched_count": status_counts.get(ReconciliationStatus.MATCHED.value, 0),
            "tolerance_count": status_counts.get(ReconciliationStatus.TOLERANCE.value, 0),
            "variance_count": status_counts.get(ReconciliationStatus.VARIANCE.value, 0),
            "unmatched_manual": status_counts.get(ReconciliationStatus.UNMATCHED_MANUAL.value, 0),
            "unmatched_daftra": status_counts.get(ReconciliationStatus.UNMATCHED_DAFTRA.value, 0),
            "total_manual_debit": total_manual_debit,
            "total_manual_credit": total_manual_credit,
            "total_daftra_debit": total_daftra_debit,
            "total_daftra_credit": total_daftra_credit,
            "total_debit_variance": total_manual_debit - total_daftra_debit,
            "total_credit_variance": total_manual_credit - total_daftra_credit,
            "total_net_variance": coa_recon['Net_Variance'].sum(),
            "largest_variance_coa": coa_recon.iloc[0]['COA'] if len(coa_recon) > 0 else None,
            "largest_variance_amount": coa_recon.iloc[0]['Abs_Variance'] if len(coa_recon) > 0 else 0
        }

        self._log_action("SUMMARY_GENERATED", summary)
        return summary
