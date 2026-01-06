
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point
import os

def analyze_spatial_hotspots():
    print("Analyzing Spatial Hotspots (Real 2022 Data)...")
    
    # 1. Load Real Data
    data_path = 'data/processed/amr_data_real.csv'
    if not os.path.exists(data_path):
        print("Real data not found.")
        return
        
    df = pd.read_csv(data_path)
    print(df.head())
    
    # 2. Get India Shapefile
    try:
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        india = world[world.name == "India"]
    except:
        india = None
        print("Warning: Could not load map boundaries.")

    os.makedirs('outputs/figures', exist_ok=True)

    # 3. Define Markers of Interest
    markers = [
        {'Pathogen': 'S. aureus', 'Gene': 'MRSA (Phenotypic)', 'Title': 'MRSA Hotspots (2022)'},
        {'Pathogen': 'K. pneumoniae', 'Gene': 'NDM', 'Title': 'NDM Carbapenemase Hotspots (K. pneumo)'},
        {'Pathogen': 'E. coli', 'Gene': 'NDM', 'Title': 'NDM Carbapenemase Hotspots (E. coli)'},
        {'Pathogen': 'K. pneumoniae', 'Gene': 'OXA48', 'Title': 'OXA-48 Hotspots (K. pneumo)'}
    ]

    for m in markers:
        # Filter for the specific marker
        if m['Gene'] == 'MRSA (Phenotypic)':
             subset = df[(df['Pathogen'] == m['Pathogen']) & (df['Antibiotic_Gene'] == m['Gene'])].copy()
        else:
             # Genotypic match
             subset = df[(df['Pathogen'] == m['Pathogen']) & (df['Antibiotic_Gene'] == m['Gene'])].copy()

        if subset.empty:
            print(f"No data for {m['Title']}")
            continue
            
        plt.figure(figsize=(10, 10))
        
        if india is not None and not india.empty:
            india.plot(ax=plt.gca(), color='#f0f0f0', edgecolor='black')
        
        sns.scatterplot(
            data=subset, 
            x='Longitude', 
            y='Latitude', 
            size='Resistance_Percentage', 
            hue='Resistance_Percentage',
            sizes=(50, 500), 
            palette='RdYlGn_r', 
            alpha=0.7,
            legend='brief'
        )
        
        for i, row in subset.iterrows():
            plt.text(
                row['Longitude']+0.2, 
                row['Latitude']+0.2, 
                f"{str(row['Center_Name']).split(',')[0]}\n{int(row['Resistance_Percentage'])}%", 
                fontsize=8,
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
            )
            
        plt.title(f"{m['Title']} - Spatial Distribution", fontsize=14)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        
        clean_title = m['Title'].replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
        out_file = f"outputs/figures/map_{clean_title}.png"
        plt.savefig(out_file, dpi=300)
        print(f"Saved {out_file}")
        plt.close()

if __name__ == "__main__":
    analyze_spatial_hotspots()
