# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AURIX Reconciliation (v2.0.0) — Automated financial reconciliation tool for BPKH (Badan Pengelola Keuangan Haji) that matches Daftra accounting system exports against Manual Journal entries. Built for Islamic Finance compliance (PSAK 109, AAOIFI, OJK Regulations, BPKH Internal Audit Standards).

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

No linter or formatter is configured.

```bash
# Run all tests (117 tests, verbose + short traceback via pytest.ini defaults)
pytest

# Run a single test file
pytest tests/test_engine.py

# Run tests by name pattern
pytest -k "test_coa_level"

# Verbose traceback (overrides pytest.ini --tb=short)
pytest --tb=long
```

Tests use pytest with fixtures in `tests/conftest.py`. LLM-dependent tests are mocked (no API keys needed). All tests run offline. AI-specific tests are in `tests/ai/`.

**CI:** GitHub Actions (`.github/workflows/ci.yml`) runs pytest on every push and PR to `main` using Python 3.11.

## Architecture

**Modular Streamlit application** — `app.py` is a thin entry point (~130 lines) that wires together the `aurix/` package.

### Package Structure

```
app.py                          # Entry point: setup → sidebar → reconcile → render tabs
aurix/
  config.py                     # ReconciliationConfig, ReconciliationStatus (enum), AuditLogEntry, ReconciliationResult dataclasses
  engine.py                     # ReconciliationEngine: data cleaning, COA-level & transaction-level reconciliation
  exporter.py                   # ReportExporter: multi-sheet Excel export with openpyxl formatting
  visualizer.py                 # ReconciliationVisualizer: Plotly charts (donut, bar, waterfall, heatmap)
  ai/
    __init__.py                 # Feature flags: LANGCHAIN_AVAILABLE, SKLEARN_AVAILABLE (try/except imports)
    base.py                     # LLMProvider: wraps ChatGroq (llama-3.3-70b-versatile, temp 0.3)
    analyzer.py                 # AIAnalyzer: LLM-powered insights, anomaly detection, chat (Bahasa Indonesia)
    ml_anomaly.py               # MLAnomalyDetector: IsolationForest + Z-score anomaly detection
    forecasting.py              # VarianceForecaster: monthly variance trend prediction
    root_cause.py               # RootCauseAnalyzer: LLM-based root cause analysis per COA
    tools.py                    # LangChain @tool functions for CrewAI agents (shared _DATA_STORE)
  agents/
    __init__.py                 # Feature flag: CREWAI_AVAILABLE (try/except import)
    orchestrator.py             # AurixCrew: CrewAI Crew that coordinates all agents
    recon_agent.py              # Reconciliation Analysis Agent (CrewAI Agent)
    fraud_agent.py              # Fraud Detection Agent (CrewAI Agent)
    report_agent.py             # Audit Report Writer Agent (CrewAI Agent)
  ui/
    styles.py                   # Page config, CSS (Apple-inspired), header rendering
    sidebar.py                  # File upload, config controls, data loading
    metrics.py                  # Summary metric cards
    tab_dashboard.py            # Plotly charts (status donut, comparison bar, variance waterfall, heatmap)
    tab_ai_analysis.py          # AI insights, anomaly detection, chat, multi-agent tabs (536 lines, largest UI module)
    tab_coa.py                  # COA reconciliation data table
    tab_transactions.py         # Transaction detail view
    tab_audit.py                # Audit trail log
```

### Data Flow

```
Excel Upload (Manual Journal + Daftra Export)
  → aurix.ui.sidebar: loads sheets, returns DataFrames + ReconciliationConfig
  → aurix.engine.ReconciliationEngine:
      clean_manual_data() / clean_daftra_data() → column standardization, pd.to_numeric COA, date parsing
      reconcile_coa_level() → groupby COA → outer join → variance calc → status assignment
      reconcile_transaction_level() → detail-level combined view
      generate_variance_summary() → summary dict
  → UI tabs: Dashboard (Plotly) + AI Analysis (optional) + COA + Transactions + Audit
  → Export: Excel (ReportExporter) / JSON / CSV
```

### Key Dataclasses (aurix/config.py)

- `ReconciliationConfig` — tolerance thresholds + column name mappings for both data sources
- `AuditLogEntry` — SHA-256 checksummed audit entries
- `ReconciliationResult` — summary/detail DataFrames + status counts

### ReconciliationStatus Enum

Values include emoji prefixes (e.g., `"✅ Matched"`):
- `MATCHED` — zero variance
- `TOLERANCE` — |Net_Variance| <= tolerance_amount (default 1.0 SAR)
- `VARIANCE` — exceeds tolerance
- `UNMATCHED_MANUAL` / `UNMATCHED_DAFTRA` — COA exists in only one source

## Reconciliation Logic

1. Aggregate Manual by `COA Daftra` → SUM(Debit, Credit, Net)
2. Aggregate Daftra by `Account Code` → SUM(Debit, Credit, Net)
3. Outer join on COA code (both converted to numeric via `pd.to_numeric()`)
4. Variances: Debit_Variance, Credit_Variance, Net_Variance = Manual - Daftra
5. Status assigned based on tolerance (default: 1.0 SAR absolute threshold)

## Data Schema

**Manual Journal columns (required):** `Tanggal` (date), `COA Daftra` (numeric COA), `Debit-SAR`, `Kredit-SAR`, `Nilai Mutasi`

**Daftra Export columns (required):** `Date`, `Account Code` (numeric COA), `Debit`, `Credit`, `Nilai Mutasi`

Column name mappings are defined in `ReconciliationConfig` defaults.

## AI/ML Features (Optional)

All AI features gracefully degrade — the app runs without Groq or scikit-learn. The UI shows 4 tabs instead of 5 when AI is unavailable.

- **LLM backend:** Groq (`llama-3.3-70b-versatile`) via LangChain. Requires `GROQ_API_KEY` env var (copy `.env.example` to `.env`).
- **Feature flags:** `LANGCHAIN_AVAILABLE` and `SKLEARN_AVAILABLE` in `aurix/ai/__init__.py` (set via try/except imports).
- **AIAnalyzer** (`aurix/ai/analyzer.py`): insights, anomaly detection (hybrid rule-based + LLM), chat in Bahasa Indonesia.
- **MLAnomalyDetector** (`aurix/ai/ml_anomaly.py`): IsolationForest + Z-score on variance columns.
- **VarianceForecaster** (`aurix/ai/forecasting.py`): monthly variance trend prediction.
- **RootCauseAnalyzer** (`aurix/ai/root_cause.py`): per-COA root cause analysis via LLM.

### Multi-Agent System (Phase 3)

CrewAI-based multi-agent architecture in `aurix/agents/`:
- **AurixCrew** orchestrator coordinates three agents (recon, fraud, report) via sequential CrewAI Process.
- Agents share data through LangChain `@tool` functions in `aurix/ai/tools.py` backed by a module-level `_DATA_STORE` dict.
- All agents communicate findings in Bahasa Indonesia.
- Guarded by `CREWAI_AVAILABLE` feature flag in `aurix/agents/__init__.py`.

## Key Patterns

### Graceful Degradation

All optional features (AI, ML, CrewAI) are guarded by feature flags set via try/except imports in `__init__.py` files. The app always runs — AI tab simply doesn't appear when dependencies are missing. The pattern:
1. Feature flag in `__init__.py` (`LANGCHAIN_AVAILABLE`, `SKLEARN_AVAILABLE`, `CREWAI_AVAILABLE`)
2. Runtime check for env var (`GROQ_API_KEY`)
3. Early return with `st.warning()` in UI if unavailable

### Streamlit Session State

Expensive computations (AI insights, ML anomalies, forecasts, crew reports) are cached in `st.session_state` to survive Streamlit reruns. Chat history also persists there. Pattern: check-then-initialize on first access.

### Audit Logging

`ReconciliationEngine._log_action()` is called at every major step. Each `AuditLogEntry` generates a SHA-256 checksum from `timestamp + action + json.dumps(details) + user` (first 16 hex chars stored).

## Deployment

- **Port:** 8501 (Streamlit default)
- **Health check:** `/_stcore/health`
- **Railway:** Uses Dockerfile with dynamic `$PORT` (see `railway.toml`)
- **Docker:** Python 3.11-slim base, non-root user `aurix:aurix` (UID 1000)
- **Streamlit Cloud:** `.streamlit/config.toml` sets headless mode, disables CORS/XSRF for embedding

## Brand & UI

Brand colors (Islamic Green `#1B5E20`, Gold `#FFD700`, Deep Blue `#0D47A1`) and Apple-inspired CSS are defined in `aurix/ui/styles.py`. The Excel export header uses Islamic Green (`#1B5E20`) via openpyxl `PatternFill`.
