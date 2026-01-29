"""LangChain tools for CrewAI agent data access."""

import pandas as pd
from langchain_core.tools import tool

_DATA_STORE = {
    "coa_recon": None,
    "txn_detail": None,
    "summary": None,
    "ml_anomalies": None,
}


def set_data_context(coa_recon, txn_detail, summary, ml_anomalies=None):
    """Populate the data store for tool access."""
    _DATA_STORE["coa_recon"] = coa_recon
    _DATA_STORE["txn_detail"] = txn_detail
    _DATA_STORE["summary"] = summary
    _DATA_STORE["ml_anomalies"] = ml_anomalies


@tool
def get_reconciliation_summary() -> str:
    """Get the reconciliation summary statistics including match rate, variance counts, and total amounts."""
    s = _DATA_STORE["summary"]
    if s is None:
        return "No reconciliation data available."
    match_rate = (s['matched_count'] + s['tolerance_count']) / s['total_coa_accounts'] * 100
    return (
        f"Total COA: {s['total_coa_accounts']}, Match Rate: {match_rate:.1f}%, "
        f"Matched: {s['matched_count']}, Tolerance: {s['tolerance_count']}, "
        f"Variance: {s['variance_count']}, Unmatched Manual: {s['unmatched_manual']}, "
        f"Unmatched Daftra: {s['unmatched_daftra']}, "
        f"Total Net Variance: SAR {s['total_net_variance']:,.2f}"
    )


@tool
def get_top_variances(n: int = 10) -> str:
    """Get the top N COA accounts with largest absolute variances."""
    df = _DATA_STORE["coa_recon"]
    if df is None:
        return "No data available."
    top = df.head(n)
    lines = []
    for _, row in top.iterrows():
        lines.append(
            f"COA {int(row['COA']) if pd.notna(row['COA']) else 'N/A'}: "
            f"{row.get('Account_Name', '')} | "
            f"Net Var: SAR {row['Net_Variance']:,.2f} | Status: {row['Status']}"
        )
    return "\n".join(lines)


@tool
def get_coa_detail(coa_code: int) -> str:
    """Get detailed reconciliation data for a specific COA account code."""
    df = _DATA_STORE["coa_recon"]
    if df is None:
        return "No data available."
    match = df[df['COA'] == float(coa_code)]
    if len(match) == 0:
        return f"COA {coa_code} not found."
    row = match.iloc[0]
    return (
        f"COA: {coa_code}, Account: {row.get('Account_Name', '')}\n"
        f"Manual - Debit: {row['Manual_Debit']:,.2f}, Credit: {row['Manual_Credit']:,.2f}, "
        f"Net: {row['Manual_Net']:,.2f}, TxnCount: {int(row['Manual_TxnCount'])}\n"
        f"Daftra - Debit: {row['Daftra_Debit']:,.2f}, Credit: {row['Daftra_Credit']:,.2f}, "
        f"Net: {row['Daftra_Net']:,.2f}, TxnCount: {int(row['Daftra_TxnCount'])}\n"
        f"Variances - Debit: {row['Debit_Variance']:,.2f}, Credit: {row['Credit_Variance']:,.2f}, "
        f"Net: {row['Net_Variance']:,.2f}\nStatus: {row['Status']}"
    )


@tool
def get_anomalies() -> str:
    """Get all detected anomalies (rule-based and ML-based)."""
    anomalies = _DATA_STORE.get("ml_anomalies", [])
    if not anomalies:
        return "No anomalies detected."
    lines = []
    for a in anomalies:
        lines.append(
            f"[{a['severity']}] {a['type']} - COA {a.get('coa', 'N/A')}: {a['description']}"
        )
    return "\n".join(lines)


@tool
def get_unmatched_entries() -> str:
    """Get all unmatched COA entries (only in Manual or only in Daftra)."""
    df = _DATA_STORE["coa_recon"]
    if df is None:
        return "No data available."
    unmatched = df[df['Status'].str.contains('Only in', na=False)]
    if len(unmatched) == 0:
        return "No unmatched entries."
    lines = []
    for _, row in unmatched.iterrows():
        lines.append(
            f"COA {int(row['COA']) if pd.notna(row['COA']) else 'N/A'}: "
            f"{row.get('Account_Name', '')} | Status: {row['Status']} | "
            f"Manual Net: {row['Manual_Net']:,.2f} | Daftra Net: {row['Daftra_Net']:,.2f}"
        )
    return "\n".join(lines)


@tool
def get_transaction_details(coa_code: int, source: str = "ALL") -> str:
    """Get transaction-level details for a specific COA. Source can be ALL, MANUAL, or DAFTRA."""
    df = _DATA_STORE["txn_detail"]
    if df is None:
        return "No data available."
    filtered = df[df['COA'] == float(coa_code)]
    if source != "ALL":
        filtered = filtered[filtered['Source'] == source]
    if len(filtered) == 0:
        return f"No transactions found for COA {coa_code}."
    lines = []
    for _, row in filtered.head(20).iterrows():
        lines.append(
            f"[{row['Source']}] {str(row.get('Date', ''))[:10]} | "
            f"D: {row['Debit']:,.2f} | C: {row['Credit']:,.2f} | "
            f"Net: {row['Net']:,.2f} | {str(row.get('Description', ''))[:50]}"
        )
    return "\n".join(lines)
