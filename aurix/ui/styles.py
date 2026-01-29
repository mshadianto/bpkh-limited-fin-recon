"""Page setup and CSS styles for AURIX Reconciliation — Apple-inspired design."""

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ── Page Background ── */
    .stApp { background: #F5F5F7; }

    /* ── Header ── */
    .main-header {
        background: #1D1D1F;
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: #F5F5F7;
        margin: 0;
        font-weight: 700;
        font-size: 2rem;
        letter-spacing: -0.5px;
    }
    .main-header .subtitle {
        color: #86868B;
        margin: 0.4rem 0 0 0;
        font-size: 0.95rem;
        font-weight: 400;
    }
    .header-tags {
        display: flex;
        gap: 0.5rem;
        margin-top: 1.2rem;
        flex-wrap: wrap;
    }
    .header-tag {
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    .tag-blue { background: #0071E3; color: white; }
    .tag-muted { background: #2D2D2F; color: #A1A1A6; }

    /* ── Metric Cards ── */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1D1D1F;
        line-height: 1;
        letter-spacing: -1px;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #86868B;
        margin-top: 0.5rem;
        font-weight: 500;
        letter-spacing: 0.2px;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #E8E8ED;
        padding: 4px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 0.85rem;
        color: #1D1D1F;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1D1D1F !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }

    /* ── Data Tables ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E8E8ED;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: white;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #1D1D1F;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #86868B;
    }

    /* ── Audit Badge ── */
    .audit-badge {
        background: #1D1D1F;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 100px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.78rem;
        letter-spacing: 0.2px;
    }

    /* ── Buttons ── */
    .stDownloadButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
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
