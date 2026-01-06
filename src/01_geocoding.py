
import pandas as pd
import os

def geocode_centers():
    print("Geocoding Centers...")
    
    # Load raw synthetic data
    try:
        df = pd.read_csv('data/raw/synthetic_icmr_amr_data.csv')
    except FileNotFoundError:
        print("Data not found. Run src/00_generate_synthetic_data.py first.")
        return

    # Hardcoded coordinates (Lat, Lon) for the 14 centers defined in synthetic generator
    # These are approximate locations of the actual hospitals
    coords = {
        'AIIMS, New Delhi': (28.5672, 77.2100),
        'CMC, Vellore': (12.9248, 79.1352),
        'PGIMER, Chandigarh': (30.7634, 76.7797),
        'JIPMER, Puducherry': (11.9547, 79.7963),
        'Apollo Hospital, Chennai': (13.0405, 80.2505),
        'Tata Memorial Hospital, Mumbai': (18.9912, 72.8258),
        'Kaling Institute, Bhubaneswar': (20.3546, 85.8198),
        'Amrita Institute, Kochi': (10.0326, 76.2829),
        'Sams Hospital, Hyderabad': (17.3850, 78.4867), # Approx generic
        'King George Medical Univ, Lucknow': (26.8687, 80.9157),
        'IPGMER, Kolkata': (22.5298, 88.3442),
        'SMS Hospital, Jaipur': (26.9066, 75.8173),
        'RIMS, Ranchi': (23.3644, 85.3400),
        'GMCH, Guwahati': (26.1528, 91.7709)
    }
    
    # Map coordinates
    df['Latitude'] = df['Center_Name'].map(lambda x: coords.get(x, (None, None))[0])
    df['Longitude'] = df['Center_Name'].map(lambda x: coords.get(x, (None, None))[1])
    
    # Verify matches
    missing = df[df['Latitude'].isna()]['Center_Name'].unique()
    if len(missing) > 0:
        print(f"Warning: Missing coordinates for: {missing}")
        
    # Standardize column names for pipeline
    df['resistance_prop'] = df['Resistance_Percentage'] / 100.0
    
    # Save processed
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/amr_data_geocoded.csv'
    df.to_csv(out_path, index=False)
    print(f"Saved geocoded data to {out_path} ({len(df)} records)")
    
    # Save a 'Centers' unique file for map plotting
    centers_df = df[['Center_Name', 'Latitude', 'Longitude']].drop_duplicates()
    centers_df.to_csv('data/processed/hospital_locations.csv', index=False)
    print(f"Saved hospital locations to data/processed/hospital_locations.csv")

if __name__ == "__main__":
    geocode_centers()
