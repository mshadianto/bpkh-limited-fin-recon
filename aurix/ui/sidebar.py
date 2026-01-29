"""Sidebar rendering for AURIX Reconciliation."""

import os
import streamlit as st
import pandas as pd
from typing import Tuple, Optional

from aurix.config import ReconciliationConfig
from aurix.ai import LANGCHAIN_AVAILABLE


def render_sidebar() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], ReconciliationConfig]:
    """Render sidebar with file upload and configuration options."""
    with st.sidebar:
        st.markdown("### 📁 Data Source")

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
        groq_api_key = os.getenv("GROQ_API_KEY")
        st.markdown("### AI Assistant")
        if groq_api_key and LANGCHAIN_AVAILABLE:
            st.success("AI Features Enabled")
        elif not LANGCHAIN_AVAILABLE:
            st.warning("Install: `pip install langchain-groq`")
        else:
            st.info("Set GROQ_API_KEY in .env")

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p><strong>AURIX v2.0.0</strong></p>
            <p>Built for BPKH Audit Committee</p>
            <p>Phase 2 & 3: AI + Multi-Agent</p>
        </div>
        """, unsafe_allow_html=True)

    return df_manual, df_daftra, config
