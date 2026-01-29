"""Metrics rendering for AURIX Reconciliation."""

import streamlit as st
from typing import Dict, Any


def render_metrics(summary: Dict[str, Any]):
    """Render key metrics cards — clean Apple style."""
    col1, col2, col3, col4, col5 = st.columns(5)

    cards = [
        (col1, summary['total_coa_accounts'], "Total COA", "#1D1D1F"),
        (col2, summary['matched_count'], "Matched", "#34C759"),
        (col3, summary['tolerance_count'], "Tolerance", "#30D158"),
        (col4, summary['variance_count'], "Variance", "#FF9500"),
        (col5, summary['unmatched_manual'] + summary['unmatched_daftra'], "Unmatched", "#FF3B30"),
    ]

    for col, value, label, color in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {color};">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
