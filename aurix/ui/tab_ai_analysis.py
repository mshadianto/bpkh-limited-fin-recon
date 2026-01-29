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

    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # --- Header Banner ---
    match_rate = (summary['matched_count'] + summary['tolerance_count']) / summary['total_coa_accounts'] * 100
    anomaly_count_display = len(st.session_state.get('ai_anomalies', []))
    high_count = sum(1 for a in st.session_state.get('ai_anomalies', []) if a.get('severity') == 'HIGH')

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%);
                padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
                box-shadow: 0 4px 20px rgba(13, 71, 161, 0.3);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h2 style="color: white; margin: 0; font-weight: 700; font-size: 1.5rem;">
                    AI-Powered Analysis
                </h2>
                <p style="color: #BBDEFB; margin: 0.25rem 0 0 0; font-size: 0.9rem;">
                    Phase 2 &amp; 3: LangChain + ML Anomaly + Multi-Agent
                </p>
            </div>
            <div style="display: flex; gap: 1.5rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="color: white; font-size: 1.5rem; font-weight: 700;">{match_rate:.0f}%</div>
                    <div style="color: #BBDEFB; font-size: 0.75rem;">Match Rate</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: {'#FF8A80' if high_count > 0 else '#A5D6A7'}; font-size: 1.5rem; font-weight: 700;">{anomaly_count_display}</div>
                    <div style="color: #BBDEFB; font-size: 0.75rem;">Anomalies</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: {'#A5D6A7' if match_rate >= 95 else '#FFE082' if match_rate >= 80 else '#FF8A80'}; font-size: 1.5rem; font-weight: 700;">
                        {'Excellent' if match_rate >= 95 else 'Good' if match_rate >= 80 else 'Attention'}
                    </div>
                    <div style="color: #BBDEFB; font-size: 0.75rem;">Health</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Sub-Tabs ---
    sub_tab_labels = ["AI Insights", "ML Anomalies", "Variance Forecast", "Root Cause Analysis"]
    if CREWAI_AVAILABLE:
        sub_tab_labels.append("Multi-Agent Report")

    sub_tabs = st.tabs(sub_tab_labels)

    # ===== Sub-Tab 1: AI Insights + Chat =====
    with sub_tabs[0]:
        _render_insights_subtab(api_key, summary, coa_recon)

    # ===== Sub-Tab 2: ML Anomalies =====
    with sub_tabs[1]:
        _render_ml_anomalies_subtab(coa_recon)

    # ===== Sub-Tab 3: Variance Forecast =====
    with sub_tabs[2]:
        _render_forecast_subtab(df_manual_clean, df_daftra_clean)

    # ===== Sub-Tab 4: Root Cause Analysis =====
    with sub_tabs[3]:
        _render_root_cause_subtab(api_key, coa_recon, txn_detail)

    # ===== Sub-Tab 5: Multi-Agent Report =====
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
        # Generate insights
        if 'ai_insights' not in st.session_state:
            with st.spinner("Generating AI insights..."):
                st.session_state.ai_insights = analyzer.generate_insights(summary, coa_recon)

        st.markdown(f"""
        <div style="background: white; border-radius: 12px; overflow: hidden;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 1rem;">
            <div style="background: linear-gradient(90deg, #1B5E20, #2E7D32);
                        padding: 0.75rem 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.25rem;">&#128161;</span>
                <span style="color: white; font-weight: 600; font-size: 1rem;">Auto-Generated Insights</span>
            </div>
            <div style="padding: 1.25rem; color: #212121; line-height: 1.7; font-size: 0.92rem;">
                {st.session_state.ai_insights.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Regenerate Insights", key="regen_insights"):
            with st.spinner("Regenerating..."):
                st.session_state.ai_insights = analyzer.generate_insights(summary, coa_recon)
            st.rerun()

    with col_ai2:
        # Anomaly detection (rule-based)
        if 'ai_anomalies' not in st.session_state:
            with st.spinner("Detecting anomalies..."):
                st.session_state.ai_anomalies = analyzer.detect_anomalies(coa_recon, summary)

        _render_anomaly_card(st.session_state.ai_anomalies)

    # --- Chat Section ---
    st.markdown("""
    <div style="margin-top: 1.5rem;">
        <div style="background: white; border-radius: 12px; overflow: hidden;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
            <div style="background: linear-gradient(90deg, #4527A0, #5E35B1);
                        padding: 0.75rem 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.25rem;">&#128172;</span>
                <span style="color: white; font-weight: 600; font-size: 1rem;">Chat with AI Assistant</span>
                <span style="color: #D1C4E9; font-size: 0.8rem; margin-left: 0.5rem;">Tanya apa saja tentang hasil reconciliation</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div style="background: #FAFAFA; border-left: 1px solid #E0E0E0; border-right: 1px solid #E0E0E0; padding: 1rem 1.25rem; max-height: 400px; overflow-y: auto;">'
        for chat in st.session_state.chat_history[-5:]:
            chat_html += f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
                <div style="background: #E3F2FD; color: #0D47A1; padding: 0.6rem 1rem;
                            border-radius: 12px 12px 2px 12px; max-width: 80%;
                            font-size: 0.88rem; line-height: 1.5;">
                    {chat['question']}
                </div>
            </div>
            <div style="display: flex; justify-content: flex-start; margin-bottom: 1rem;">
                <div style="background: white; color: #212121; padding: 0.6rem 1rem;
                            border-radius: 12px 12px 12px 2px; max-width: 80%;
                            font-size: 0.88rem; line-height: 1.6; border: 1px solid #E0E0E0;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                    {chat['answer'].replace(chr(10), '<br>')}
                </div>
            </div>
            """
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

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
    """Render the anomaly detection card as single HTML block."""
    severity_styles = {
        "HIGH": {"bg": "#FFEBEE", "border": "#C62828", "badge_bg": "#C62828", "badge_text": "white", "label": "HIGH"},
        "MEDIUM": {"bg": "#FFF3E0", "border": "#F57C00", "badge_bg": "#F57C00", "badge_text": "white", "label": "MEDIUM"},
        "LOW": {"bg": "#FFFDE7", "border": "#F9A825", "badge_bg": "#F9A825", "badge_text": "#212121", "label": "LOW"}
    }

    high_count = sum(1 for a in anomalies if a['severity'] == 'HIGH')
    med_count = sum(1 for a in anomalies if a['severity'] == 'MEDIUM')
    low_count = sum(1 for a in anomalies if a['severity'] == 'LOW')

    if anomalies:
        anomaly_body = ""
        for anomaly in anomalies:
            s = severity_styles.get(anomaly['severity'], severity_styles['LOW'])
            amount_str = f"SAR {anomaly.get('amount', 0):,.2f}" if anomaly.get('amount') else ""
            coa_str = str(anomaly.get('coa', ''))

            anomaly_body += f"""
            <div style="background: {s['bg']}; padding: 0.85rem 1rem; border-radius: 8px;
                        margin-bottom: 0.6rem; border-left: 4px solid {s['border']}; color: #212121;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <span style="background: {s['badge_bg']}; color: {s['badge_text']};
                                     padding: 0.1rem 0.5rem; border-radius: 10px;
                                     font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px;">{s['label']}</span>
                        <span style="font-weight: 600; font-size: 0.88rem;">{anomaly['type']}</span>
                    </div>
                    {'<span style="background: white; color: #555; padding: 0.1rem 0.5rem; border-radius: 6px; font-size: 0.7rem; font-weight: 500; font-family: monospace;">COA ' + coa_str + '</span>' if coa_str and coa_str != 'N/A' else ''}
                </div>
                <div style="font-size: 0.85rem; color: #424242; line-height: 1.5;">{anomaly['description']}</div>
                {'<div style="margin-top: 0.35rem; font-size: 0.8rem; color: #616161; font-weight: 500;">' + amount_str + '</div>' if amount_str else ''}
            </div>
            """
    else:
        anomaly_body = """
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">&#9989;</div>
            <div style="color: #2E7D32; font-weight: 600; font-size: 1rem;">No Anomalies Detected</div>
            <div style="color: #666; font-size: 0.85rem; margin-top: 0.25rem;">All reconciliation entries look normal</div>
        </div>
        """

    st.markdown(f"""
    <div style="background: white; border-radius: 12px; overflow: hidden;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 1rem;">
        <div style="background: linear-gradient(90deg, #BF360C, #E65100);
                    padding: 0.75rem 1.25rem; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.25rem;">&#128737;</span>
                <span style="color: white; font-weight: 600; font-size: 1rem;">Anomaly Detection</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                {'<span style="background: #C62828; color: white; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600;">' + str(high_count) + ' HIGH</span>' if high_count > 0 else ''}
                {'<span style="background: #F57C00; color: white; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600;">' + str(med_count) + ' MED</span>' if med_count > 0 else ''}
                {'<span style="background: #F9A825; color: #212121; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600;">' + str(low_count) + ' LOW</span>' if low_count > 0 else ''}
            </div>
        </div>
        <div style="padding: 1rem; max-height: 480px; overflow-y: auto;">
            {anomaly_body}
        </div>
    </div>
    """, unsafe_allow_html=True)


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
        st.info("Click 'Run ML Anomaly Detection' to analyze data with machine learning models.")
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

    # Anomaly cards
    for anomaly in ml_anomalies:
        sev = anomaly['severity']
        bg_color = {"HIGH": "#FFEBEE", "MEDIUM": "#FFF3E0", "LOW": "#FFFDE7"}.get(sev, "#F5F5F5")
        border_color = {"HIGH": "#C62828", "MEDIUM": "#F57C00", "LOW": "#F9A825"}.get(sev, "#999")
        method = anomaly.get('method', 'unknown')
        method_label = "Z-Score" if method == 'z_score' else "IsolationForest" if method == 'isolation_forest' else method

        st.markdown(f"""
        <div style="background: {bg_color}; padding: 1rem; border-radius: 8px;
                    margin-bottom: 0.75rem; border-left: 4px solid {border_color}; color: #212121;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <span style="font-weight: 700; font-size: 0.9rem;">{anomaly['type']}</span>
                <div style="display: flex; gap: 0.4rem;">
                    <span style="background: {border_color}; color: white; padding: 0.1rem 0.5rem;
                                 border-radius: 10px; font-size: 0.7rem; font-weight: 700;">{sev}</span>
                    <span style="background: #E0E0E0; color: #424242; padding: 0.1rem 0.5rem;
                                 border-radius: 10px; font-size: 0.7rem; font-weight: 500;">{method_label}</span>
                </div>
            </div>
            <div style="font-size: 0.85rem; color: #424242; line-height: 1.5;">{anomaly['description']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Scatter plot: anomaly score vs variance
    if_anomalies = [a for a in ml_anomalies if a.get('method') == 'isolation_forest']
    if if_anomalies:
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
            margin=dict(t=30, b=60, l=60, r=40)
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
        st.info("Click 'Generate Forecast' to predict future variance trends from monthly data.")
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
    trend_icons = {"increasing": "red", "decreasing": "green", "stable": "blue"}
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
        line=dict(color='#1B5E20', width=2),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=[hist_months[-1]] + fc_months,
        y=[hist_values[-1]] + fc_values,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#F57C00', width=2, dash='dash'),
        marker=dict(size=8, symbol='diamond')
    ))
    fig.update_layout(
        title="Total Absolute Variance: Historical & Forecast",
        xaxis_title="Month",
        yaxis_title="Total Absolute Variance (SAR)",
        height=400,
        margin=dict(t=50, b=60, l=80, r=40),
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
            line=dict(color='#0D47A1', width=2), marker=dict(size=8)
        ))
        fig2.add_trace(go.Scatter(
            x=[r_hist[-1]] + r_fc_months,
            y=[r_vals[-1]] + r_fc_vals,
            mode='lines+markers', name='Forecast',
            line=dict(color='#F57C00', width=2, dash='dash'), marker=dict(size=8, symbol='diamond')
        ))
        fig2.update_layout(
            title="Match Rate Over Time (%)",
            xaxis_title="Month",
            yaxis_title="Match Rate (%)",
            height=350,
            margin=dict(t=50, b=60, l=60, r=40),
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
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; overflow: hidden;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-top: 1rem;">
                <div style="background: linear-gradient(90deg, #1565C0, #1976D2);
                            padding: 0.75rem 1.25rem;">
                    <span style="color: white; font-weight: 600;">Root Cause: COA {int(coa_code)}</span>
                </div>
                <div style="padding: 1.25rem; color: #212121; line-height: 1.7; font-size: 0.92rem;">
                    {st.session_state[key].replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

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

    st.markdown("""
    <div style="background: #E8F5E9; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; color: #212121;">
        <strong>Multi-Agent System</strong> — Three specialized AI agents collaborate to produce a comprehensive audit report:
        <ul style="margin: 0.5rem 0 0 1rem;">
            <li><strong>Reconciliation Analyst</strong> - Analyzes variances and match patterns</li>
            <li><strong>Fraud Detection Specialist</strong> - Examines anomalies and suspicious patterns</li>
            <li><strong>Audit Report Writer</strong> - Synthesizes findings into executive report</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

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
        with st.spinner("Running full multi-agent analysis (this may take a few moments)..."):
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
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; overflow: hidden;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
            <div style="background: linear-gradient(90deg, #1B5E20, #2E7D32);
                        padding: 0.75rem 1.25rem;">
                <span style="color: white; font-weight: 600;">Audit Report (Multi-Agent)</span>
            </div>
            <div style="padding: 1.25rem; color: #212121; line-height: 1.7; font-size: 0.92rem;">
                {report_text.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

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
