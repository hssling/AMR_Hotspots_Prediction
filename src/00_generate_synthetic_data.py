
import pandas as pd
import numpy as np
import os

def generate_synthetic_icmr_data():
    print("Generating Synthetic ICMR AMR Data...")
    os.makedirs('data/raw', exist_ok=True)
    
    # Define realistic parameters based on ICMR AMRSN knowledge
    centers = [
        'AIIMS, New Delhi', 'CMC, Vellore', 'PGIMER, Chandigarh', 'JIPMER, Puducherry',
        'Apollo Hospital, Chennai', 'Tata Memorial Hospital, Mumbai', 'Kaling Institute, Bhubaneswar',
        'Amrita Institute, Kochi', 'Sams Hospital, Hyderabad', 'King George Medical Univ, Lucknow',
        'IPGMER, Kolkata', 'SMS Hospital, Jaipur', 'RIMS, Ranchi', 'GMCH, Guwahati'
    ]
    
    pathogens = ['Escherichia coli', 'Klebsiella pneumoniae', 'Staphylococcus aureus', 'Acinetobacter baumannii', 'Pseudomonas aeruginosa']
    
    antibiotics_gneg = ['Imipenem', 'Meropenem', 'Ceftriaxone', 'Ciprofloxacin', 'Amikacin', 'Colistin']
    antibiotics_gpos = ['Penicillin', 'Ciprofloxacin', 'Erythromycin', 'Clindamycin', 'Vancomycin', 'Linezolid']
    
    records = []
    
    np.random.seed(42)
    
    for year in [2022, 2023]:
        for center in centers:
            # Simulate hospital size/type
            n_isolates_base = np.random.randint(500, 3000)
            
            for pathogen in pathogens:
                n_isolates = int(n_isolates_base * np.random.uniform(0.1, 0.4))
                
                # Assign antibiotics based on Gram type
                if pathogen == 'Staphylococcus aureus':
                    abx_list = antibiotics_gpos
                    # MRSA logic: ~40% resistance to Cefoxitin/Penicillin proxies
                    base_res = 0.4
                else: 
                    abx_list = antibiotics_gneg
                    # Carbapenem resistance logic (high in Kleb/Acineto)
                    if pathogen in ['Klebsiella pneumoniae', 'Acinetobacter baumannii']:
                        base_res = 0.5
                    else:
                        base_res = 0.2
                
                for abx in abx_list:
                    # Resistance rate with some spatial noise
                    # North India (Delhi/Lucknow) often higher resistance
                    region_mod = 1.2 if any(x in center for x in ['Delhi', 'Lucknow', 'Chandigarh', 'Jaipur']) else 0.9
                    
                    res_rate = min(0.95, max(0.01, base_res * region_mod * np.random.normal(1, 0.1)))
                    # Specific drug modifiers
                    if abx == 'Colistin': res_rate *= 0.1 # Low colistin resistance
                    if abx == 'Ceftriaxone': res_rate *= 1.5 # High cephalosporin resistance
                    res_rate = min(0.98, res_rate)
                    
                    res_count = int(n_isolates * res_rate)
                    
                    records.append({
                        'Year': year,
                        'Center_Name': center,
                        'Pathogen': pathogen,
                        'Antibiotic': abx,
                        'Total_Isolates': n_isolates,
                        'Resistant_Isolates': res_count,
                        'Resistance_Percentage': round(res_rate * 100, 1)
                    })
                    
    df = pd.DataFrame(records)
    out_path = 'data/raw/synthetic_icmr_amr_data.csv'
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} records at {out_path}")
    
    # Preview
    print("\nTop 5 rows:")
    print(df.head())

if __name__ == "__main__":
    generate_synthetic_icmr_data()
