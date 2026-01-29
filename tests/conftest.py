"""Shared fixtures for AURIX Reconciliation tests."""

import pytest
import numpy as np
import pandas as pd

from aurix.config import ReconciliationConfig, ReconciliationStatus
from aurix.engine import ReconciliationEngine


@pytest.fixture
def default_config():
    """ReconciliationConfig with default tolerance=1.0 SAR."""
    return ReconciliationConfig()


@pytest.fixture
def raw_manual_df():
    """Raw Manual Journal DataFrame with edge cases.

    6 rows:
    - 2 rows COA 1001 (aggregation test) + 1 row COA 1001 with string numeric
    - 1 row COA 2001 (will have variance vs daftra)
    - 1 row COA 3001 (unmatched in manual only)
    - 1 row with NaN Tanggal (should be dropped during cleaning)
    """
    return pd.DataFrame({
        "Tanggal": ["2024-01-15", "2024-01-16", "2024-02-01", "2024-02-10", None, "2024-01-20"],
        "COA Daftra": [1001, 1001, 2001, 3001, 9999, 1001],
        "COA Daftra Name": ["Cash", "Cash", "Revenue", "Expense", "Ghost", "Cash"],
        "Debit-SAR": [1000.0, 500.0, 0.0, 250.0, 100.0, "200.00"],
        "Kredit-SAR": [0.0, 0.0, 3000.0, 0.0, 0.0, 0.0],
        "Nilai Mutasi": [1000.0, 500.0, -3000.0, 250.0, 100.0, 200.0],
        "Uraian": ["Deposit A", "Deposit B", "Sales Jan", "Office Supply", "Null date row", "Deposit C"],
        "Ref. No": ["MJ-001", "MJ-002", "MJ-003", "MJ-004", "MJ-005", "MJ-006"],
        "Rekening": ["ACC1", "ACC1", "ACC2", "ACC3", "ACC9", "ACC1"],
        "COA Manual": [10010, 10010, 20010, 30010, 99990, 10010],
        "Month": [1, 1, 2, 2, 1, 1],
        "Year": [2024, 2024, 2024, 2024, 2024, 2024],
    })


@pytest.fixture
def raw_daftra_df():
    """Raw Daftra Export DataFrame.

    4 rows:
    - 2 rows Account Code 1001 (matches manual 1001, same amounts → MATCHED)
    - 1 row Account Code 2001 (different credit → creates VARIANCE)
    - 1 row Account Code 4001 (unmatched in daftra only)
    - No rows for COA 3001 (so manual 3001 becomes UNMATCHED_MANUAL)
    """
    return pd.DataFrame({
        "Date": ["2024-01-15", "2024-01-16", "2024-02-01", "2024-03-01"],
        "Account Code": [1001, 1001, 2001, 4001],
        "Account": ["Cash", "Cash", "Revenue", "Receivable"],
        "Debit": [1000.0, 500.0, 0.0, 800.0],
        "Credit": [0.0, 0.0, 2900.0, 0.0],
        "Nilai Mutasi": [1000.0, 500.0, -2900.0, 800.0],
        "Description": ["Deposit A", "Deposit B", "Sales Jan", "Invoice X"],
        "Number": ["DE-001", "DE-002", "DE-003", "DE-004"],
        "Source": ["Bank", "Bank", "Sales", "AR"],
        "Month": [1, 1, 2, 3],
        "Year": [2024, 2024, 2024, 2024],
    })


@pytest.fixture
def engine(default_config):
    """ReconciliationEngine with default config."""
    return ReconciliationEngine(default_config)


@pytest.fixture
def cleaned_manual_df(engine, raw_manual_df):
    """Cleaned Manual Journal DataFrame."""
    return engine.clean_manual_data(raw_manual_df)


@pytest.fixture
def cleaned_daftra_df(engine, raw_daftra_df):
    """Cleaned Daftra Export DataFrame."""
    return engine.clean_daftra_data(raw_daftra_df)


@pytest.fixture
def coa_recon_df(engine, cleaned_manual_df, cleaned_daftra_df):
    """COA-level reconciliation result."""
    return engine.reconcile_coa_level(cleaned_manual_df, cleaned_daftra_df)


@pytest.fixture
def txn_detail_df(engine, cleaned_manual_df, cleaned_daftra_df):
    """Transaction-level reconciliation result."""
    return engine.reconcile_transaction_level(cleaned_manual_df, cleaned_daftra_df)


@pytest.fixture
def variance_summary(engine, coa_recon_df):
    """Variance summary dict."""
    return engine.generate_variance_summary(coa_recon_df)


@pytest.fixture
def large_coa_recon_df():
    """25-row COA reconciliation DataFrame with injected outliers for ML tests."""
    np.random.seed(42)
    n = 25
    coas = list(range(1000, 1000 + n))

    manual_debit = np.random.uniform(100, 5000, n)
    manual_credit = np.random.uniform(100, 5000, n)
    manual_net = manual_debit - manual_credit

    daftra_debit = manual_debit + np.random.normal(0, 50, n)
    daftra_credit = manual_credit + np.random.normal(0, 50, n)
    daftra_net = daftra_debit - daftra_credit

    # Inject 2 clear outliers
    daftra_debit[0] += 50000
    daftra_net[0] = daftra_debit[0] - daftra_credit[0]
    daftra_credit[1] += 30000
    daftra_net[1] = daftra_debit[1] - daftra_credit[1]

    debit_var = manual_debit - daftra_debit
    credit_var = manual_credit - daftra_credit
    net_var = manual_net - daftra_net
    abs_var = np.abs(net_var)

    statuses = []
    for nv, md, dd in zip(net_var, manual_debit, daftra_debit):
        if abs(nv) == 0:
            statuses.append(ReconciliationStatus.MATCHED.value)
        elif abs(nv) <= 1.0:
            statuses.append(ReconciliationStatus.TOLERANCE.value)
        else:
            statuses.append(ReconciliationStatus.VARIANCE.value)

    return pd.DataFrame({
        "COA": coas,
        "Account_Name": [f"Account_{c}" for c in coas],
        "Manual_Debit": manual_debit,
        "Manual_Credit": manual_credit,
        "Manual_Net": manual_net,
        "Manual_TxnCount": np.random.randint(1, 20, n),
        "Daftra_Debit": daftra_debit,
        "Daftra_Credit": daftra_credit,
        "Daftra_Net": daftra_net,
        "Daftra_TxnCount": np.random.randint(1, 20, n),
        "Debit_Variance": debit_var,
        "Credit_Variance": credit_var,
        "Net_Variance": net_var,
        "Abs_Variance": abs_var,
        "Status": statuses,
    })


@pytest.fixture
def monthly_manual_df():
    """Manual data spanning 4 months for forecasting tests."""
    rows = []
    for month in range(1, 5):
        for coa in [1001, 2001, 3001]:
            rows.append({
                "Tanggal": pd.Timestamp(2024, month, 15),
                "COA Daftra": coa,
                "COA Daftra Name": f"Account_{coa}",
                "Debit-SAR": 1000.0 + month * 100,
                "Kredit-SAR": 500.0,
                "Nilai Mutasi": 500.0 + month * 100,
                "Uraian": f"Txn {month}",
                "Ref. No": f"MJ-{month:03d}",
                "Rekening": "ACC1",
                "COA Manual": coa * 10,
                "Month": month,
                "Year": 2024,
                "_source": "MANUAL",
                "_row_id": len(rows) + 1,
            })
    return pd.DataFrame(rows)


@pytest.fixture
def monthly_daftra_df():
    """Daftra data spanning 4 months for forecasting tests."""
    rows = []
    for month in range(1, 5):
        for coa in [1001, 2001, 3001]:
            rows.append({
                "Date": pd.Timestamp(2024, month, 15),
                "Account Code": coa,
                "Account": f"Account_{coa}",
                "Debit": 1000.0 + month * 80,
                "Credit": 500.0,
                "Nilai Mutasi": 500.0 + month * 80,
                "Description": f"Txn {month}",
                "Number": f"DE-{month:03d}",
                "Source": "Bank",
                "Month": month,
                "Year": 2024,
                "_source": "DAFTRA",
                "_row_id": len(rows) + 1,
            })
    return pd.DataFrame(rows)
