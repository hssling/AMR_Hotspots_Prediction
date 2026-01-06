
import pdfplumber
import pandas as pd

def extract_gram_neg_tables():
    pdf_path = 'data/raw/ICMR reports/AMRSN_Annual_Report_2022.pdf'
    # Page 94 (Index 93) -> E. coli?
    # Page 97 (Index 96) -> K. pneumo?
    
    target_pages = [93, 94, 96, 97]
    
    print("Extracting Gram Negative RC Data...")
    
    with pdfplumber.open(pdf_path) as pdf:
        for i in target_pages:
            try:
                page = pdf.pages[i]
                text = page.extract_text()
                print(f"\n--- PAGE {i+1} ---")
                print(text[:300])
                
                tables = page.extract_tables()
                if tables:
                    for idx, table in enumerate(tables):
                        df = pd.DataFrame(table)
                        # Check if it has RC column
                        first_col = df.iloc[:,0].astype(str).values
                        if any("RC" in str(x) for x in first_col):
                            print(f"Found RC Table on Page {i+1} Table {idx}")
                            df.to_csv(f"outputs/table_p{i+1}_{idx}.csv", index=False, header=False)
            except:
                pass

if __name__ == "__main__":
    extract_gram_neg_tables()
