import os
import re
import pandas as pd

def get_google_patent_url(pat_id):
    # Remove hyphens and spaces for the URL
    clean_id = re.sub(r'[^A-Z0-9]', '', str(pat_id).upper())
    return f"https://patents.google.com/patent/{clean_id}/en"

def main():
    # Paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    my_patents_pdf_dir = os.path.join(project_root, "my-patents")
    
    # Input CSV files
    my_patents_csv = os.path.join(data_dir, "my-patents.csv")
    citing_patents_csv = os.path.join(data_dir, "citing-patents.csv")
    forward_citations_csv = os.path.join(data_dir, "forward_citations.csv")
    
    # Check inputs
    if not all(os.path.exists(f) for f in [my_patents_csv, citing_patents_csv, forward_citations_csv]):
        print("Error: Missing required CSV files in data/ directory. Run get_citations.py first.")
        return

    # Output MD files
    my_patents_md = os.path.join(data_dir, "my_patents.md")
    citing_patents_md = os.path.join(data_dir, "citing_patents.md")
    forward_citations_md = os.path.join(data_dir, "forward_citations.md")

    print("Generating Markdown files...")

    # 1. Generate my_patents.md
    print("  Processing my_patents.md...")
    df_my = pd.read_csv(my_patents_csv).fillna("")
    
    with open(my_patents_md, "w", encoding="utf-8") as f:
        f.write("# James McKeeth Patent Portfolio\n\n")
        f.write(f"This list contains the {len(df_my)} patents authored by James (Jim) McKeeth.\n\n")
        
        f.write("| Document ID | Title | Date Published | Family ID | Pages | CPC Classification | Online Link |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :--- | :---: |\n")
        
        for _, row in df_my.iterrows():
            doc_id = row['Document ID']
            clean_id = re.sub(r'[^A-Z0-9]', '', str(doc_id).upper())
            web_url = get_google_patent_url(doc_id)
            
            # Link to the patent online
            online_link = f"[🌐 Google Patents]({web_url})"
            
            title = row['Title']
            date = row['Date Published']
            family = row['Family ID']
            pages = row['Pages']
            cpc = row['CPCI']
            
            # Shorten CPC to first 3 elements for readability in table if long
            if cpc and len(cpc.split(';')) > 3:
                cpc = "; ".join(cpc.split(';')[:3]) + "..."
            
            f.write(f"| **[{doc_id}]({web_url})** | {title} | {date} | {family} | {pages} | `{cpc or '-'}` | {online_link} |\n")
            
    print(f"  Saved: {my_patents_md}")

    # 2. Generate citing_patents.md
    print("  Processing citing_patents.md...")
    df_citing = pd.read_csv(citing_patents_csv).fillna("")
    
    with open(citing_patents_md, "w", encoding="utf-8") as f:
        f.write("# Citing Patents List\n\n")
        f.write(f"This list contains the {len(df_citing)} unique external/internal patents that reference James McKeeth's portfolio.\n\n")
        
        f.write("| Citing Patent | Title | Assignee / Company | Link |\n")
        f.write("| :--- | :--- | :--- | :---: |\n")
        
        for _, row in df_citing.iterrows():
            pat_id = row['citing_patent']
            title = row['citing_title']
            assignee = row['citing_assignee']
            url = row['citing_url'] or get_google_patent_url(pat_id)
            
            f.write(f"| **{pat_id}** | {title} | {assignee or 'Unknown'} | [Google Patents]({url}) |\n")
            
    print(f"  Saved: {citing_patents_md}")

    # 3. Generate forward_citations.md
    print("  Processing forward_citations.md...")
    df_fw = pd.read_csv(forward_citations_csv).fillna("")
    
    with open(forward_citations_md, "w", encoding="utf-8") as f:
        f.write("# Forward Citations Mapping\n\n")
        f.write(f"This file records the {len(df_fw)} individual citation relationships between citing patents and James McKeeth's patents.\n\n")
        
        f.write("| Citing Patent | Citing Assignee | Cited Patent | Cited Title | Category |\n")
        f.write("| :--- | :--- | :--- | :--- | :---: |\n")
        
        for _, row in df_fw.iterrows():
            citing_id = row['citing_patent']
            citing_url = row['citing_url'] or get_google_patent_url(citing_id)
            assignee = row['citing_assignee']
            
            cited_id = row['cited_patent']
            cited_url = row['cited_url'] or get_google_patent_url(cited_id)
            cited_title = row['cited_title']
            category = row['category_name'] or row['category_code']
            
            citing_link = f"[{citing_id}]({citing_url})"
            cited_link = f"[{cited_id}]({cited_url})"
            
            f.write(f"| **{citing_link}** | {assignee or 'Unknown'} | {cited_link} | {cited_title} | <span class=\"badge\">{category}</span> |\n")
            
    print(f"  Saved: {forward_citations_md}")
    print("\nAll Markdown patent lists successfully generated!")

if __name__ == "__main__":
    main()
