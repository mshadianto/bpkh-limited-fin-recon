"""Enhanced AI Analysis tab for AURIX Reconciliation (Phase 2 & 3)."""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional

from aurix.ai import LANGCHAIN_AVAILABLE, SKLEARN_AVAILABLE
from aurix.agents import CREWAI_AVAILABLE


def render_ai_analysis_tab(
    summary: Dict[str, Any],
    coa_recon: pd.DataFrame,
    txn_detail: pd.DataFrame,
    df_manual_clean: Optional[pd.DataFrame] = None,
    df_daftra_clean: Optional[pd.DataFrame] = None,
):
    """Render the AI Analysis tab with 5 sub-tabs."""
    if not LANGCHAIN_AVAILABLE:
        st.warning("AI features require `langchain-groq`. Install: `pip install langchain-groq`")
        return

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.info("Set GROQ_API_KEY in your .env file to enable AI features.")
        return

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # --- Header metrics ---
    match_rate = (summary['matched_count'] + summary['tolerance_count']) / summary['total_coa_accounts'] * 100
    anomaly_count_display = len(st.session_state.get('ai_anomalies', []))
    health = "Excellent" if match_rate >= 95 else "Good" if match_rate >= 80 else "Attention"

    col_h1, col_h2, col_h3 = st.columns(3)
    col_h1.metric("Match Rate", f"{match_rate:.0f}%")
    col_h2.metric("Anomalies Detected", anomaly_count_display)
    col_h3.metric("Health Status", health)

    st.markdown("---")

    # --- Sub-Tabs ---
    sub_tab_labels = ["AI Insights", "ML Anomalies", "Variance Forecast", "Root Cause Analysis"]
    if CREWAI_AVAILABLE:
        sub_tab_labels.append("Multi-Agent Report")

    sub_tabs = st.tabs(sub_tab_labels)

    with sub_tabs[0]:
        _render_insights_subtab(api_key, summary, coa_recon)

    with sub_tabs[1]:
        _render_ml_anomalies_subtab(coa_recon)

    with sub_tabs[2]:
        _render_forecast_subtab(df_manual_clean, df_daftra_clean)

    with sub_tabs[3]:
        _render_root_cause_subtab(api_key, coa_recon, txn_detail)

    if CREWAI_AVAILABLE:
        with sub_tabs[4]:
            _render_multi_agent_subtab(api_key, coa_recon, txn_detail, summary)


# ─────────────────────────────────────────────────────────────
# Sub-Tab 1: AI Insights + Chat
# ─────────────────────────────────────────────────────────────

def _render_insights_subtab(api_key: str, summary: Dict, coa_recon: pd.DataFrame):
    """AI Insights and Chat interface."""
    from aurix.ai.analyzer import AIAnalyzer

    try:
        analyzer = AIAnalyzer(api_key)
    except Exception as e:
        st.error(f"Failed to initialize AI: {e}")
        return

    col_ai1, col_ai2 = st.columns([3, 2])

    with col_ai1:
        st.markdown("#### Auto-Generated Insights")

        if 'ai_insights' not in st.session_state:
            with st.spinner("Generating AI insights..."):
                st.session_state.ai_insights = analyzer.generate_insights(summary, coa_recon)

        st.markdown(st.session_state.ai_insights)

        if st.button("Regenerate Insights", key="regen_insights"):
            with st.spinner("Regenerating..."):
                st.session_state.ai_insights = analyzer.generate_insights(summary, coa_recon)
            st.rerun()

    with col_ai2:
        if 'ai_anomalies' not in st.session_state:
            with st.spinner("Detecting anomalies..."):
                st.session_state.ai_anomalies = analyzer.detect_anomalies(coa_recon, summary)

        _render_anomaly_card(st.session_state.ai_anomalies)

    # --- Chat Section ---
    st.markdown("---")
    st.markdown("#### Chat with AI Assistant")
    st.caption("Tanya apa saja tentang hasil reconciliation")

    # Chat history display
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history[-5:]:
            with st.chat_message("user"):
                st.markdown(chat['question'])
            with st.chat_message("assistant"):
                st.markdown(chat['answer'])

    # Chat input
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_question = st.text_input(
            "Pertanyaan Anda:",
            placeholder="Contoh: Jelaskan COA dengan variance terbesar...",
            key="ai_chat_input",
            label_visibility="collapsed"
        )
    with col_btn:
        send_clicked = st.button("Kirim", key="send_chat", use_container_width=True)

    if send_clicked and user_question:
        with st.spinner("Thinking..."):
            response = analyzer.chat(user_question, summary, coa_recon)
            st.session_state.chat_history.append({
                "question": user_question,
                "answer": response
            })
        st.rerun()


def _render_anomaly_card(anomalies):
    """Render anomaly detection using native Streamlit components."""
    high_count = sum(1 for a in anomalies if a['severity'] == 'HIGH')
    med_count = sum(1 for a in anomalies if a['severity'] == 'MEDIUM')
    low_count = sum(1 for a in anomalies if a['severity'] == 'LOW')

    badge_parts = []
    if high_count > 0:
        badge_parts.append(f"**{high_count} HIGH**")
    if med_count > 0:
        badge_parts.append(f"**{med_count} MED**")
    if low_count > 0:
        badge_parts.append(f"**{low_count} LOW**")

    st.markdown(f"#### Anomaly Detection ({' / '.join(badge_parts) if badge_parts else 'None'})")

    if not anomalies:
        st.success("No anomalies detected. All reconciliation entries look normal.")
        return

    severity_icons = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}

    for anomaly in anomalies:
        sev = anomaly['severity']
        icon = severity_icons.get(sev, "⚪")
        coa_str = str(anomaly.get('coa', ''))
        coa_tag = f" `COA {coa_str}`" if coa_str and coa_str != 'N/A' else ""
        amount = anomaly.get('amount', 0)
        amount_str = f" — SAR {amount:,.2f}" if amount else ""

        st.markdown(
            f"{icon} **{sev}** | {anomaly['type']}{coa_tag}\n\n"
            f"{anomaly['description']}{amount_str}"
        )


# ─────────────────────────────────────────────────────────────
# Sub-Tab 2: ML Anomalies
# ─────────────────────────────────────────────────────────────

def _render_ml_anomalies_subtab(coa_recon: pd.DataFrame):
    """ML-based anomaly detection with IsolationForest and Z-score."""
    if not SKLEARN_AVAILABLE:
        st.warning("ML anomaly detection requires scikit-learn. Install: `pip install scikit-learn`")
        return

    from aurix.ai.ml_anomaly import MLAnomalyDetector

    if len(coa_recon) < 5:
        st.info("Need at least 5 COA entries for ML anomaly detection.")
        return

    if st.button("Run ML Anomaly Detection", key="run_ml"):
        with st.spinner("Running IsolationForest + Z-Score analysis..."):
            detector = MLAnomalyDetector(contamination=0.1)
            st.session_state.ml_anomalies = detector.detect_all(coa_recon)

    if 'ml_anomalies' not in st.session_state:
        st.info("Click **Run ML Anomaly Detection** to analyze data with machine learning models.")
        return

    ml_anomalies = st.session_state.ml_anomalies

    if not ml_anomalies:
        st.success("No ML anomalies detected. All data points appear normal.")
        return

    # Severity summary
    high = sum(1 for a in ml_anomalies if a['severity'] == 'HIGH')
    med = sum(1 for a in ml_anomalies if a['severity'] == 'MEDIUM')
    low = sum(1 for a in ml_anomalies if a['severity'] == 'LOW')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ML Anomalies", len(ml_anomalies))
    col2.metric("HIGH", high)
    col3.metric("MEDIUM", med)
    col4.metric("LOW", low)

    st.markdown("---")

    # Anomaly list — native markdown per anomaly
    severity_icons = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}

    for anomaly in ml_anomalies:
        sev = anomaly['severity']
        icon = severity_icons.get(sev, "⚪")
        method = anomaly.get('method', 'unknown')
        method_label = "Z-Score" if method == 'z_score' else "IsolationForest" if method == 'isolation_forest' else method

        st.markdown(
            f"{icon} **{sev}** | {anomaly['type']} · `{method_label}`\n\n"
            f"{anomaly['description']}"
        )

    # Scatter plot: anomaly score vs variance
    if_anomalies = [a for a in ml_anomalies if a.get('method') == 'isolation_forest']
    if if_anomalies:
        st.markdown("---")
        st.markdown("#### Isolation Forest: Anomaly Score vs Net Variance")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[a['amount'] for a in if_anomalies],
            y=[a.get('anomaly_score', 0) for a in if_anomalies],
            mode='markers+text',
            text=[f"COA {a['coa']}" for a in if_anomalies],
            textposition='top center',
            marker=dict(
                size=12,
                color=[a.get('anomaly_score', 0) for a in if_anomalies],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Score")
            ),
            hovertemplate="<b>COA %{text}</b><br>Net Variance: SAR %{x:,.2f}<br>Score: %{y:.3f}<extra></extra>"
        ))
        fig.update_layout(
            xaxis_title="Net Variance (SAR)",
            yaxis_title="Anomaly Score (lower = more anomalous)",
            height=400,
            margin=dict(t=30, b=60, l=60, r=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Sub-Tab 3: Variance Forecast
# ─────────────────────────────────────────────────────────────

def _render_forecast_subtab(df_manual_clean, df_daftra_clean):
    """Variance forecasting with linear regression."""
    if not SKLEARN_AVAILABLE:
        st.warning("Variance forecasting requires scikit-learn. Install: `pip install scikit-learn`")
        return

    if df_manual_clean is None or df_daftra_clean is None:
        st.info("Clean data not available for forecasting.")
        return

    from aurix.ai.forecasting import VarianceForecaster

    if st.button("Generate Forecast", key="run_forecast"):
        with st.spinner("Aggregating monthly variances and forecasting..."):
            forecaster = VarianceForecaster()
            monthly_df = forecaster.aggregate_monthly_variances(df_manual_clean, df_daftra_clean)
            st.session_state.monthly_variances = monthly_df

            if len(monthly_df) >= 3:
                forecast_var = forecaster.forecast_linear(monthly_df, "total_abs_variance")
                forecast_rate = forecaster.forecast_linear(monthly_df, "match_rate")
                st.session_state.forecast_result = forecast_var
                st.session_state.forecast_rate = forecast_rate
            else:
                st.session_state.forecast_result = {"error": "Insufficient data (need at least 3 months)"}
                st.session_state.forecast_rate = {"error": "Insufficient data"}

    if 'forecast_result' not in st.session_state:
        st.info("Click **Generate Forecast** to predict future variance trends from monthly data.")
        return

    forecast = st.session_state.forecast_result

    if 'error' in forecast:
        st.warning(forecast['error'])
        if 'monthly_variances' in st.session_state:
            st.markdown("#### Monthly Data (insufficient for forecast)")
            st.dataframe(st.session_state.monthly_variances, use_container_width=True)
        return

    # Trend metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Trend Direction", forecast['trend_direction'].capitalize())
    col2.metric("Slope (SAR/month)", f"{forecast['slope']:,.2f}")
    col3.metric("R-squared", f"{forecast['r_squared']:.3f}")

    st.markdown("---")

    # Plotly chart: historical + forecast
    hist_months = [h['month'] for h in forecast['historical']]
    hist_values = [h['value'] for h in forecast['historical']]
    fc_months = [f['month'] for f in forecast['forecast']]
    fc_values = [f['value'] for f in forecast['forecast']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_months, y=hist_values,
        mode='lines+markers',
        name='Historical',
        line=dict(color='#1D1D1F', width=2),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=[hist_months[-1]] + fc_months,
        y=[hist_values[-1]] + fc_values,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#FF9500', width=2, dash='dash'),
        marker=dict(size=8, symbol='diamond')
    ))
    fig.update_layout(
        title="Total Absolute Variance: Historical & Forecast",
        xaxis_title="Month",
        yaxis_title="Total Absolute Variance (SAR)",
        height=400,
        margin=dict(t=50, b=60, l=80, r=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Match rate over time
    if 'forecast_rate' in st.session_state and 'error' not in st.session_state.forecast_rate:
        rate_data = st.session_state.forecast_rate
        r_hist = [h['month'] for h in rate_data['historical']]
        r_vals = [h['value'] for h in rate_data['historical']]
        r_fc_months = [f['month'] for f in rate_data['forecast']]
        r_fc_vals = [f['value'] for f in rate_data['forecast']]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=r_hist, y=r_vals,
            mode='lines+markers', name='Historical',
            line=dict(color='#0071E3', width=2), marker=dict(size=8)
        ))
        fig2.add_trace(go.Scatter(
            x=[r_hist[-1]] + r_fc_months,
            y=[r_vals[-1]] + r_fc_vals,
            mode='lines+markers', name='Forecast',
            line=dict(color='#FF9500', width=2, dash='dash'), marker=dict(size=8, symbol='diamond')
        ))
        fig2.update_layout(
            title="Match Rate Over Time (%)",
            xaxis_title="Month",
            yaxis_title="Match Rate (%)",
            height=350,
            margin=dict(t=50, b=60, l=60, r=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Sub-Tab 4: Root Cause Analysis
# ─────────────────────────────────────────────────────────────

def _render_root_cause_subtab(api_key: str, coa_recon: pd.DataFrame, txn_detail: pd.DataFrame):
    """Root cause analysis per COA using LLM."""
    from aurix.ai.base import LLMProvider
    from aurix.ai.root_cause import RootCauseAnalyzer
    from aurix.config import ReconciliationStatus

    variance_coas = coa_recon[coa_recon['Status'] == ReconciliationStatus.VARIANCE.value]

    if len(variance_coas) == 0:
        st.success("No variance COAs to analyze. All accounts are matched!")
        return

    # Single COA analysis
    st.markdown("#### Analyze Single COA")
    coa_options = []
    for _, row in variance_coas.head(20).iterrows():
        coa_code = int(row['COA']) if pd.notna(row.get('COA')) else 'N/A'
        name = str(row.get('Account_Name', ''))[:30]
        var = row.get('Net_Variance', 0)
        coa_options.append(f"COA {coa_code} - {name} (SAR {var:,.2f})")

    selected = st.selectbox("Select COA to analyze", options=coa_options, key="rc_coa_select")

    if st.button("Analyze Root Cause", key="rc_single"):
        idx = coa_options.index(selected)
        row = variance_coas.iloc[idx]
        coa_code = row.get('COA')

        with st.spinner(f"Analyzing COA {int(coa_code) if pd.notna(coa_code) else 'N/A'}..."):
            provider = LLMProvider(api_key)
            analyzer = RootCauseAnalyzer(provider)
            coa_txn = txn_detail[txn_detail['COA'] == coa_code] if coa_code is not None else pd.DataFrame()
            ml_anomalies = st.session_state.get('ml_anomalies', [])
            result = analyzer.analyze_single_coa(row, coa_txn, ml_anomalies)
            st.session_state[f'rc_single_{int(coa_code)}'] = result

    # Display single result
    if selected:
        idx = coa_options.index(selected)
        row = variance_coas.iloc[idx]
        coa_code = row.get('COA')
        key = f'rc_single_{int(coa_code)}' if pd.notna(coa_code) else None
        if key and key in st.session_state:
            st.markdown(f"**Root Cause Analysis: COA {int(coa_code)}**")
            st.markdown(st.session_state[key])

    # Batch analysis
    st.markdown("---")
    st.markdown("#### Batch: Analyze Top 5 Variances")

    if st.button("Analyze Top 5", key="rc_batch"):
        with st.spinner("Analyzing top 5 variance COAs..."):
            provider = LLMProvider(api_key)
            analyzer = RootCauseAnalyzer(provider)
            ml_anomalies = st.session_state.get('ml_anomalies', [])
            results = analyzer.analyze_top_variances(coa_recon, txn_detail, ml_anomalies, top_n=5)
            st.session_state.root_cause_results = results

    if 'root_cause_results' in st.session_state:
        for rc in st.session_state.root_cause_results:
            with st.expander(f"COA {rc['coa']} - {rc['account_name']} (SAR {rc['net_variance']:,.2f})"):
                st.markdown(rc['analysis'])


# ─────────────────────────────────────────────────────────────
# Sub-Tab 5: Multi-Agent Report
# ─────────────────────────────────────────────────────────────

def _render_multi_agent_subtab(
    api_key: str,
    coa_recon: pd.DataFrame,
    txn_detail: pd.DataFrame,
    summary: Dict[str, Any]
):
    """CrewAI multi-agent orchestration for comprehensive audit report."""
    from aurix.agents.orchestrator import AurixCrew

    st.markdown(
        "Three specialized AI agents collaborate to produce a comprehensive audit report:"
    )
    st.markdown(
        "- **Reconciliation Analyst** — Analyzes variances and match patterns\n"
        "- **Fraud Detection Specialist** — Examines anomalies and suspicious patterns\n"
        "- **Audit Report Writer** — Synthesizes findings into executive report"
    )

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        run_full = st.button("Run Full Analysis", key="crew_full", use_container_width=True)
    with col2:
        run_recon = st.button("Recon Agent", key="crew_recon", use_container_width=True)
    with col3:
        run_fraud = st.button("Fraud Agent", key="crew_fraud", use_container_width=True)
    with col4:
        run_report = st.button("Report Agent", key="crew_report", use_container_width=True)

    def _setup_crew():
        crew = AurixCrew(api_key)
        ml_anomalies = st.session_state.get('ml_anomalies', None)
        crew.set_context(coa_recon, txn_detail, summary, ml_anomalies)
        return crew

    if run_full:
        with st.spinner("Running full multi-agent analysis..."):
            crew = _setup_crew()
            result = crew.run()
            if result['success']:
                st.session_state.crew_report = str(result['report'])
            else:
                st.error(f"Crew execution failed: {result['error']}")

    if run_recon:
        with st.spinner("Running Reconciliation Agent..."):
            crew = _setup_crew()
            st.session_state.crew_recon = str(crew.run_single_agent("recon"))

    if run_fraud:
        with st.spinner("Running Fraud Detection Agent..."):
            crew = _setup_crew()
            st.session_state.crew_fraud = str(crew.run_single_agent("fraud"))

    if run_report:
        with st.spinner("Running Report Writer Agent..."):
            crew = _setup_crew()
            st.session_state.crew_report_single = str(crew.run_single_agent("report"))

    # Display results
    if 'crew_report' in st.session_state and st.session_state.crew_report:
        report_text = str(st.session_state.crew_report)
        st.markdown("#### Full Multi-Agent Report")
        st.markdown(report_text)

        st.download_button(
            label="Download Report",
            data=report_text,
            file_name="aurix_multi_agent_report.txt",
            mime="text/plain",
            key="dl_crew_report"
        )

    for key, label in [('crew_recon', 'Reconciliation Agent'), ('crew_fraud', 'Fraud Agent'), ('crew_report_single', 'Report Agent')]:
        if key in st.session_state:
            with st.expander(f"{label} Output"):
                st.markdown(str(st.session_state[key]))
