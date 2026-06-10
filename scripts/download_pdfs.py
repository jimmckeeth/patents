import os
import re
import urllib.request
import pandas as pd
import argparse

def normalize_patent_id(pat_id):
    if not isinstance(pat_id, str):
        return pat_id
    # Strip spaces, hyphens, commas
    clean = re.sub(r'[^A-Z0-9]', '', pat_id.upper())
    
    # 1. Match US application publications: US + YYYY (19xx or 20xx) + sequence digits + kind code
    match_app = re.match(r'^US(19\d{2}|20\d{2})([0-9]+)([A-Z][0-9]*)$', clean)
    if match_app:
        year = match_app.group(1)
        seq = match_app.group(2)
        kind = match_app.group(3)
        # Pad sequence number to 7 digits
        padded_seq = seq.zfill(7)
        return f"US-{year}-{padded_seq}-{kind}"
        
    # 2. Match standard US utility patents: US + sequence digits + kind code
    match_pat = re.match(r'^US([0-9]+)([A-Z][0-9]*)$', clean)
    if match_pat:
        seq = match_pat.group(1)
        kind = match_pat.group(2)
        return f"US-{seq}-{kind}"
        
    # 3. Match foreign patents (e.g. AU, CN, EP)
    match_foreign = re.match(r'^([A-Z]{2})([0-9]+)([A-Z][0-9]*)$', clean)
    if match_foreign:
        cc = match_foreign.group(1)
        seq = match_foreign.group(2)
        kind = match_foreign.group(3)
        return f"{cc}-{seq}-{kind}"
        
    return pat_id

def download_patent_pdf(patent_id, output_dir):
    # Normalize ID: first convert to standard hyphenated/padded format
    standard_id = normalize_patent_id(patent_id)
    # Then strip spaces and hyphens for filename and Google Patents search
    normalized_id = standard_id.replace('-', '').replace(' ', '')
    output_path = os.path.join(output_dir, f"{normalized_id}.pdf")
    
    # Check if file already exists
    if os.path.exists(output_path):
        return "exists", output_path
        
    # Stage 1: Try scraping the Google Patents page
    page_url = f"https://patents.google.com/patent/{normalized_id}/en"
    req = urllib.request.Request(
        page_url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    pdf_url = None
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Look for storage.googleapis.com links ending in .pdf
            matches = re.findall(r'href="([^"]+storage\.googleapis\.com[^"]+\.pdf)"', html)
            if matches:
                pdf_url = matches[0]
    except Exception:
        pass
        
    # Stage 2: Fallback to guessing the URL if scraping failed
    if not pdf_url:
        match = re.match(r'^(US\d+)', normalized_id)
        guessed_id = match.group(1) if match else normalized_id
        pdf_url = f"https://patentimages.storage.googleapis.com/pdfs/{guessed_id}.pdf"
        
    # Stage 3: Download the PDF file
    pdf_req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(pdf_req) as response:
            content = response.read()
            if content.startswith(b'%PDF'):
                with open(output_path, 'wb') as f:
                    f.write(content)
                return "success", output_path
            else:
                return "invalid_content", None
    except Exception as e:
        return f"failed: {e}", None

def main():
    parser = argparse.ArgumentParser(description="Download patent PDFs into the my-patents/ or citing-patents/ folder.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--portfolio", action="store_true", help="Download PDFs of the inventor's portfolio patents (default)")
    group.add_argument("--citing", action="store_true", help="Download PDFs of all citing patents (warning: 800+ files, ~1GB data)")
    group.add_argument("--notable", "-notable", action="store_true", help="Download PDFs of only the high-profile citing patents listed in NOTABLE.md")
    args = parser.parse_args()

    # Paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    
    if args.notable:
        # Notable mode
        docs_dir = os.path.join(project_root, "citing-patents")
        notable_md_path = os.path.join(project_root, "notable.md")
        mode_desc = "Notable Citing Patents"
        
        if not os.path.exists(notable_md_path):
            print(f"Error: {notable_md_path} does not exist.")
            return
            
        print(f"Reading notable citing patents from {notable_md_path}...")
        patent_ids = []
        with open(notable_md_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Citing Patent:" in line:
                    match = re.search(r'patents\.google\.com/patent/([A-Z0-9\-]+)', line)
                    if match:
                        patent_ids.append(match.group(1))
    elif args.citing:
        # Citing mode
        docs_dir = os.path.join(project_root, "citing-patents")
        csv_file = os.path.join(data_dir, "citing-patents.csv")
        id_column = "citing_patent"
        mode_desc = "Citing Patents"
        
        if not os.path.exists(csv_file):
            print(f"Error: Required file {csv_file} does not exist. Run get_citations.py first.")
            return
            
        df = pd.read_csv(csv_file)
        patent_ids = df[id_column].dropna().unique().tolist()
    else:
        # Portfolio mode (default if neither --citing nor --notable is passed)
        docs_dir = os.path.join(project_root, "my-patents")
        csv_file = os.path.join(data_dir, "my-patents.csv")
        id_column = "Document ID"
        mode_desc = "Portfolio Patents"
        
        if not os.path.exists(csv_file):
            print(f"Error: Required file {csv_file} does not exist. Run get_citations.py first.")
            return
            
        df = pd.read_csv(csv_file)
        patent_ids = df[id_column].dropna().unique().tolist()

    # Create target folder if it doesn't exist
    os.makedirs(docs_dir, exist_ok=True)
    
    print(f"=== Starting Download of {len(patent_ids)} {mode_desc} ===")
    print(f"Destination folder: {docs_dir}\n")
    
    success_count = 0
    exists_count = 0
    fail_count = 0
    
    for idx, pat_id in enumerate(patent_ids, 1):
        # Clean the ID string if it's '0' (remnant of corrupt row check)
        if str(pat_id).strip() == '0':
            continue
            
        print(f"[{idx}/{len(patent_ids)}] Processing {pat_id}...", end="", flush=True)
        status, path = download_patent_pdf(str(pat_id), docs_dir)
        
        if status == "success":
            print(" Done (Downloaded).")
            success_count += 1
        elif status == "exists":
            print(" Skiped (Already exists).")
            exists_count += 1
        else:
            print(f" Failed ({status}).")
            fail_count += 1
            
    print("\n=== Download Summary ===")
    print(f"Total processed: {len(patent_ids)}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Already existed: {exists_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    main()
