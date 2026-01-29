"""Transaction Detail tab rendering for AURIX Reconciliation."""

import streamlit as st
import pandas as pd

from aurix.engine import ReconciliationEngine


def render_transactions_tab(
    engine: ReconciliationEngine,
    coa_recon: pd.DataFrame,
    txn_detail: pd.DataFrame,
    df_manual_clean: pd.DataFrame,
    df_daftra_clean: pd.DataFrame,
):
    """Render the Transaction Detail tab with COA drill-down."""
    st.markdown("### Transaction-Level Detail")

    # COA selector
    selected_coa = st.selectbox(
        "Select COA to drill down",
        options=['All'] + sorted(coa_recon['COA'].dropna().astype(int).unique().tolist()),
        index=0
    )

    if selected_coa != 'All':
        txn_filtered = engine.reconcile_transaction_level(
            df_manual_clean,
            df_daftra_clean,
            float(selected_coa)
        )
    else:
        txn_filtered = txn_detail

    st.dataframe(
        txn_filtered.style.format({
            'Debit': '{:,.2f}',
            'Credit': '{:,.2f}',
            'Net': '{:,.2f}'
        }),
        use_container_width=True,
        height=500
    )
