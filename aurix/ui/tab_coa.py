"""COA Reconciliation tab rendering for AURIX Reconciliation."""

import streamlit as st
import pandas as pd
from datetime import datetime


def render_coa_tab(coa_recon: pd.DataFrame):
    """Render the COA Reconciliation tab with filters and data table."""
    st.markdown("### COA-Level Reconciliation Results")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=coa_recon['Status'].unique().tolist(),
            default=coa_recon['Status'].unique().tolist()
        )

    with col_f2:
        min_variance = st.number_input(
            "Min Absolute Variance (SAR)",
            min_value=0.0,
            value=0.0
        )

    with col_f3:
        sort_by = st.selectbox(
            "Sort by",
            options=['Abs_Variance', 'COA', 'Net_Variance'],
            index=0
        )

    # Filter data
    filtered_coa = coa_recon[
        (coa_recon['Status'].isin(status_filter)) &
        (coa_recon['Abs_Variance'] >= min_variance)
    ].sort_values(sort_by, ascending=(sort_by == 'COA'))

    st.dataframe(
        filtered_coa[[
            'COA', 'Account_Name', 'Manual_Debit', 'Manual_Credit', 'Manual_Net',
            'Daftra_Debit', 'Daftra_Credit', 'Daftra_Net',
            'Net_Variance', 'Status'
        ]].style.format({
            'Manual_Debit': '{:,.2f}',
            'Manual_Credit': '{:,.2f}',
            'Manual_Net': '{:,.2f}',
            'Daftra_Debit': '{:,.2f}',
            'Daftra_Credit': '{:,.2f}',
            'Daftra_Net': '{:,.2f}',
            'Net_Variance': '{:,.2f}'
        }),
        use_container_width=True,
        height=500
    )

    st.download_button(
        label="Download Filtered COA Data (CSV)",
        data=filtered_coa.to_csv(index=False),
        file_name=f"coa_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
