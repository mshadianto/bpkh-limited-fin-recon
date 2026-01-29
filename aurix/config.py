"""Configuration and data classes for AURIX Reconciliation."""

import hashlib
import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd


class ReconciliationStatus(Enum):
    """Enumeration for reconciliation status types."""
    MATCHED = "✅ Matched"
    VARIANCE = "⚠️ Variance"
    UNMATCHED_MANUAL = "🔴 Only in Manual"
    UNMATCHED_DAFTRA = "🔵 Only in Daftra"
    TOLERANCE = "🟡 Within Tolerance"


@dataclass
class ReconciliationConfig:
    """Configuration parameters for reconciliation process."""
    tolerance_amount: float = 1.0  # SAR
    tolerance_percentage: float = 0.001  # 0.1%
    date_column_manual: str = "Tanggal"
    date_column_daftra: str = "Date"
    coa_column_manual: str = "COA Daftra"
    coa_column_daftra: str = "Account Code"
    debit_column_manual: str = "Debit-SAR"
    credit_column_manual: str = "Kredit-SAR"
    debit_column_daftra: str = "Debit"
    credit_column_daftra: str = "Credit"
    description_column_manual: str = "Uraian"
    description_column_daftra: str = "Description"


@dataclass
class AuditLogEntry:
    """Single audit log entry for traceability."""
    timestamp: str
    action: str
    details: Dict[str, Any]
    user: str = "System"
    checksum: str = ""

    def __post_init__(self):
        """Generate checksum after initialization."""
        content = f"{self.timestamp}{self.action}{json.dumps(self.details, default=str)}{self.user}"
        self.checksum = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class ReconciliationResult:
    """Container for reconciliation results."""
    summary_df: pd.DataFrame
    detail_df: pd.DataFrame
    matched_count: int = 0
    variance_count: int = 0
    unmatched_manual: int = 0
    unmatched_daftra: int = 0
    total_variance_amount: float = 0.0
    audit_log: List[AuditLogEntry] = field(default_factory=list)
