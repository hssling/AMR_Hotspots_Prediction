
import pandas as pd
import os

def ingest_dataset_3():
    print("Ingesting Dataset 3 (Granular Data)...")
    
    # URL for Dataset 3
    url3 = "https://docs.google.com/spreadsheets/d/1TZYhYKOA0yyc6MPK2TZfdIsyhcYG9BSjEmZ_ox4QwsQ/export?format=csv&gid=675506298"
    
    try:
        df3 = pd.read_csv(url3)
        print(f"Dataset 3 Loaded: {df3.shape}")
        print(df3.head())
        
        out_path = 'data/raw/dataset_3_granular.csv'
        df3.to_csv(out_path, index=False)
        print(f"Saved to {out_path}")
        
    except Exception as e:
        print(f"Error downloading Dataset 3: {e}")
        # Create a placeholder if it fails so we don't crash, but usually we just want to know
        pass

if __name__ == "__main__":
    ingest_dataset_3()
