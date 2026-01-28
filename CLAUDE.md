# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AURIX Reconciliation - Automated financial reconciliation tool for BPKH (Badan Pengelola Keuangan Haji) that matches Daftra accounting system exports against Manual Journal entries. Built for Islamic Finance compliance (PSAK 109, AAOIFI).

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

## Architecture

**Single monolithic Streamlit application** (`app.py`, ~1,600 lines) with four core classes:

- `ReconciliationEngine` - Core reconciliation logic: aggregates data by COA, performs outer join matching, calculates variances
- `ReconciliationVisualizer` - Plotly chart generation (donut, bar, waterfall, heatmap)
- `ReportExporter` - Multi-sheet Excel export with styling
- `AIAnalyzer` - Groq LLM integration for insights, anomaly detection, and chat

**Data flow:**
```
Daftra Export + Manual Journal → Data Cleaning → Reconciliation Engine → Dashboard/Reports
```

**Key dataclasses:** `ReconciliationConfig`, `AuditLogEntry`, `ReconciliationResult`

**Status enum values:** `MATCHED`, `TOLERANCE`, `VARIANCE`, `UNMATCHED_MANUAL`, `UNMATCHED_DAFTRA`

## Reconciliation Logic

1. Aggregate Manual data by `COA Daftra` → SUM(Debit, Credit, Net)
2. Aggregate Daftra data by `Account Code` → SUM(Debit, Credit, Net)
3. Outer join on COA code
4. Calculate variances (Manual - Daftra)
5. Apply status based on tolerance (default: 1.0 SAR)

## Data Schema

**Manual Journal columns:** `Tanggal`, `COA Daftra`, `COA Daftra Name`, `Debit-SAR`, `Kredit-SAR`, `Nilai Mutasi`

**Daftra Export columns:** `Date`, `Account Code`, `Account`, `Debit`, `Credit`, `Nilai Mutasi`

COA codes are auto-converted to numeric via `pd.to_numeric()` for matching.

## Deployment

- **Port:** 8501 (Streamlit default)
- **Health check:** `/_stcore/health`
- **Railway:** Uses Dockerfile with dynamic $PORT
- **Docker user:** `aurix:aurix` (non-root, UID 1000)

## AI Features (Groq Integration)

Requires `GROQ_API_KEY` environment variable. Copy `.env.example` to `.env` and add your key.

**Model:** `llama-3.3-70b-versatile`

**Features:**
- **Auto-Insights** - AI-generated analysis of reconciliation results (3-5 bullet points)
- **Anomaly Detection** - Rule-based + AI detection of unusual patterns (HIGH/MEDIUM/LOW severity)
- **Chat Assistant** - Natural language Q&A about reconciliation data in Bahasa Indonesia

**AIAnalyzer methods:**
- `generate_insights(summary, coa_recon)` - Generate bullet-point insights
- `detect_anomalies(coa_recon, summary)` - Return list of anomaly dicts
- `chat(question, summary, coa_recon)` - Answer user questions

## Brand Colors

```python
primary = "#1B5E20"    # Islamic Green
secondary = "#FFD700"  # Gold
accent = "#0D47A1"     # Deep Blue
```

## Compliance Standards

PSAK 109 (Zakat Accounting), AAOIFI Standards, OJK Regulations, BPKH Internal Audit Standards
