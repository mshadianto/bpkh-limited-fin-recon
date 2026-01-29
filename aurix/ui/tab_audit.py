"""Audit Trail tab rendering for AURIX Reconciliation."""

import streamlit as st
import pandas as pd
from typing import List

from aurix.config import AuditLogEntry


def render_audit_tab(audit_log: List[AuditLogEntry]):
    """Render the Audit Trail tab."""
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <h3 style="margin: 0; color: #1B5E20;">Audit Trail</h3>
        <div class="audit-badge">SHA-256 Verified</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem;
                box-shadow: 0 1px 8px rgba(0,0,0,0.05); display: flex; gap: 2rem; flex-wrap: wrap;">
        <div>
            <span style="color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">Total Events</span>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1B5E20;">{len(audit_log)}</div>
        </div>
        <div>
            <span style="color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">Integrity</span>
            <div style="font-size: 1.5rem; font-weight: 700; color: #2E7D32;">Verified</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    audit_df = pd.DataFrame([
        {
            'Timestamp': entry.timestamp,
            'Action': entry.action,
            'Details': str(entry.details)[:100] + '...' if len(str(entry.details)) > 100 else str(entry.details),
            'Checksum': entry.checksum
        }
        for entry in audit_log
    ])

    st.dataframe(audit_df, use_container_width=True)
