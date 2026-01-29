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

    # Key Insights
    st.markdown("### Key Insights")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"""
        **Total Net Variance:** SAR {summary['total_net_variance']:,.2f}

        **Largest Single Variance:**
        - COA: {int(summary['largest_variance_coa']) if summary['largest_variance_coa'] else 'N/A'}
        - Amount: SAR {summary['largest_variance_amount']:,.2f}
        """)

    with col_b:
        match_rate = (summary['matched_count'] + summary['tolerance_count']) / summary['total_coa_accounts'] * 100
        health = "Excellent" if match_rate >= 95 else "Good" if match_rate >= 80 else "Needs Attention"
        health_icon = "green" if match_rate >= 95 else "yellow" if match_rate >= 80 else "red"
        st.markdown(f"""
        **Match Rate:** {match_rate:.1f}%

        **Reconciliation Health:**
        :{health_icon}_circle: {health}
        """)
