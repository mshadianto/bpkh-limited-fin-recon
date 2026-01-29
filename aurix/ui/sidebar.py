"""Sidebar rendering for AURIX Reconciliation."""

import os
import streamlit as st
import pandas as pd
from typing import Tuple, Optional

from aurix.config import ReconciliationConfig
from aurix.ai import LANGCHAIN_AVAILABLE, SKLEARN_AVAILABLE
from aurix.agents import CREWAI_AVAILABLE


def render_sidebar() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], ReconciliationConfig]:
    """Render sidebar with file upload and configuration options."""
    with st.sidebar:
        # Logo / brand
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.25rem;">&#9878;&#65039;</div>
            <div style="font-weight: 800; font-size: 1.1rem; color: #1B5E20; letter-spacing: -0.5px;">AURIX</div>
            <div style="font-size: 0.7rem; color: #999; font-weight: 500; letter-spacing: 1px; text-transform: uppercase;">Reconciliation</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Data Source")

        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload Excel file with 'Jurnal Manual' and 'Daftra' sheets"
        )

        df_manual = None
        df_daftra = None

        if uploaded_file:
            try:
                xl = pd.ExcelFile(uploaded_file)
                if 'Jurnal Manual' in xl.sheet_names:
                    df_manual = pd.read_excel(uploaded_file, sheet_name='Jurnal Manual')
                    st.success(f"Jurnal Manual: {len(df_manual)} rows")
                else:
                    st.error("Sheet 'Jurnal Manual' not found")
                if 'Daftra' in xl.sheet_names:
                    df_daftra = pd.read_excel(uploaded_file, sheet_name='Daftra')
                    st.success(f"Daftra: {len(df_daftra)} rows")
                else:
                    st.error("Sheet 'Daftra' not found")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")

        st.markdown("---")
        st.markdown("### Configuration")

        tolerance = st.number_input(
            "Tolerance Amount (SAR)",
            min_value=0.0, max_value=1000.0, value=1.0, step=0.1,
            help="Maximum difference considered as matched"
        )
        config = ReconciliationConfig(tolerance_amount=tolerance)

        st.markdown("---")
        st.markdown("### Quick Stats")
        if df_manual is not None:
            with st.expander("Jurnal Manual Preview"):
                st.dataframe(df_manual.head(3), use_container_width=True)
        if df_daftra is not None:
            with st.expander("Daftra Preview"):
                st.dataframe(df_daftra.head(3), use_container_width=True)

        st.markdown("---")
        st.markdown("### System Status")

        groq_api_key = os.getenv("GROQ_API_KEY")

        # Status indicators
        statuses = []
        if groq_api_key and LANGCHAIN_AVAILABLE:
            statuses.append(("LangChain + Groq", True))
        else:
            statuses.append(("LangChain + Groq", False))

        statuses.append(("ML Anomaly (sklearn)", SKLEARN_AVAILABLE))
        statuses.append(("Multi-Agent (CrewAI)", CREWAI_AVAILABLE))

        status_html = ""
        for name, ok in statuses:
            color = "#2E7D32" if ok else "#BDBDBD"
            icon = "&#9679;" if ok else "&#9675;"
            label = "Active" if ok else "Inactive"
            status_html += f"""
            <div style="display: flex; align-items: center; justify-content: space-between;
                        padding: 0.35rem 0; font-size: 0.8rem;">
                <span style="color: #424242; font-weight: 500;">{name}</span>
                <span style="color: {color}; font-weight: 600; font-size: 0.72rem;
                             display: flex; align-items: center; gap: 0.25rem;">
                    {icon} {label}
                </span>
            </div>
            """

        st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 0.75rem 1rem;
                    box-shadow: 0 1px 6px rgba(0,0,0,0.06);">
            {status_html}
        </div>
        """, unsafe_allow_html=True)

        if not groq_api_key:
            st.caption("Set GROQ_API_KEY in .env for AI features")

        # Developer footer
        st.markdown("---")
        st.markdown("""
        <div class="dev-footer">
            <div class="dev-name">MS Hadianto</div>
            <div class="dev-role">Audit Committee @BPKH 2026</div>
            <div class="dev-version">AURIX v2.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    return df_manual, df_daftra, config
