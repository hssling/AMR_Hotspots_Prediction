
import os
import pypdf
import re

def extract_pdf_data():
    print("Scanning ICMR Reports for Center-wise AMR Data...")
    
    subdir = 'data/raw/ICMR reports'
    if not os.path.exists(subdir):
        print(f"Directory not found: {subdir}")
        return

    files = [f for f in os.listdir(subdir) if f.lower().endswith('.pdf')]
    print(f"Found {len(files)} PDF files.")
    
    out_file = 'outputs/icmr_reports_dump.txt'
    
    with open(out_file, 'w', encoding='utf-8') as f:
        for fname in files:
            path = os.path.join(subdir, fname)
            f.write(f"\n{'='*50}\nFILE: {fname}\n{'='*50}\n")
            
            try:
                reader = pypdf.PdfReader(path)
                # Read first 10 pages for metadata/intro
                # And maybe check a middle page for tables?
                pages_to_check = list(range(10)) + [len(reader.pages)//2]
                
                for i in pages_to_check:
                    if i < len(reader.pages):
                        text = reader.pages[i].extract_text()
                        # Look for potential table keywords
                        if "Table" in text or "Resistance" in text or "Escherichia" in text:
                             f.write(f"\n--- PAGE {i+1} ---\n")
                             f.write(text[:2000]) # Limit output size
                             f.write("\n...\n")
            except Exception as e:
                f.write(f"Error extracting {fname}: {e}\n")
                
    print(f"Dumped text samples to {out_file}")

if __name__ == "__main__":
    extract_pdf_data()
