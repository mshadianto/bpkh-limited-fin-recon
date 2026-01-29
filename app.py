#!/usr/bin/env python3
"""
AURIX Reconciliation Module v2.0.0
BPKH Limited - Islamic Finance Suite

Thin entry point: imports and wires modules from the aurix/ package.
Phase 1: Core Reconciliation Engine
Phase 2: AI-Powered Analysis (LangChain + ML)
Phase 3: Multi-Agent Architecture (CrewAI)
"""

import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from aurix.config import ReconciliationConfig
from aurix.engine import ReconciliationEngine
from aurix.exporter import ReportExporter
from aurix.ai import LANGCHAIN_AVAILABLE
from aurix.ui.styles import setup_page, render_header
from aurix.ui.sidebar import render_sidebar
from aurix.ui.metrics import render_metrics
from aurix.ui.tab_dashboard import render_dashboard_tab
from aurix.ui.tab_ai_analysis import render_ai_analysis_tab
from aurix.ui.tab_coa import render_coa_tab
from aurix.ui.tab_transactions import render_transactions_tab
from aurix.ui.tab_audit import render_audit_tab


def main():
    """Main application entry point."""
    setup_page()
    render_header()

    # Sidebar and data loading
    df_manual, df_daftra, config = render_sidebar()

    if df_manual is None or df_daftra is None:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">&#9878;&#65039;</span>
            <h2>Upload Your Reconciliation Data</h2>
            <p>Upload an Excel file with <strong>Jurnal Manual</strong> and <strong>Daftra</strong>
            sheets to begin automated reconciliation</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Expected Data Format"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Jurnal Manual Sheet:**
                - `Tanggal` — Transaction date
                - `COA Daftra` — Account code (numeric)
                - `Debit-SAR` — Debit amount
                - `Kredit-SAR` — Credit amount
                - `Uraian` — Description
                """)
            with col2:
                st.markdown("""
                **Daftra Sheet:**
                - `Date` — Transaction date
                - `Account Code` — Account code (numeric)
                - `Debit` — Debit amount
                - `Credit` — Credit amount
                - `Description` — Transaction description
                """)
        return

    # Initialize engine and run reconciliation
    engine = ReconciliationEngine(config)

    with st.spinner("Cleaning and preparing data..."):
        df_manual_clean = engine.clean_manual_data(df_manual)
        df_daftra_clean = engine.clean_daftra_data(df_daftra)

    with st.spinner("Performing reconciliation..."):
        coa_recon = engine.reconcile_coa_level(df_manual_clean, df_daftra_clean)
        txn_detail = engine.reconcile_transaction_level(df_manual_clean, df_daftra_clean)
        summary = engine.generate_variance_summary(coa_recon)

    # Render metrics
    render_metrics(summary)
    st.markdown("&nbsp;", unsafe_allow_html=True)

    # Check AI availability
    groq_api_key = os.getenv("GROQ_API_KEY")
    ai_available = bool(groq_api_key and LANGCHAIN_AVAILABLE)

    # Main content tabs
    if ai_available:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Dashboard",
            "AI Analysis",
            "COA Reconciliation",
            "Transaction Detail",
            "Audit Trail"
        ])
    else:
        tab1, tab3, tab4, tab5 = st.tabs([
            "Dashboard",
            "COA Reconciliation",
            "Transaction Detail",
            "Audit Trail"
        ])
        tab2 = None

    with tab1:
        render_dashboard_tab(summary, coa_recon)

    if ai_available and tab2 is not None:
        with tab2:
            render_ai_analysis_tab(
                summary, coa_recon, txn_detail,
                df_manual_clean, df_daftra_clean
            )

    with tab3:
        render_coa_tab(coa_recon)

    with tab4:
        render_transactions_tab(engine, coa_recon, txn_detail, df_manual_clean, df_daftra_clean)

    with tab5:
        render_audit_tab(engine.audit_log)

    # Export section
    st.markdown("---")
    st.markdown("#### Export Full Report")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        excel_buffer = ReportExporter.export_to_excel(
            coa_recon, txn_detail, summary, engine.audit_log
        )
        st.download_button(
            label="Download Excel Report",
            data=excel_buffer,
            file_name=f"AURIX_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_exp2:
        json_report = json.dumps({
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "config": {
                "tolerance_amount": config.tolerance_amount,
                "tolerance_percentage": config.tolerance_percentage
            }
        }, indent=2)
        st.download_button(
            label="Download JSON Summary",
            data=json_report,
            file_name=f"AURIX_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )


if __name__ == "__main__":
    main()
