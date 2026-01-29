"""AI-powered analysis module using LangChain + Groq LLM."""

import pandas as pd
from typing import Dict, List, Any

from aurix.config import ReconciliationStatus
from aurix.ai.base import LLMProvider


class AIAnalyzer:
    """AI-powered analysis for reconciliation data."""

    SYSTEM_PROMPT = """Anda adalah AI assistant untuk AURIX Reconciliation System di BPKH Limited (Saudi Arabia).
Tugas Anda menganalisis hasil reconciliation antara Jurnal Manual dan Daftra Export untuk keperluan audit keuangan syariah.

Status Categories:
- MATCHED (Sesuai): Tidak ada selisih sama sekali
- TOLERANCE (Dalam Toleransi): Selisih dalam batas yang dapat diterima
- VARIANCE (Selisih): Selisih di luar toleransi, perlu investigasi
- UNMATCHED_MANUAL: Transaksi hanya ada di Jurnal Manual (tidak ada di Daftra)
- UNMATCHED_DAFTRA: Transaksi hanya ada di Daftra (tidak ada di Jurnal Manual)

Berikan analisis dalam Bahasa Indonesia yang jelas, profesional, dan actionable.
Fokus pada temuan yang signifikan dan rekomendasi perbaikan."""

    def __init__(self, api_key: str):
        """Initialize AI Analyzer with LangChain Groq provider."""
        self.provider = LLMProvider(api_key)

    def _call_llm(self, user_message: str, max_tokens: int = 1024) -> str:
        """Make a call to Groq LLM via LangChain."""
        try:
            return self.provider.invoke([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ], max_tokens=max_tokens)
        except Exception as e:
            return f"Error calling AI: {str(e)}"

    def generate_insights(self, summary: Dict[str, Any], coa_recon: pd.DataFrame) -> str:
        """Generate AI-powered insights from reconciliation results."""
        match_rate = (summary['matched_count'] + summary['tolerance_count']) / summary['total_coa_accounts'] * 100

        top_variances = coa_recon[coa_recon['Status'] == ReconciliationStatus.VARIANCE.value].head(5)
        variance_details = ""
        for _, row in top_variances.iterrows():
            variance_details += f"- COA {int(row['COA'])}: Selisih SAR {row['Net_Variance']:,.2f}\n"

        prompt = f"""Analisis hasil reconciliation berikut dan berikan 3-5 insight utama:

RINGKASAN DATA:
- Total COA: {summary['total_coa_accounts']}
- Match Rate: {match_rate:.1f}%
- Fully Matched: {summary['matched_count']} COA
- Within Tolerance: {summary['tolerance_count']} COA
- With Variance: {summary['variance_count']} COA
- Only in Manual: {summary['unmatched_manual']} COA
- Only in Daftra: {summary['unmatched_daftra']} COA

TOTAL AMOUNTS:
- Manual Debit: SAR {summary['total_manual_debit']:,.2f}
- Manual Credit: SAR {summary['total_manual_credit']:,.2f}
- Daftra Debit: SAR {summary['total_daftra_debit']:,.2f}
- Daftra Credit: SAR {summary['total_daftra_credit']:,.2f}
- Total Net Variance: SAR {summary['total_net_variance']:,.2f}

TOP 5 VARIANCES:
{variance_details if variance_details else "Tidak ada variance signifikan"}

Berikan insight dalam format bullet points, fokus pada:
1. Kesehatan overall reconciliation
2. Area yang perlu perhatian
3. Rekomendasi tindak lanjut"""

        return self._call_llm(prompt)

    def detect_anomalies(self, coa_recon: pd.DataFrame, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies using rule-based analysis."""
        anomalies = []

        variance_values = coa_recon['Net_Variance'].abs()
        mean_variance = variance_values.mean()
        std_variance = variance_values.std()

        # 1. Extreme variances (> 3 std dev)
        extreme_threshold = mean_variance + (3 * std_variance) if std_variance > 0 else mean_variance * 3
        extreme_variances = coa_recon[variance_values > extreme_threshold]

        for _, row in extreme_variances.iterrows():
            anomalies.append({
                "severity": "HIGH",
                "type": "Extreme Variance",
                "coa": int(row['COA']) if pd.notna(row['COA']) else "N/A",
                "description": f"COA {int(row['COA']) if pd.notna(row['COA']) else 'N/A'} memiliki variance ekstrem: SAR {row['Net_Variance']:,.2f}",
                "amount": row['Net_Variance']
            })

        # 2. Large unmatched amounts
        unmatched_manual = coa_recon[coa_recon['Status'] == ReconciliationStatus.UNMATCHED_MANUAL.value]
        for _, row in unmatched_manual.iterrows():
            if abs(row['Manual_Net']) > 10000:
                anomalies.append({
                    "severity": "MEDIUM",
                    "type": "Large Unmatched (Manual)",
                    "coa": int(row['COA']) if pd.notna(row['COA']) else "N/A",
                    "description": f"COA {int(row['COA']) if pd.notna(row['COA']) else 'N/A'} hanya di Manual dengan nilai besar: SAR {row['Manual_Net']:,.2f}",
                    "amount": row['Manual_Net']
                })

        unmatched_daftra = coa_recon[coa_recon['Status'] == ReconciliationStatus.UNMATCHED_DAFTRA.value]
        for _, row in unmatched_daftra.iterrows():
            if abs(row['Daftra_Net']) > 10000:
                anomalies.append({
                    "severity": "MEDIUM",
                    "type": "Large Unmatched (Daftra)",
                    "coa": int(row['COA']) if pd.notna(row['COA']) else "N/A",
                    "description": f"COA {int(row['COA']) if pd.notna(row['COA']) else 'N/A'} hanya di Daftra dengan nilai besar: SAR {row['Daftra_Net']:,.2f}",
                    "amount": row['Daftra_Net']
                })

        # 3. Suspicious patterns - one-sided entries
        for _, row in coa_recon.iterrows():
            if row['Status'] not in [ReconciliationStatus.UNMATCHED_MANUAL.value, ReconciliationStatus.UNMATCHED_DAFTRA.value]:
                manual_ratio = row['Manual_Debit'] / (row['Manual_Credit'] + 0.01) if row['Manual_Credit'] != 0 else float('inf')
                daftra_ratio = row['Daftra_Debit'] / (row['Daftra_Credit'] + 0.01) if row['Daftra_Credit'] != 0 else float('inf')

                if (manual_ratio > 100 and daftra_ratio < 0.01) or (manual_ratio < 0.01 and daftra_ratio > 100):
                    anomalies.append({
                        "severity": "LOW",
                        "type": "Debit/Credit Pattern Mismatch",
                        "coa": int(row['COA']) if pd.notna(row['COA']) else "N/A",
                        "description": f"COA {int(row['COA']) if pd.notna(row['COA']) else 'N/A'} memiliki pola debit/credit yang berbeda antara Manual dan Daftra",
                        "amount": row['Net_Variance']
                    })

        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        anomalies.sort(key=lambda x: severity_order.get(x['severity'], 3))
        return anomalies[:10]

    def chat(self, question: str, summary: Dict[str, Any], coa_recon: pd.DataFrame) -> str:
        """Answer user questions about reconciliation data."""
        match_rate = (summary['matched_count'] + summary['tolerance_count']) / summary['total_coa_accounts'] * 100

        top_variances = coa_recon.head(20)
        variance_table = "COA | Account | Manual Net | Daftra Net | Variance | Status\n"
        variance_table += "-" * 80 + "\n"
        for _, row in top_variances.iterrows():
            variance_table += f"{int(row['COA']) if pd.notna(row['COA']) else 'N/A'} | {str(row['Account_Name'])[:20]} | {row['Manual_Net']:,.0f} | {row['Daftra_Net']:,.0f} | {row['Net_Variance']:,.0f} | {row['Status']}\n"

        prompt = f"""KONTEKS DATA RECONCILIATION:

Ringkasan:
- Total COA: {summary['total_coa_accounts']}
- Match Rate: {match_rate:.1f}%
- Total Net Variance: SAR {summary['total_net_variance']:,.2f}
- Matched: {summary['matched_count']}, Tolerance: {summary['tolerance_count']}, Variance: {summary['variance_count']}
- Unmatched Manual: {summary['unmatched_manual']}, Unmatched Daftra: {summary['unmatched_daftra']}

Top 20 COA by Variance:
{variance_table}

PERTANYAAN USER:
{question}

Jawab pertanyaan dengan jelas dan spesifik berdasarkan data di atas."""

        return self._call_llm(prompt, max_tokens=1500)
