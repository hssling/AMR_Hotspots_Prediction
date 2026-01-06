
import os
import pypdf

def scan_pdf_for_keywords():
    print("Full Scan of ICMR 2022 Report for Granular Data...")
    
    # Target the main 2022 report
    pdf_path = 'data/raw/ICMR reports/AMRSN_Annual_Report_2022.pdf'
    if not os.path.exists(pdf_path):
        print("Main file not found, checking others...")
        # Fallback logic could go here
        return
        
    print(f"Scanning: {pdf_path}")
    
    keywords = ["Annexure", "Appendix", "Center wise", "Centre wise", "Site wise", "Table 2", "Table 3", "AIIMS", "CMC", "PGI"]
    
    try:
        reader = pypdf.PdfReader(pdf_path)
        num_pages = len(reader.pages)
        print(f"Total Pages: {num_pages}")
        
        matches = []
        
        for i in range(num_pages):
            try:
                text = reader.pages[i].extract_text()
                # Check for "Table" AND ("Center" or "Site")
                # Or just "Annexure"
                
                found = []
                if "Annexure" in text:
                    found.append("Annexure")
                
                if "Table" in text and ("Center" in text or "Site" in text or "Hospital" in text):
                    found.append("Table+Center")
                    
                if found:
                    snippet = text[:200].replace('\n', ' ')
                    matches.append(f"Page {i+1}: Found {found} - '{snippet}...'")
                    
            except:
                pass
                
        # Write matches to file
        with open('outputs/pdf_scan_results.txt', 'w') as f:
            for m in matches:
                f.write(m + "\n")
                
        print(f"Scan Complete. Found {len(matches)} potential pages. See outputs/pdf_scan_results.txt")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_pdf_for_keywords()
