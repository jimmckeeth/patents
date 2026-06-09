# [Jim McKeeth's Patent Citation Analysis](https://github.com/jimmckeeth/patents/)

I created this utility to fetch, de-duplicate, and analyze forward patent citations for my patents. It queries the public [Google Cloud BigQuery](https://cloud.google.com/bigquery) patent dataset (`patents-public-data.patents.publications`) to find all publications that cite **James** or **Jim McKeeth** as inventor.

If you want to use this to analyize patents by other inventors you are free to do so under the [GNU Affero General Public License](license.md).

## 📊 High-Level Metrics

* **Portfolio Size**: 62 patents across **12 distinct invention families**
* **Citation Rate**: **100% of families** have forward citations
* **Total Citations**: 1,032 citation links from **823 unique citing patents**
* **Top Citing Companies**: Micron Technology, Google, IBM, Apple, VirnetX, Microsoft
* **Top Cited Areas**: Access Control / Device Security (374 citations) and Search Engine Database Optimization (244 citations)

---

## 🔗 Documentation Links

* [**Summary**](SUMMARY.md) of key statistics and notable insights.
* A convenient browsable **[portal](portal.html)** interface with links to patents.
* Comprehensive **[Data Review and Analysis.](ANALYSIS.md)**

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
│   ├── download_pdfs.py         # Helper script to download patent PDFs to my-patents/ or citing-patents/
│   ├── generate_portal.py       # Helper script to compile static HTML portal dashboard
│   ├── prereq                   # Minimal pip installation instructions
│   └── requirements.txt         # Full Python dependencies dump
├── README.md                    # Core project index & quick start (this file)
├── portal.html                  # Interactive, self-contained HTML dashboard portal
├── AGENTS.md                    # Detailed developer configurations & setup
├── ANALYSIS.md                  # Comprehensive CSV data review & integrity report
└── SUMMARY.md                   # Executive portfolio citation statistics
```

---

## ⚡ Quick Start

If you want to pull the latest or just verify the data.

### 1. Prerequisites
Ensure you have a [Google Cloud Project with the BigQuery API enabled](gcp_setup_guide.md), and a Service Account JSON key file with permissions (`BigQuery Data Viewer` and `BigQuery Job User`).

### 2. Install Dependencies
Run the minimal installation command:
```bash
python -m pip install -r scripts/requirements.txt
```

### 3. Configure Credentials
Set your Google Application Credentials environment variable:
* **Linux/macOS (Bash/Zsh)**: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"`
* **Linux/macOS (Fish)**: `set -x GOOGLE_APPLICATION_CREDENTIALS "/path/to/key.json"`
* **Windows (PowerShell)**: `$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\key.json"`

### 4. Run the Citation Query
From the repository root, run:
```bash
python scripts/get_citations.py
```
This script will query BigQuery, update `data/forward_citations.csv` and `data/citing-patents.csv`, and output a citation matching summary directly to your terminal.

### 5. Download Patent PDFs (Optional)
To download the full PDFs of your portfolio patents into the `my-patents/` directory:
```bash
python scripts/download_pdfs.py
```
*Note: To download PDFs for citing patents (warning: ~1GB of data across 800+ files) into `citing-patents/`, you can run: `python scripts/download_pdfs.py --citing`.*

### 6. Generate the Portal Dashboard (Optional)
To generate or refresh the interactive, search/sort/filter HTML dashboard:
```bash
python scripts/generate_portal.py
```
This will compile all your patent and citation datasets into a single self-contained file **`portal.html`** in the root of the project. Simply double-click **`portal.html`** to open the dashboard in your web browser. It features:
* Interactive overview cards.
* Filterable portfolio list with links to open the downloaded PDFs in `my-patents/`.
* Searchable and filterable citation relationships and company-specific breakdowns.



