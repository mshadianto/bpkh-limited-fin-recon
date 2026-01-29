# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AURIX Reconciliation - Automated financial reconciliation tool for BPKH (Badan Pengelola Keuangan Haji) that matches Daftra accounting system exports against Manual Journal entries. Built for Islamic Finance compliance (PSAK 109, AAOIFI, OJK Regulations, BPKH Internal Audit Standards).

## Commands

```bash
# Create virtual environment (Python 3.10+ required)
python -m venv venv
source venv/bin/activate      # Linux/Mac
.\venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py

# Docker build & run
docker build -t aurix-reconciliation .
docker run -p 8501:8501 aurix-reconciliation
```

No test suite exists. No linter or formatter is configured.

## Architecture

**Single monolithic Streamlit application** (`app.py`, ~1,600 lines) with four core classes:

- `ReconciliationEngine` (line ~113) - Core logic: cleans data, aggregates by COA, outer-join matches, calculates variances, maintains audit log with SHA-256 checksums
- `ReconciliationVisualizer` (line ~423) - Plotly chart generation (status donut, comparison bar, variance waterfall, variance heatmap)
- `ReportExporter` (line ~606) - Multi-sheet Excel export (Executive Summary, COA Reconciliation, Transaction Detail, Audit Trail) with BPKH-branded styling
- `AIAnalyzer` (line ~761) - Optional Groq LLM integration (`llama-3.3-70b-versatile`). Groq import is wrapped in try/except; the app runs without it. Requires `GROQ_API_KEY` env var (copy `.env.example` to `.env`).

**Data flow:**
```
Excel Upload (Manual Journal + Daftra Export)
  → Data Cleaning (column standardization, pd.to_numeric COA conversion, date parsing, NaN row exclusion)
  → ReconciliationEngine.reconcile_coa_level() (groupby COA → outer join → variance calc → status assignment)
  → ReconciliationEngine.reconcile_transaction_level() (detail-level matching)
  → Dashboard (Plotly charts) + AI Analysis (optional) + Excel/JSON/CSV Export
```

**Key dataclasses:** `ReconciliationConfig` (tolerance & column mappings), `AuditLogEntry` (SHA-256 checksummed), `ReconciliationResult` (summary + detail DataFrames + counts)

**ReconciliationStatus enum** (display values include emoji prefixes):
- `MATCHED` = "Matched" — zero variance
- `TOLERANCE` = "Within Tolerance" — |Net_Variance| <= tolerance_amount (default 1.0 SAR)
- `VARIANCE` = "Variance" — exceeds tolerance
- `UNMATCHED_MANUAL` = "Only in Manual" — COA exists only in manual journal
- `UNMATCHED_DAFTRA` = "Only in Daftra" — COA exists only in Daftra export

## Reconciliation Logic

1. Aggregate Manual data by `COA Daftra` → SUM(Debit, Credit, Net)
2. Aggregate Daftra data by `Account Code` → SUM(Debit, Credit, Net)
3. Outer join on COA code (both sides converted to numeric first)
4. Calculate variances: Debit_Variance, Credit_Variance, Net_Variance = Manual - Daftra
5. Assign status based on tolerance (default: 1.0 SAR absolute threshold)

## Data Schema

**Manual Journal columns (required):** `Tanggal` (date), `COA Daftra` (numeric COA), `Debit-SAR`, `Kredit-SAR`, `Nilai Mutasi`

**Daftra Export columns (required):** `Date`, `Account Code` (numeric COA), `Debit`, `Credit`, `Nilai Mutasi`

**COA Reconciliation output columns:** `COA`, `Account_Name`, `Manual_Debit/Credit/Net`, `Manual_TxnCount`, `Daftra_Debit/Credit/Net`, `Daftra_TxnCount`, `Debit_Variance`, `Credit_Variance`, `Net_Variance`, `Abs_Variance`, `Status`

Column name mappings are defined in `ReconciliationConfig` defaults. COA codes are auto-converted to numeric via `pd.to_numeric()` for join matching.

## Deployment

- **Port:** 8501 (Streamlit default)
- **Health check:** `/_stcore/health`
- **Railway:** Uses Dockerfile with dynamic `$PORT` (see `railway.toml`)
- **Docker:** Python 3.11-slim base, non-root user `aurix:aurix` (UID 1000)

## AI Features (Groq Integration)

The `AIAnalyzer` class is **optional** — the UI gracefully degrades to 4 tabs instead of 5 when Groq is unavailable. Model: `llama-3.3-70b-versatile`, temperature 0.3.

- `generate_insights(summary, coa_recon)` — 3-5 bullet-point analysis
- `detect_anomalies(coa_recon, summary)` — Hybrid: rule-based detection (>3 std dev, >SAR 10K unmatched, debit/credit mismatches) + AI enrichment. Returns top 10 sorted by severity (HIGH/MEDIUM/LOW).
- `chat(question, summary, coa_recon)` — Q&A in Bahasa Indonesia with reconciliation context

## Brand Colors

```python
primary = "#1B5E20"    # Islamic Green
secondary = "#FFD700"  # Gold
accent = "#0D47A1"     # Deep Blue
success = "#2E7D32"    # Green
warning = "#F57C00"    # Orange
danger = "#C62828"     # Red
```
