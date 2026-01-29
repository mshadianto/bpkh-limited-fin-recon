"""Metrics rendering for AURIX Reconciliation."""

import streamlit as st
from typing import Dict, Any


def render_metrics(summary: Dict[str, Any]):
    """Render key metrics cards with icons."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">&#128202;</span>
            <div class="metric-value">{summary['total_coa_accounts']}</div>
            <div class="metric-label">Total COA</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2E7D32;">
            <span class="metric-icon">&#9989;</span>
            <div class="metric-value" style="color: #2E7D32;">{summary['matched_count']}</div>
            <div class="metric-label">Fully Matched</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #81C784;">
            <span class="metric-icon">&#128309;</span>
            <div class="metric-value" style="color: #558B2F;">{summary['tolerance_count']}</div>
            <div class="metric-label">Within Tolerance</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #F57C00;">
            <span class="metric-icon">&#9888;&#65039;</span>
            <div class="metric-value" style="color: #E65100;">{summary['variance_count']}</div>
            <div class="metric-label">With Variance</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        total_unmatched = summary['unmatched_manual'] + summary['unmatched_daftra']
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #C62828;">
            <span class="metric-icon">&#128308;</span>
            <div class="metric-value" style="color: #C62828;">{total_unmatched}</div>
            <div class="metric-label">Unmatched</div>
        </div>
        """, unsafe_allow_html=True)
