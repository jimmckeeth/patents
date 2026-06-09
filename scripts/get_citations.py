import os
import pandas as pd
from google.cloud import bigquery

# Verify the environment variable is set
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
    print("Run this in your Fish shell first: set -x GOOGLE_APPLICATION_CREDENTIALS '/path/to/your/key.json'")
    exit(1)

client = bigquery.Client()

# The SQL query explicitly searches for name variations, extracts  
# patent numbers, and maps them to any forward citations in the database.
query = r"""
WITH my_patents AS (
  SELECT DISTINCT 
    publication_number,
    family_id,
    (SELECT text FROM UNNEST(title_localized) WHERE language = 'en' LIMIT 1) AS title,
    COALESCE(
      NULLIF((SELECT STRING_AGG(a.name, ', ') FROM UNNEST(assignee_harmonized) AS a), ''),
      NULLIF((SELECT STRING_AGG(a, ', ') FROM UNNEST(assignee) AS a), '')
    ) AS assignee
  FROM `patents-public-data.patents.publications`,
  UNNEST(inventor) AS inv
  WHERE LOWER(inv) LIKE '%mckeeth%james%' 
     OR LOWER(inv) LIKE '%mckeeth%jim%'
)
SELECT 
  citer.publication_number AS citing_patent,
  citer.family_id AS citing_family_id,
  (SELECT text FROM UNNEST(citer.title_localized) WHERE language = 'en' LIMIT 1) AS citing_title,
  COALESCE(
    NULLIF((SELECT STRING_AGG(a.name, ', ') FROM UNNEST(citer.assignee_harmonized) AS a), ''),
    NULLIF((SELECT STRING_AGG(a, ', ') FROM UNNEST(citer.assignee) AS a), '')
  ) AS citing_assignee,
  CONCAT('https://patents.google.com/patent/', 
    CASE 
      WHEN REGEXP_CONTAINS(citer.publication_number, r'^US-20\d{8,9}-A[1-9]') 
      THEN CONCAT('US', REGEXP_EXTRACT(citer.publication_number, r'^US-(\d{4})'), LPAD(REGEXP_EXTRACT(citer.publication_number, r'^US-\d{4}(\d+)-'), 7, '0'), REGEXP_EXTRACT(citer.publication_number, r'-([A-Z0-9]+)$'))
      ELSE REPLACE(citer.publication_number, '-', '')
    END
  ) AS citing_url,
  my.publication_number AS cited_patent,
  my.family_id AS cited_family_id,
  my.title AS cited_title,
  my.assignee AS cited_assignee,
  CONCAT('https://patents.google.com/patent/', 
    CASE 
      WHEN REGEXP_CONTAINS(my.publication_number, r'^US-20\d{8,9}-A[1-9]') 
      THEN CONCAT('US', REGEXP_EXTRACT(my.publication_number, r'^US-(\d{4})'), LPAD(REGEXP_EXTRACT(my.publication_number, r'^US-\d{4}(\d+)-'), 7, '0'), REGEXP_EXTRACT(my.publication_number, r'-([A-Z0-9]+)$'))
      ELSE REPLACE(my.publication_number, '-', '')
    END
  ) AS cited_url,
  c.category AS category_code
FROM `patents-public-data.patents.publications` AS citer,
UNNEST(citer.citation) AS c
JOIN my_patents AS my 
  ON c.publication_number = my.publication_number
"""

print("Submitting query to BigQuery (this may take a minute)...")

try:
    query_job = client.query(query)
    df = query_job.to_dataframe()
    
    # Map the BigQuery category codes to readable formats
    category_map = {
        'PRS': 'Patent Register Service',
        'APP': 'Applicant',
        'EXA': 'Examiner',
        'OPP': 'Opposition (3rd Party)',
        '115': 'Article 115 (3rd Party)',
        'ISR': 'Intl Search Report',
        'SEA': 'Search Report',
        'SUP': 'Supplementary Search'
    }
    df['category_name'] = df['category_code'].map(category_map).fillna(df['category_code'])
    
    # De-duplicate to ensure a clean 1:1 list of citations
    df.drop_duplicates(subset=['citing_patent', 'cited_patent'], inplace=True)
    
    # Reorganized paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    
    # Save the primary forward citations file
    filename = os.path.join(data_dir, "forward_citations.csv")
    df.to_csv(filename, index=False)
    print(f"Success! Saved {len(df)} unique citations to {filename}")

    # Automatically generate/update citing-patents.csv to keep it in sync
    citing_filename = os.path.join(data_dir, "citing-patents.csv")
    citing_df = df[['citing_patent', 'citing_title', 'citing_assignee', 'citing_url']].drop_duplicates(subset=['citing_patent'])
    # Remove any corrupt or empty entries if they somehow slipped in
    citing_df = citing_df[citing_df['citing_patent'].astype(str) != '0'].dropna(subset=['citing_patent'])
    citing_df.to_csv(citing_filename, index=False)
    print(f"Success! Generated and synced {len(citing_df)} unique citing patents to {citing_filename}")

    # Compare with local my-patents.csv if it exists
    my_patents_file = os.path.join(data_dir, "my-patents.csv")
    if os.path.exists(my_patents_file):
        print("\n--- Local Portfolio & Citation Statistics ---")
        try:
            my_df = pd.read_csv(my_patents_file)
            # Normalize Document ID formatting (spaces -> hyphens)
            my_df['Document ID'] = my_df['Document ID'].astype(str).str.replace(' ', '-')
            
            # Find cited patents
            cited_in_dataset = df['cited_patent'].unique()
            my_patents_cited = my_df[my_df['Document ID'].isin(cited_in_dataset)]
            
            total_my_patents = len(my_df)
            total_cited_patents = len(my_patents_cited)
            
            print(f"Total patents in portfolio: {total_my_patents}")
            print(f"Patents with direct forward citations: {total_cited_patents} ({total_cited_patents/total_my_patents:.1%})")
            
            # Family level stats
            total_families = my_df['Family ID'].nunique()
            # A family is cited if any of its members are cited, or family ID matches
            cited_families = my_df[my_df['Document ID'].isin(cited_in_dataset)]['Family ID'].nunique()
            print(f"Total patent families represented: {total_families}")
            print(f"Families with forward citations: {cited_families} ({cited_families/total_families:.1%})")
            
        except Exception as e_stats:
            print(f"Could not calculate portfolio statistics: {e_stats}")

except Exception as e:
    print(f"An error occurred during execution: {e}")
    
print("\n--- Top Citing Companies ---")
if 'df' in locals() and 'citing_assignee' in df.columns:
    # Split comma-separated companies into separate rows, drop blanks, and count
    assignees = df['citing_assignee'].dropna().str.split(', ').explode()
    top_assignees = assignees.value_counts().head(10)
    
    if not top_assignees.empty:
        for company, count in top_assignees.items():
            print(f"{count} citations: {company}")
    else:
        print("No corporate assignee data found in the citing patents.")    