
import pandas as pd
import os

def ingest_sheets():
    print("Ingesting Google Sheets Data...")
    
    # Define Sheet URLs (Export Format)
    # Sheet 1: Epidemiology
    url1 = "https://docs.google.com/spreadsheets/d/1MH09Cv6LVhTCbjvbd7xVw0sKp4HIcZ5cDRDikRXBeBE/export?format=csv&gid=843575140"
    
    # Sheet 2: Molecular/Genomic
    url2 = "https://docs.google.com/spreadsheets/d/1KvWmtcTtdBaYLtsZ8jFHROOaY-7U7Ty_vUvZugY7zqY/export?format=csv&gid=219154987"
    
    os.makedirs('data/raw', exist_ok=True)
    
    # Download Dataset 1
    print(f"Downloading Dataset 1 from {url1}...")
    try:
        df1 = pd.read_csv(url1)
        print(f"Dataset 1 Loaded: {df1.shape}")
        print(df1.head())
        df1.to_csv('data/raw/dataset_1_epidemiology.csv', index=False)
        print("Saved to data/raw/dataset_1_epidemiology.csv")
    except Exception as e:
        print(f"Error downloading Dataset 1: {e}")

    # Download Dataset 2
    print(f"\nDownloading Dataset 2 from {url2}...")
    try:
        df2 = pd.read_csv(url2)
        print(f"Dataset 2 Loaded: {df2.shape}")
        print(df2.head())
        df2.to_csv('data/raw/dataset_2_molecular.csv', index=False)
        print("Saved to data/raw/dataset_2_molecular.csv")
    except Exception as e:
        print(f"Error downloading Dataset 2: {e}")

if __name__ == "__main__":
    ingest_sheets()
