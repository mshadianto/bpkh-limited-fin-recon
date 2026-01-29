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
        # Brand
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-name">
                <span class="sidebar-brand-accent">A</span>URIX
            </div>
            <div class="sidebar-brand-sub">RECONCILIATION ENGINE</div>
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

        if df_manual is not None or df_daftra is not None:
            st.markdown("---")
            st.markdown("### Preview")
            if df_manual is not None:
                with st.expander("Jurnal Manual"):
                    st.dataframe(df_manual.head(3), use_container_width=True)
            if df_daftra is not None:
                with st.expander("Daftra"):
                    st.dataframe(df_daftra.head(3), use_container_width=True)

        st.markdown("---")
        st.markdown("### System")

        groq_api_key = os.getenv("GROQ_API_KEY")

        statuses = [
            ("LangChain + Groq", bool(groq_api_key and LANGCHAIN_AVAILABLE)),
            ("ML Anomaly", SKLEARN_AVAILABLE),
            ("Multi-Agent", CREWAI_AVAILABLE),
        ]

        for name, ok in statuses:
            dot_class = "sys-dot-on" if ok else "sys-dot-off"
            st.markdown(f"""
            <div class="sys-status">
                <div class="sys-dot {dot_class}"></div>
                <span class="sys-label">{name}</span>
            </div>
            """, unsafe_allow_html=True)

        if not groq_api_key:
            st.caption("Set `GROQ_API_KEY` in .env")

        st.markdown("---")

        # Developer info
        st.markdown("""
        <div class="sidebar-dev">
            <div class="sidebar-dev-name">MS Hadianto</div>
            <div class="sidebar-dev-role">Audit Committee @ BPKH 2026</div>
            <div class="sidebar-dev-badge">AURIX v2.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    return df_manual, df_daftra, config
