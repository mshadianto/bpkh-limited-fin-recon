"""Page setup and CSS styles for AURIX Reconciliation — Premium Apple-inspired design."""

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
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --apple-black: #1D1D1F;
        --apple-gray-bg: #F5F5F7;
        --apple-gray-text: #86868B;
        --apple-blue: #0071E3;
        --apple-green: #34C759;
        --apple-orange: #FF9500;
        --apple-red: #FF3B30;
        --apple-teal: #5AC8FA;
        --card-radius: 18px;
        --card-shadow: 0 2px 12px rgba(0,0,0,0.06);
        --card-shadow-hover: 0 8px 30px rgba(0,0,0,0.12);
    }

    * { font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ── Page Background ── */
    .stApp {
        background: linear-gradient(180deg, #F5F5F7 0%, #EEEEF0 100%);
    }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, #1D1D1F 0%, #2C2C2E 100%);
        padding: 2.5rem 3rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(0,113,227,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: 10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(52,199,89,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    .main-header h1 {
        color: #F5F5F7;
        margin: 0;
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: -0.8px;
        position: relative;
        z-index: 1;
    }
    .main-header .subtitle {
        color: #98989D;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: 0.2px;
        position: relative;
        z-index: 1;
    }
    .header-tags {
        display: flex;
        gap: 0.5rem;
        margin-top: 1.4rem;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    .header-tag {
        padding: 0.3rem 0.85rem;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.2s ease;
    }
    .header-tag:hover {
        transform: scale(1.05);
    }
    .tag-blue {
        background: linear-gradient(135deg, #0071E3 0%, #007AFF 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(0,113,227,0.3);
    }
    .tag-muted {
        background: rgba(255,255,255,0.08);
        color: #A1A1A6;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: white;
        padding: 1.5rem 1.5rem 1.25rem;
        border-radius: var(--card-radius);
        box-shadow: var(--card-shadow);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        border: 1px solid rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 3px 3px 0 0;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--card-shadow-hover);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--apple-black);
        line-height: 1;
        letter-spacing: -1.5px;
    }
    .metric-label {
        font-size: 0.72rem;
        color: var(--apple-gray-text);
        margin-top: 0.6rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .metric-bar {
        height: 4px;
        border-radius: 2px;
        background: #E8E8ED;
        margin-top: 0.75rem;
        overflow: hidden;
    }
    .metric-bar-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 1s ease;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(232,232,237,0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 5px;
        border-radius: 14px;
        border: 1px solid rgba(0,0,0,0.04);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        padding: 0.6rem 1.3rem;
        font-weight: 500;
        font-size: 0.85rem;
        color: #1D1D1F;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.5);
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1D1D1F !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }

    /* ── Data Tables ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E8E8ED;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FAFAFA 100%);
        border-right: 1px solid #E8E8ED;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--apple-gray-text);
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ── Buttons ── */
    .stDownloadButton > button,
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.2px !important;
    }
    .stDownloadButton > button:hover,
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }

    /* ── Expanders ── */
    details {
        border: 1px solid #E8E8ED !important;
        border-radius: 14px !important;
        background: white !important;
    }
    details summary {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* ── Metrics (built-in st.metric) ── */
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem 1.25rem;
        border-radius: 14px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: var(--apple-gray-text) !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }

    /* ── File Uploader ── */
    section[data-testid="stFileUploader"] {
        border-radius: 14px;
    }
    section[data-testid="stFileUploader"] > div {
        border-radius: 14px !important;
    }

    /* ── Chat Messages ── */
    div[data-testid="stChatMessage"] {
        border-radius: 14px !important;
        border: 1px solid rgba(0,0,0,0.04) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: #C7C7CC;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #8E8E93; }

    /* ── Toast / Alerts ── */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    /* ── Sidebar Brand ── */
    .sidebar-brand {
        text-align: center;
        padding: 0.5rem 0 0.25rem;
    }
    .sidebar-brand-name {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1D1D1F;
        letter-spacing: -0.5px;
    }
    .sidebar-brand-accent {
        color: #0071E3;
    }
    .sidebar-brand-sub {
        font-size: 0.72rem;
        color: #86868B;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-top: 0.15rem;
    }
    .sidebar-dev {
        text-align: center;
        padding: 0.75rem 0;
    }
    .sidebar-dev-name {
        font-size: 0.8rem;
        font-weight: 600;
        color: #1D1D1F;
    }
    .sidebar-dev-role {
        font-size: 0.7rem;
        color: #86868B;
        margin-top: 0.1rem;
    }
    .sidebar-dev-badge {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.2rem 0.65rem;
        background: #1D1D1F;
        color: white;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    /* ── System Status ── */
    .sys-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0;
    }
    .sys-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .sys-dot-on {
        background: #34C759;
        box-shadow: 0 0 6px rgba(52,199,89,0.4);
    }
    .sys-dot-off {
        background: #C7C7CC;
    }
    .sys-label {
        font-size: 0.78rem;
        color: #48484A;
        font-weight: 500;
    }

    /* ── Empty State ── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        max-width: 480px;
        margin: 2rem auto;
    }
    .empty-icon {
        font-size: 4rem;
        display: block;
        margin-bottom: 1rem;
        opacity: 0.8;
    }
    .empty-state h2 {
        color: #1D1D1F;
        font-weight: 700;
        font-size: 1.5rem;
        letter-spacing: -0.3px;
        margin: 0 0 0.5rem;
    }
    .empty-state p {
        color: #86868B;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header."""
    st.markdown("""
    <div class="main-header">
        <h1>AURIX Reconciliation</h1>
        <p class="subtitle">BPKH Limited &middot; Daftra-Manual Journal Reconciliation &middot; Islamic Finance</p>
        <div class="header-tags">
            <span class="header-tag tag-blue">AI-Powered v2.0</span>
            <span class="header-tag tag-muted">PSAK 109</span>
            <span class="header-tag tag-muted">AAOIFI</span>
            <span class="header-tag tag-muted">Multi-Agent</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
