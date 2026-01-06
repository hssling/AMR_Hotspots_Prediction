
import pandas as pd
import os
import re

def process_extracted_data():
    print("Processing Extracted PDF Data...")
    
    # 1. Define RC Mapping (Assumed from Annexure I Order)
    rc_map = {
        'RC1': 'AIIMS New Delhi',
        'RC2': 'CMC Vellore',
        'RC3': 'JIPMER Puducherry',
        'RC4': 'PGIMER Chandigarh',
        'RC5': 'AFMC Pune',
        'RC6': 'AIIMS Bhopal',
        'RC7': 'AIIMS Jodhpur',
        'RC8': 'Apollo Chennai',
        'RC9': 'Assam Medical College',
        'RC10': 'IPGMER Kolkata',
        'RC11': 'JPN Apex Trauma Center',
        'RC12': 'KGMU Lucknow',
        'RC13': 'KMC Manipal',
        'RC14': 'LTMMC Mumbai',
        'RC15': 'MGIMS Wardha',
        'RC16': 'NIMS Hyderabad',
        'RC17': 'PD Hinduja Mumbai',
        'RC18': 'RIMS Imphal',
        'RC19': 'Sir Ganga Ram Delhi',
        'RC20': 'Tata Medical Center',
        'RC21': 'SKIMS Srinagar'
    }
    
    # 2. Define Geocodes (Approximate)
    geocodes = {
        'AIIMS New Delhi': (28.5672, 77.2100),
        'CMC Vellore': (12.9248, 79.1352),
        'JIPMER Puducherry': (11.9546, 79.8000),
        'PGIMER Chandigarh': (30.7628, 76.7774),
        'AFMC Pune': (18.5020, 73.8800),
        'AIIMS Bhopal': (23.2599, 77.4126),
        'AIIMS Jodhpur': (26.2389, 73.0243),
        'Apollo Chennai': (13.0645, 80.2565),
        'Assam Medical College': (27.4728, 94.9120), # Dibrugarh
        'IPGMER Kolkata': (22.5354, 88.3424),
        'JPN Apex Trauma Center': (28.5680, 77.2000), # Delhi
        'KGMU Lucknow': (26.8679, 80.9174),
        'KMC Manipal': (13.3530, 74.7850),
        'LTMMC Mumbai': (19.0305, 72.8590),
        'MGIMS Wardha': (20.7280, 78.5800), # Sevagram
        'NIMS Hyderabad': (17.4116, 78.4550), # Punjagutta
        'PD Hinduja Mumbai': (19.0330, 72.8390),
        'RIMS Imphal': (24.8170, 93.9360),
        'Sir Ganga Ram Delhi': (28.6380, 77.1940),
        'Tata Medical Center': (22.5690, 88.4720), # Kolkata New Town
        'SKIMS Srinagar': (34.1370, 74.8090)
    }

    combined_data = []

    # 3. Process MRSA (Phenotypic) - Page 149
    # File: outputs/table_p149_0.csv (RC1-12) and table_p150_0.csv (RC13+)
    # Format: RC/Antibiotics, Cefoxitin(n), Oxacillin, ...
    # We want RC column and "Cefoxitin" (MRSA indicator) or "Oxacillin".
    # The header is messy (split across lines). 
    # Usually Col 0 is RC. Col 1 is Cefoxitin or Oxacillin.
    # Note: Text dump showed Cefoxitin is Col 1.
    
    print("Processing MRSA Tables...")
    for f in ['outputs/table_p149_0.csv', 'outputs/table_p150_0.csv']:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f, header=None)
                # Find start of data (RC1, RC13)
                start_idx = -1
                for idx, row in df.iterrows():
                    if str(row[0]).startswith('RC'):
                        start_idx = idx
                        break
                
                if start_idx != -1:
                    data_rows = df.iloc[start_idx:]
                    for _, row in data_rows.iterrows():
                        rc_code = str(row[0]).strip()
                        # Clean RC code (remove extra chars if any)
                        if rc_code in rc_map:
                            center = rc_map[rc_code]
                            # Column 3 is Methicillin/Cefoxitin (based on CSV inspection)
                            val_str = str(row[3]) 
                            
                            # Extract percentage (in brackets)
                            match = re.search(r'\((\d+\.?\d*)\)', val_str)
                            if match:
                                pct = float(match.group(1))
                                combined_data.append({
                                    'RC_Code': rc_code,
                                    'Center_Name': center,
                                    'Pathogen': 'S. aureus',
                                    'Antibiotic_Gene': 'MRSA (Phenotypic)',
                                    'Resistance_Percentage': pct,
                                    'Latitude': geocodes[center][0],
                                    'Longitude': geocodes[center][1]
                                })
            except Exception as e:
                print(f"Error processing {f}: {e}")

    # 4. Process Genotypic (E. coli / Klebsiella) - Page 94/97
    # Files: outputs/table_p94_0.csv (E. coli), outputs/table_p97_0.csv (Klebsiella)
    # Header: RC, CTXM15, OXA48, TEM, NDM ...
    # Rows: RC1 55% 30% ...
    
    gen_files = {
        'E. coli': 'outputs/table_p94_0.csv',
        'K. pneumoniae': 'outputs/table_p97_0.csv'
    }
    
    for pathogen, fname in gen_files.items():
        if os.path.exists(fname):
            print(f"Processing {pathogen} Genotypic Table...")
            try:
                df = pd.read_csv(fname, header=None)
                # Locate header row: "Regional Centers" or "RC1"
                # Actually PDF header might be split.
                # Find row with "RC1" and assume columns match report order.
                # Report Order (from dump): CTXM15 OXA48 TEM NDM SHV OXA1 IMP VIM KPC CTXM1
                genes = ['CTXM15', 'OXA48', 'TEM', 'NDM', 'SHV', 'OXA1', 'IMP', 'VIM', 'KPC', 'CTXM1']
                
                for _, row in df.iterrows():
                    first_cell = str(row[0])
                    if 'RC' in first_cell: # Data Row
                        # Extract RC number
                        rc_match = re.search(r'RC\d+', first_cell)
                        if rc_match:
                            rc_code = rc_match.group(0)
                        else:
                            continue
                            
                        if rc_code in rc_map:
                            center = rc_map[rc_code]
                            
                            # Iterate columns
                            for i, gene in enumerate(genes):
                                col_idx = i + 1 # RC is col 0
                                if col_idx < len(row):
                                    val = str(row[col_idx])
                                    # Extract number (remove %)
                                    val_clean = re.sub(r'[^\d.]', '', val)
                                    if val_clean:
                                        try:
                                            pct = float(val_clean)
                                            # Normalize to 100 max (sometimes OCR error gives >100?)
                                            pct = min(pct, 100.0) 
                                            
                                            combined_data.append({
                                                'RC_Code': rc_code,
                                                'Center_Name': center,
                                                'Pathogen': pathogen,
                                                'Antibiotic_Gene': gene,
                                                'Resistance_Percentage': pct,
                                                'Latitude': geocodes[center][0],
                                                'Longitude': geocodes[center][1]
                                            })
                                        except:
                                            pass
            except Exception as e:
                print(f"Error processing {fname}: {e}")

    # 5. Save Combined
    final_df = pd.DataFrame(combined_data)
    out_path = 'data/processed/amr_data_real.csv'
    final_df.to_csv(out_path, index=False)
    print(f"Saved Processed Real Data to {out_path}")
    print(final_df.head())
    print(f"Total Records: {len(final_df)}")

if __name__ == "__main__":
    process_extracted_data()
