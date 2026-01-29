"""Dashboard tab rendering for AURIX Reconciliation."""

import streamlit as st
from typing import Dict, Any
import pandas as pd

from aurix.visualizer import ReconciliationVisualizer


def render_dashboard_tab(summary: Dict[str, Any], coa_recon: pd.DataFrame):
    """Render the Dashboard tab with charts and key insights."""
    col1, col2 = st.columns(2)

    with col1:
        fig_donut = ReconciliationVisualizer.create_status_donut(summary)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        fig_bar = ReconciliationVisualizer.create_comparison_bar(summary)
        st.plotly_chart(fig_bar, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig_waterfall = ReconciliationVisualizer.create_variance_waterfall(coa_recon)
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col4:
        fig_heatmap = ReconciliationVisualizer.create_variance_heatmap(coa_recon)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # Key Insights section
    match_rate = (summary['matched_count'] + summary['tolerance_count']) / summary['total_coa_accounts'] * 100
    health = "Excellent" if match_rate >= 95 else "Good" if match_rate >= 80 else "Needs Attention"
    health_color = "#2E7D32" if match_rate >= 95 else "#F57C00" if match_rate >= 80 else "#C62828"
    health_bg = "#E8F5E9" if match_rate >= 95 else "#FFF3E0" if match_rate >= 80 else "#FFEBEE"

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">&#128200; Variance Overview</div>
            <div class="insight-body">
                <div style="font-size: 1.8rem; font-weight: 800; color: #1B5E20; letter-spacing: -1px;">
                    SAR {summary['total_net_variance']:,.2f}
                </div>
                <div style="color: #888; font-size: 0.8rem; margin-top: 0.25rem;">Total Net Variance</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        lv_coa = int(summary['largest_variance_coa']) if summary['largest_variance_coa'] else 'N/A'
        st.markdown(f"""
        <div class="insight-card" style="border-top-color: #F57C00;">
            <div class="insight-title" style="color: #E65100;">&#128269; Largest Variance</div>
            <div class="insight-body">
                <div style="font-size: 1.8rem; font-weight: 800; color: #E65100; letter-spacing: -1px;">
                    COA {lv_coa}
                </div>
                <div style="color: #888; font-size: 0.8rem; margin-top: 0.25rem;">
                    SAR {summary['largest_variance_amount']:,.2f}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown(f"""
        <div class="insight-card" style="border-top-color: {health_color};">
            <div class="insight-title" style="color: {health_color};">&#127919; Reconciliation Health</div>
            <div class="insight-body">
                <div style="font-size: 1.8rem; font-weight: 800; color: {health_color}; letter-spacing: -1px;">
                    {match_rate:.1f}%
                </div>
                <div style="display: inline-block; background: {health_bg}; color: {health_color};
                            padding: 0.2rem 0.75rem; border-radius: 20px; font-size: 0.75rem;
                            font-weight: 700; margin-top: 0.3rem;">{health}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
