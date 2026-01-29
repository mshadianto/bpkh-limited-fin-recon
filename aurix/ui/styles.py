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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(27, 94, 32, 0.3);
    }
    .main-header h1 { color: white; margin: 0; font-weight: 700; font-size: 2rem; }
    .main-header p { color: #C8E6C9; margin: 0.5rem 0 0 0; font-size: 1rem; }

    .metric-card {
        background: white; padding: 1.5rem; border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08); border-left: 4px solid #1B5E20;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1B5E20; }
    .metric-label { font-size: 0.9rem; color: #666; margin-top: 0.25rem; }

    .status-matched { background-color: #E8F5E9; color: #2E7D32; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 500; }
    .status-variance { background-color: #FFF3E0; color: #E65100; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 500; }
    .status-unmatched { background-color: #FFEBEE; color: #C62828; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 500; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #F5F5F5; border-radius: 8px; padding: 0.75rem 1.5rem; }
    .stTabs [aria-selected="true"] { background-color: #1B5E20 !important; color: white !important; }
    div[data-testid="stDataFrame"] { border: 1px solid #E0E0E0; border-radius: 8px; }
    .audit-badge { background: #FFD700; color: #1B5E20; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header with BPKH branding."""
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ AURIX Reconciliation Module</h1>
        <p>BPKH Limited • Automated Daftra-Manual Journal Reconciliation • Islamic Finance Suite</p>
    </div>
    """, unsafe_allow_html=True)
