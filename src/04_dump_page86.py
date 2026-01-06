
import pdfplumber

def dump_page_86():
    pdf_path = 'data/raw/ICMR reports/AMRSN_Annual_Report_2022.pdf'
    print("Dumping Page 86 (Index 85)...")
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[85]
        text = page.extract_text()
        print(text)

if __name__ == "__main__":
    dump_page_86()
