
import pdfplumber
import pandas as pd
import re

def extract_center_tables():
    pdf_path = 'data/raw/ICMR reports/AMRSN_Annual_Report_2022.pdf'
    print(f"Extracting Center Data from {pdf_path}...")
    
    # Target Pages (0-indexed based on scan which was 1-indexed? No, scan used i+1 so page 86 is index 85)
    # Scan said: "Page 86" (1-indexed implies index 85)
    
    target_pages = [85, 86, 87, 88, 147, 148, 149] 
    
    with pdfplumber.open(pdf_path) as pdf:
        for i in target_pages:
            print(f"\n--- Processing Page {i+1} ---")
            page = pdf.pages[i]
            
            # Extract Text for Context
            text = page.extract_text()
            print(text[:500])
            
            # Extract Tables
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables.")
                for idx, table in enumerate(tables):
                    # Convert to DataFrame
                    df = pd.DataFrame(table)
                    # Save raw CSV
                    csv_name = f"outputs/table_p{i+1}_{idx}.csv"
                    df.to_csv(csv_name, index=False, header=False)
                    print(f"Saved {csv_name}")
            else:
                print("No tables found on this page.")

if __name__ == "__main__":
    extract_center_tables()
