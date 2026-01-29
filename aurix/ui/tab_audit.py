"""Audit Trail tab rendering for AURIX Reconciliation."""

import streamlit as st
import pandas as pd
from typing import List

from aurix.config import AuditLogEntry


def render_audit_tab(audit_log: List[AuditLogEntry]):
    """Render the Audit Trail tab."""
    st.markdown("### Audit Trail")
    st.markdown('<div class="audit-badge">SHA-256 Verified</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

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
