"""Page setup and CSS styles for AURIX Reconciliation."""

import streamlit as st


def setup_page():
    """Configure Streamlit page settings and custom CSS."""
    st.set_page_config(
        page_title="AURIX Reconciliation | BPKH Limited",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* ── Animated Header ── */
    .main-header {
        background: linear-gradient(135deg, #0D3B0E 0%, #1B5E20 30%, #2E7D32 60%, #388E3C 100%);
        padding: 2.5rem 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(27, 94, 32, 0.35), 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -30%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 70%);
        border-radius: 50%;
    }
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%);
        border-radius: 50%;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    .main-header .subtitle {
        color: #A5D6A7;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    .header-badges {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
        flex-wrap: wrap;
    }
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-gold {
        background: linear-gradient(135deg, #FFD700, #FFC107);
        color: #1B5E20;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    }
    .badge-glass {
        background: rgba(255, 255, 255, 0.12);
        color: white;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .badge-ai {
        background: linear-gradient(135deg, #7C4DFF, #536DFE);
        color: white;
        box-shadow: 0 2px 8px rgba(124, 77, 255, 0.3);
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: white;
        padding: 1.5rem 1.25rem;
        border-radius: 14px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
        border-left: 5px solid #1B5E20;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 80px;
        height: 80px;
        background: radial-gradient(circle at top right, rgba(27,94,32,0.04), transparent 70%);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1B5E20;
        line-height: 1;
        letter-spacing: -1px;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.4rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Status Pills ── */
    .status-matched { background-color: #E8F5E9; color: #2E7D32; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
    .status-variance { background-color: #FFF3E0; color: #E65100; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
    .status-unmatched { background-color: #FFEBEE; color: #C62828; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #F8F9FA;
        padding: 0.4rem;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        padding: 0.65rem 1.25rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E8F5E9;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1B5E20, #2E7D32) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(27, 94, 32, 0.3) !important;
    }

    /* ── Data Tables ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Section Cards ── */
    .section-card {
        background: white;
        border-radius: 14px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        overflow: hidden;
        margin-bottom: 1.5rem;
    }
    .section-header {
        padding: 1rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-body {
        padding: 1.5rem;
    }

    /* ── Insight Cards ── */
    .insight-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        border-top: 4px solid #1B5E20;
        transition: all 0.3s ease;
    }
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0,0,0,0.1);
    }
    .insight-card .insight-title {
        font-weight: 700;
        color: #1B5E20;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .insight-card .insight-body {
        color: #424242;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    /* ── Audit Badge ── */
    .audit-badge {
        background: linear-gradient(135deg, #FFD700, #FFC107);
        color: #1B5E20;
        padding: 0.5rem 1.25rem;
        border-radius: 10px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.85rem;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
        letter-spacing: 0.3px;
    }

    /* ── Export Section ── */
    .export-section {
        background: linear-gradient(135deg, #F8F9FA 0%, #ECEFF1 100%);
        border-radius: 14px;
        padding: 2rem;
        margin-top: 1rem;
    }
    .export-section h3 {
        color: #1B5E20;
        margin: 0 0 1rem 0;
    }

    /* ── Empty State ── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
    }
    .empty-state .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
    }
    .empty-state h2 {
        color: #1B5E20;
        font-weight: 700;
        margin: 0 0 0.5rem;
    }
    .empty-state p {
        color: #757575;
        font-size: 1rem;
        margin: 0;
    }

    /* ── Developer Footer ── */
    .dev-footer {
        text-align: center;
        padding: 1rem 0.5rem;
        border-top: 1px solid #E0E0E0;
        margin-top: 0.5rem;
    }
    .dev-footer .dev-name {
        font-weight: 700;
        font-size: 0.82rem;
        color: #1B5E20;
        letter-spacing: 0.3px;
    }
    .dev-footer .dev-role {
        font-size: 0.72rem;
        color: #888;
        margin-top: 0.15rem;
    }
    .dev-footer .dev-version {
        display: inline-block;
        background: linear-gradient(135deg, #1B5E20, #2E7D32);
        color: white;
        padding: 0.15rem 0.6rem;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 600;
        margin-top: 0.5rem;
        letter-spacing: 0.5px;
    }

    /* ── Sidebar Styling ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FAFAFA 0%, #F5F5F5 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #1B5E20;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header with BPKH branding."""
    st.markdown("""
    <div class="main-header">
        <h1>AURIX Reconciliation Module</h1>
        <p class="subtitle">BPKH Limited &bull; Automated Daftra-Manual Journal Reconciliation &bull; Islamic Finance Suite</p>
        <div class="header-badges">
            <span class="header-badge badge-gold">PSAK 109 Compliant</span>
            <span class="header-badge badge-gold">AAOIFI Standards</span>
            <span class="header-badge badge-ai">AI-Powered v2.0</span>
            <span class="header-badge badge-glass">Multi-Agent Architecture</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
