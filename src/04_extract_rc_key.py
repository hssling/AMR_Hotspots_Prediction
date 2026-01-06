
import pdfplumber

def extract_rc_key():
    pdf_path = 'data/raw/ICMR reports/AMRSN_Annual_Report_2022.pdf'
    # Page 221 in Scan results (1-indexed) = Index 220
    # Also Page 86 = Index 85
    
    target_pages = [85, 220, 221]
    
    print("Extracting potential RC Keys...")
    with pdfplumber.open(pdf_path) as pdf:
        for i in target_pages:
            try:
                page = pdf.pages[i]
                text = page.extract_text()
                print(f"\n--- PAGE {i+1} ---")
                print(text)
            except:
                print(f"Error on Page {i+1}")

if __name__ == "__main__":
    extract_rc_key()
