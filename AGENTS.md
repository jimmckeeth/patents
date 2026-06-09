# Project Overview: Patent Citation Analysis

This project is a Python-based tool for retrieving and analyzing forward patent citations for patents authored by **James (Jim) McKeeth**. It utilizes the Google Cloud BigQuery public dataset `patents-public-data.patents.publications` to find patents that cite a specific set of inventor names.

## Main Technologies
- **Python**: Core programming language.
- **Google Cloud BigQuery**: Used for high-performance querying of the public patent database.
- **Pandas**: Used for data manipulation and CSV/ODS export.
- **Google Cloud SDK**: Required for authentication and BigQuery access.

## Setup and Installation

### Prerequisites
- A Google Cloud Project with the BigQuery API enabled.
- A Service Account JSON key with BigQuery Data Viewer and BigQuery Job User permissions.

### Dependency Installation
The project provides a `scripts/prereq` file with the minimal installation command:
```bash
python3 -m pip install google-cloud-bigquery db-dtypes pandas
```
Alternatively, a full environment dump is available in `scripts/requirements.txt`.

### Environment Configuration
The script requires the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to be set:

**Bash/Zsh:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
```

**Fish Shell:**
```fish
set -x GOOGLE_APPLICATION_CREDENTIALS "/path/to/your/key.json"
```

## Usage

### Running the Citation Query
Execute the main script to fetch citations from the root directory:
```bash
python scripts/get_citations.py
```
The script will:
1. Submit a SQL query to BigQuery searching for patents citing inventors matching "McKeeth James" or "McKeeth Jim".
2. Map BigQuery category codes to readable names (e.g., "Examiner", "Applicant").
3. De-duplicate findings.
4. Save the results to `data/forward_citations.csv`.
5. Display a summary of the "Top Citing Companies" in the terminal.

## Key Files
- `scripts/get_citations.py`: The primary execution script containing the BigQuery SQL logic.
- `data/forward_citations.csv`: The primary output containing all found forward citations.
- `data/my-patents.csv`: A local dataset containing metadata for James McKeeth's patents.
- `data/citing-patents.csv`: A dataset of patents known to cite the author's work.
- `scripts/prereq`: A helper file containing the minimal `pip install` command for quick setup.
- `.gitignore`: Configured to ignore Python virtual environments (`venv/`).

## Development Conventions
- **Data Deduplication**: The script enforces 1:1 citation uniqueness before saving.
- **URL Mapping**: Patent numbers are automatically converted into Google Patents URLs for easy reference.
- **Assignee Harmonization**: The query prioritizes harmonized assignee names for better data consistency across corporate entities.
