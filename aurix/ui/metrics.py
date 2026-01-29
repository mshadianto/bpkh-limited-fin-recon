"""Metrics rendering for AURIX Reconciliation."""

import streamlit as st
from typing import Dict, Any


def render_metrics(summary: Dict[str, Any]):
    """Render key metrics cards — premium Apple style with accent bars."""
    total = summary['total_coa_accounts']
    matched = summary['matched_count']
    tolerance = summary['tolerance_count']
    variance = summary['variance_count']
    unmatched = summary['unmatched_manual'] + summary['unmatched_daftra']

    col1, col2, col3, col4, col5 = st.columns(5)

    cards = [
        (col1, total, "Total COA", "#1D1D1F", 100),
        (col2, matched, "Matched", "#34C759", (matched / total * 100) if total else 0),
        (col3, tolerance, "Tolerance", "#30D158", (tolerance / total * 100) if total else 0),
        (col4, variance, "Variance", "#FF9500", (variance / total * 100) if total else 0),
        (col5, unmatched, "Unmatched", "#FF3B30", (unmatched / total * 100) if total else 0),
    ]

    for col, value, label, color, pct in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {color};">
                <div class="metric-value" style="color: {color};">{value}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-bar">
                    <div class="metric-bar-fill" style="width: {pct:.0f}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
