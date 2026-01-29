"""Automated root cause analysis for reconciliation variances."""

import pandas as pd
from typing import Dict, Any, List

from aurix.ai.base import LLMProvider
from aurix.config import ReconciliationStatus


class RootCauseAnalyzer:
    """Automated root cause analysis using LLM chains."""

    ANALYSIS_PROMPT = """Anda adalah auditor keuangan syariah senior di BPKH Limited.
Analisis root cause untuk selisih reconciliation pada COA berikut:

COA CODE: {coa_code}
ACCOUNT NAME: {account_name}

DATA RECONCILIATION:
- Manual Debit: SAR {manual_debit:,.2f}
- Manual Credit: SAR {manual_credit:,.2f}
- Manual Net: SAR {manual_net:,.2f}
- Manual Txn Count: {manual_txn_count}
- Daftra Debit: SAR {daftra_debit:,.2f}
- Daftra Credit: SAR {daftra_credit:,.2f}
- Daftra Net: SAR {daftra_net:,.2f}
- Daftra Txn Count: {daftra_txn_count}
- Net Variance: SAR {net_variance:,.2f}
- Status: {status}

TRANSAKSI DETAIL (sample):
{transaction_sample}

{ml_context}

Berikan analisis dalam format berikut:
1. **Root Cause**: Identifikasi penyebab utama selisih (1-2 paragraf)
2. **Contributing Factors**: Faktor-faktor yang berkontribusi (bullet points)
3. **Risk Level**: LOW/MEDIUM/HIGH dan penjelasan
4. **Recommended Actions**: Langkah-langkah perbaikan spesifik (numbered list)
5. **Compliance Impact**: Dampak terhadap kepatuhan PSAK 109/AAOIFI (1 paragraf)"""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analyze_single_coa(
        self,
        coa_row: pd.Series,
        txn_detail: pd.DataFrame,
        ml_anomalies: List[Dict] = None
    ) -> str:
        """Perform root cause analysis for a single COA."""
        txn_sample = ""
        if len(txn_detail) > 0:
            for _, txn in txn_detail.head(10).iterrows():
                txn_sample += (
                    f"  [{txn.get('Source', '?')}] {str(txn.get('Date', ''))[:10]} | "
                    f"Debit: {txn.get('Debit', 0):,.2f} | Credit: {txn.get('Credit', 0):,.2f} | "
                    f"Net: {txn.get('Net', 0):,.2f} | {str(txn.get('Description', ''))[:40]}\n"
                )
        else:
            txn_sample = "  (tidak ada detail transaksi)"

        ml_context = ""
        if ml_anomalies:
            coa_code = int(coa_row.get('COA', 0)) if pd.notna(coa_row.get('COA')) else None
            relevant = [a for a in ml_anomalies if a.get('coa') == coa_code] if coa_code else []
            if relevant:
                ml_context = "ML ANOMALY DETECTION:\n"
                for a in relevant:
                    ml_context += f"- [{a['severity']}] {a['type']}: {a['description']}\n"

        prompt = self.ANALYSIS_PROMPT.format(
            coa_code=int(coa_row.get('COA', 0)) if pd.notna(coa_row.get('COA')) else 'N/A',
            account_name=str(coa_row.get('Account_Name', 'Unknown')),
            manual_debit=float(coa_row.get('Manual_Debit', 0)),
            manual_credit=float(coa_row.get('Manual_Credit', 0)),
            manual_net=float(coa_row.get('Manual_Net', 0)),
            manual_txn_count=int(coa_row.get('Manual_TxnCount', 0)),
            daftra_debit=float(coa_row.get('Daftra_Debit', 0)),
            daftra_credit=float(coa_row.get('Daftra_Credit', 0)),
            daftra_net=float(coa_row.get('Daftra_Net', 0)),
            daftra_txn_count=int(coa_row.get('Daftra_TxnCount', 0)),
            net_variance=float(coa_row.get('Net_Variance', 0)),
            status=str(coa_row.get('Status', '')),
            transaction_sample=txn_sample,
            ml_context=ml_context
        )

        return self.provider.invoke([
            {"role": "system", "content": "Anda adalah auditor keuangan syariah senior."},
            {"role": "user", "content": prompt}
        ], max_tokens=2000)

    def analyze_top_variances(
        self,
        coa_recon: pd.DataFrame,
        txn_detail: pd.DataFrame,
        ml_anomalies: List[Dict] = None,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Analyze root causes for the top N variance COAs."""
        variance_rows = coa_recon[
            coa_recon['Status'] == ReconciliationStatus.VARIANCE.value
        ].head(top_n)

        results = []
        for _, row in variance_rows.iterrows():
            coa_code = row.get('COA')
            coa_txn = txn_detail[txn_detail['COA'] == coa_code] if coa_code is not None else pd.DataFrame()

            analysis = self.analyze_single_coa(row, coa_txn, ml_anomalies)
            results.append({
                "coa": int(coa_code) if pd.notna(coa_code) else "N/A",
                "account_name": str(row.get('Account_Name', '')),
                "net_variance": float(row.get('Net_Variance', 0)),
                "analysis": analysis
            })

        return results
