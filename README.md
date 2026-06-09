# Patent Citation Analysis Tool

This project provides a Python-based utility to fetch, de-duplicate, and analyze forward patent citations for patents authored by **James (Jim) McKeeth**. It queries the public Google Cloud BigQuery patent dataset (`patents-public-data.patents.publications`) to find all publications that cite Jim McKeeth's patent portfolio.

---

## 📁 Repository Structure

The project is structured into dedicated folders for scripts and data files:

```text
├── data/
│   ├── citing-patents.csv       # Unique citing patents (deduplicated)
│   ├── forward_citations.csv    # Citation pairs with category mappings
│   ├── forward_citations.ods    # OpenDocument spreadsheet version of citations
│   └── my-patents.csv           # James McKeeth's primary patent portfolio
├── scripts/
│   ├── get_citations.py         # Main execution script (BigQuery client & processor)
│   ├── prereq                   # Minimal pip installation instructions
│   └── requirements.txt         # Full Python dependencies dump
├── README.md                    # Core project index & quick start (this file)
├── AGENTS.md                    # Detailed developer configurations & setup
├── ANALYSIS.md                  # Comprehensive CSV data review & integrity report
└── SUMMARY.md                   # Executive portfolio citation statistics
```

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have a Google Cloud Project with the BigQuery API enabled, and a Service Account JSON key file with permissions (`BigQuery Data Viewer` and `BigQuery Job User`).

### 2. Install Dependencies
Run the minimal installation command:
```bash
python3 -m pip install -r scripts/requirements.txt
```

### 3. Configure Credentials
Set your Google Application Credentials environment variable:
* **Linux/macOS (Bash/Zsh)**: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"`
* **Linux/macOS (Fish)**: `set -x GOOGLE_APPLICATION_CREDENTIALS "/path/to/key.json"`
* **Windows (PowerShell)**: `$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\key.json"`

### 4. Run the Script
From the repository root, run:
```bash
python scripts/get_citations.py
```
This script will query BigQuery, update `data/forward_citations.csv` and `data/citing-patents.csv`, and output a citation matching summary directly to your terminal.

---

## 📊 High-Level Metrics

* **Portfolio Size**: 62 patents across **12 distinct invention families**
* **Citation Rate**: **100% of families** have forward citations
* **Total Citations**: 1,030 citation links from **821 unique citing patents**
* **Top Citing Companies**: Micron Technology, IBM, Apple, Google, Microsoft, VirnetX
* **Top Cited Areas**: Access Control / Device Security (374 citations) and Search Engine Database Optimization (244 citations)

---

## 🔗 Documentation Links
* **Detailed Setup**: [AGENTS.md](file:///C:/Users/jim/documents/Git/patents/AGENTS.md)
* **Data Review & Anomalies**: [ANALYSIS.md](file:///C:/Users/jim/documents/Git/patents/ANALYSIS.md)
* **Executive Performance Summary**: [SUMMARY.md](file:///C:/Users/jim/documents/Git/patents/SUMMARY.md)
