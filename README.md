# ⚖️ AURIX Reconciliation Module

> **BPKH Limited - Islamic Finance Suite**  
> Automated Daftra-Manual Journal Reconciliation System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-Proprietary-green.svg)]()

---

## 📋 Executive Summary

AURIX Reconciliation Module adalah sistem enterprise-grade untuk melakukan rekonsiliasi otomatis antara **Daftra Accounting System** dan **Manual Journal Entries** di BPKH Limited (Saudi Arabia).

### Key Features

| Feature | Description |
|---------|-------------|
| **Dual-Level Reconciliation** | COA aggregate + transaction detail matching |
| **Configurable Tolerance** | Set acceptable variance threshold (SAR) |
| **Interactive Dashboard** | Real-time visualization dengan Plotly |
| **Audit Trail** | SHA-256 verified logging untuk compliance |
| **Export Capability** | Professional Excel report generation |
| **Arabic Support** | Handle dual-language descriptions |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AURIX RECONCILIATION                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Daftra    │    │   Manual    │    │   Config    │     │
│  │   Export    │    │   Journal   │    │  Settings   │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              DATA CLEANING LAYER                     │   │
│  │  • Column standardization                            │   │
│  │  • Type conversion                                   │   │
│  │  • Null handling                                     │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                               │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           RECONCILIATION ENGINE                      │   │
│  │  ┌───────────────┐  ┌───────────────┐               │   │
│  │  │  COA Level    │  │  Transaction  │               │   │
│  │  │  Aggregate    │  │    Detail     │               │   │
│  │  └───────────────┘  └───────────────┘               │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                               │
│         ┌──────────────────┼──────────────────┐           │
│         ▼                  ▼                  ▼           │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │  Dashboard  │   │   Reports   │   │ Audit Trail │     │
│  │  (Plotly)   │   │   (Excel)   │   │  (SHA-256)  │     │
│  └─────────────┘   └─────────────┘   └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Requirements

### System Requirements
- Python 3.10+
- 2GB RAM minimum
- Modern web browser

### Dependencies
```
streamlit>=1.32.0
pandas>=2.2.0
numpy>=1.26.0
openpyxl>=3.1.2
plotly>=5.18.0
```

---

## 🚀 Installation & Deployment

### Option 1: Local Development

```bash
# Clone repository
git clone https://github.com/mshadianto/aurix-reconciliation.git
cd aurix-reconciliation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Option 2: Railway Deployment

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 3: Docker

```bash
# Build image
docker build -t aurix-reconciliation .

# Run container
docker run -p 8501:8501 aurix-reconciliation
```

---

## 📊 Data Schema

### Input: Jurnal Manual (Sheet 1)

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `Tanggal` | datetime | ✅ | Transaction date |
| `COA Daftra` | float | ✅ | Account code for matching |
| `COA Daftra Name` | string | ❌ | Account name |
| `Debit-SAR` | float | ✅ | Debit amount in SAR |
| `Kredit-SAR` | float | ✅ | Credit amount in SAR |
| `Nilai Mutasi` | float | ✅ | Net mutation |
| `Uraian` | string | ❌ | Transaction description |
| `Rekening` | string | ❌ | Source type (AlRajhi, Riyad Bank, etc.) |

### Input: Daftra Export (Sheet 2)

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `Date` | datetime | ✅ | Transaction date |
| `Account Code` | float | ✅ | COA code for matching |
| `Account` | string | ❌ | Account name |
| `Debit` | float | ✅ | Debit amount in SAR |
| `Credit` | float | ✅ | Credit amount in SAR |
| `Nilai Mutasi` | float | ✅ | Net mutation |
| `Source` | string | ❌ | Journal type |

---

## ⚙️ Reconciliation Logic

### Matching Algorithm

```python
# COA-Level Matching
1. Aggregate Manual by COA Daftra → SUM(Debit), SUM(Credit), SUM(Net)
2. Aggregate Daftra by Account Code → SUM(Debit), SUM(Credit), SUM(Net)
3. OUTER JOIN on COA code
4. Calculate variances:
   - Debit_Variance = Manual_Debit - Daftra_Debit
   - Credit_Variance = Manual_Credit - Daftra_Credit
   - Net_Variance = Manual_Net - Daftra_Net
5. Determine status based on tolerance

# Status Classification
- MATCHED: Net_Variance == 0
- TOLERANCE: |Net_Variance| <= tolerance_amount
- VARIANCE: |Net_Variance| > tolerance_amount
- UNMATCHED_MANUAL: COA exists only in Manual
- UNMATCHED_DAFTRA: COA exists only in Daftra
```

### Tolerance Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tolerance_amount` | 1.0 SAR | Absolute variance threshold |
| `tolerance_percentage` | 0.1% | Percentage-based threshold (future) |

---

## 📈 Output Reports

### 1. Executive Summary
- Total COA accounts
- Match rate percentage
- Total variance amounts
- Health indicator

### 2. COA Reconciliation
- Full breakdown by account code
- Debit/Credit/Net for both sources
- Variance calculations
- Status flags

### 3. Transaction Detail
- Line-by-line transactions
- Drill-down by selected COA
- Source identification

### 4. Audit Trail
- Timestamped actions
- SHA-256 checksums
- Full traceability

---

## 🔐 Security & Compliance

### Data Handling
- ✅ No data persistence (session-based)
- ✅ Client-side processing
- ✅ No external API calls
- ✅ Audit trail with checksums

### Compliance Standards
- PSAK 109 (Zakat Accounting)
- AAOIFI Standards
- OJK Regulations
- BPKH Internal Audit Standards

---

## 🐛 Edge Cases & Risks

| Risk | Mitigation |
|------|------------|
| COA code mismatch (int vs float) | Automatic type conversion |
| Missing date values | Row exclusion with logging |
| Arabic character encoding | UTF-8 handling throughout |
| Large file processing | Chunked processing for >100K rows |
| Circular references | N/A (no formula dependencies) |
| Currency precision | 2 decimal places enforcement |

---

## 🔮 Future Enhancements (Agentic RAG)

### Phase 2: AI-Powered Analysis
```
1. LangChain integration for natural language queries
2. Anomaly detection using ML models
3. Predictive variance forecasting
4. Automated root cause analysis
```

### Phase 3: Multi-Agent Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    AURIX MULTI-AGENT                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Recon     │  │   Fraud     │  │   Report    │     │
│  │   Agent     │  │  Detection  │  │  Generator  │     │
│  │             │  │   Agent     │  │   Agent     │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          ▼                              │
│              ┌───────────────────────┐                 │
│              │   Orchestrator Agent  │                 │
│              │   (LangGraph/CrewAI)  │                 │
│              └───────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📞 Support

**Developer:** MS Hadianto | Audit Committee @BPKH  
**Contact:** sopian@bpkh.go.id   
**GitHub:** [@mshadianto](https://github.com/mshadianto)

---

<div align="center">
  <sub>Built with ❤️ for BPKH Limited Islamic Finance Suite</sub>
</div>
