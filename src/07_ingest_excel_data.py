
import pandas as pd
import os

def ingest_excel_files():
    print("Ingesting Excel Data Files...")
    
    # Define File Paths
    file1_path = 'data/raw/Antimicrobial Resistance Trends and Epidemiological Data for Priority Pathogens.xlsx'
    file2_path = 'data/raw/Antimicrobial Resistance Patterns and Isolate Distribution in ICMR Participating Centers.xlsx'
    
    # Ingest Dataset 1 (Epidemiology)
    if os.path.exists(file1_path):
        print(f"Reading: {file1_path}")
        try:
            # Check for header issues by reading sample
            # Usually simple read_excel works if row 1 is header
            df1 = pd.read_excel(file1_path)
            print("Columns:", df1.columns.tolist())
            
            # Save as standard CSV
            out1 = 'data/raw/dataset_1_epidemiology.csv'
            df1.to_csv(out1, index=False)
            print(f"Standardized to {out1}")
        except Exception as e:
            print(f"Error processing {file1_path}: {e}")
    else:
        print(f"Missing: {file1_path}")

    # Ingest Dataset 2 (Isolate Distribution / Molecular)
    if os.path.exists(file2_path):
        print(f"Reading: {file2_path}")
        try:
            df2 = pd.read_excel(file2_path)
            print("Columns:", df2.columns.tolist())
            
            out2 = 'data/raw/dataset_2_molecular.csv'
            df2.to_csv(out2, index=False)
            print(f"Standardized to {out2}")
        except Exception as e:
            print(f"Error processing {file2_path}: {e}")
    else:
        print(f"Missing: {file2_path}")

if __name__ == "__main__":
    ingest_excel_files()
