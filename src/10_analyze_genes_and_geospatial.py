
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import re
import os

def analyze_molecular_geospatial():
    print("Analyzing Molecular & Geospatial Risk (Dataset 2)...")
    
    # 1. Load Data
    # Dataset 2 has 'Organism', 'Resistance Mechanism/Gene Detected', 'Total Culture Positive Isolates', 'Source'
    # We need location info. Dataset 1 had 'Region/State'. Dataset 2 refers to "ICMR Participating Centers".
    # We might need to map Source ID or check if location is implicit.
    # Looking at the filename "Antimicrobial Resistance Patterns and Isolate Distribution in ICMR Participating Centers.xlsx"
    # The columns: Organism, Specimen, Clinic, Gene, Abx Susc, Total Isolates, Report Year, Source.
    
    # Challenge: Dataset 2 might not have explicit Lat/Lon.
    # Strategy: Use 'dataset_1_epidemiology.csv' for Region mapping if possible or just analyze gene prevalence by organism/year derived from Source.
    # Actually, let's look at dataset 1 again. It has 'Region/State'.
    # Does Dataset 2 have location? Let's check the first few rows again or assume national aggregation if not specific.
    
    # Load Dataset 2
    df2 = pd.read_csv('data/raw/dataset_2_molecular.csv')
    
    # 2. Gene Analysis
    # Column: 'Resistance Mechanism/Gene Detected' (e.g., "blaOXA-23 (Predominant), blaNDM")
    
    # Extract Genes
    target_genes = ['NDM', 'OXA-23', 'OXA-48', 'KPC', 'VIM', 'IMP', 'mecA', 'vanA']
    
    gene_counts = {g: 0 for g in target_genes}
    
    for _, row in df2.iterrows():
        val = str(row['Resistance Mechanism/Gene Detected']).upper()
        count = row['Total Culture Positive Isolates'] # Weight by isolates if available
        # If count is NaN or string, treat as 1 occurrence entry
        try:
            weight = float(count) if pd.notnull(count) else 1.0
        except:
            weight = 1.0
            
        for gene in target_genes:
            if gene in val:
                gene_counts[gene] += weight

    # Plot Gene Prevalence
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(gene_counts.keys()), y=list(gene_counts.values()), palette='viridis')
    plt.title('Prevalence of Key Resistance Genes (Weighted by Isolates)')
    plt.ylabel('Estimated Isolate Count')
    plt.savefig('outputs/figures/mol_gene_prevalence.png')
    print("Saved outputs/figures/mol_gene_prevalence.png")
    
    # 3. Geospatial Risk Map (using Dataset 1 for Location)
    # Dataset 1 has 'Region/State'. We can map Region -> Lat/Lon (Approx Centroid).
    df1 = pd.read_csv('data/raw/dataset_1_epidemiology.csv')
    
    # Standardize Regions
    # Map: 'North' -> (28, 77), 'South' -> (12, 79), 'West' -> (19, 72), 'National' -> Filter out or Show as India avg.
    region_coords = {
        'North': (28.6, 77.2), # Delhi approx
        'North India': (30.7, 76.7), # Chandigarh
        'South': (12.9, 80.2), # Chennai
        'South India': (12.9, 79.1), # Vellore
        'West': (19.0, 72.8), # Mumbai
        'West India': (18.5, 73.8), # Pune
        'Karnataka': (15.3, 75.7)
    }
    
    # Aggregate Resistance by Region in Dataset 1
    # Function to parse resistance (reuse)
    def parse_res(v):
        import re
        m = re.search(r'(\d+\.?\d*)', str(v))
        if m and ('resistant' in str(v).lower() or ' r ' in str(v).lower()): return float(m.group(1))
        if m and ('susceptible' in str(v).lower() or ' s ' in str(v).lower()): return 100 - float(m.group(1))
        return None

    df1['Res_Pct'] = df1['Resistance/Susceptibility Percentage'].apply(parse_res)
    regional_risk = df1.groupby('Region/State')['Res_Pct'].mean().reset_index()
    
    # Map Coords
    regional_risk['Lat'] = regional_risk['Region/State'].map(lambda x: region_coords.get(x, (None, None))[0])
    regional_risk['Lon'] = regional_risk['Region/State'].map(lambda x: region_coords.get(x, (None, None))[1])
    regional_risk = regional_risk.dropna(subset=['Lat'])
    
    # Plot Map
    try:
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        india = world[world.name == "India"]
    except:
        india = None
        
    plt.figure(figsize=(10, 10))
    if india is not None:
        india.plot(ax=plt.gca(), color='#f0f0f0', edgecolor='gray')
        
    sns.scatterplot(
        data=regional_risk, x='Lon', y='Lat', size='Res_Pct', hue='Res_Pct',
        sizes=(100, 1000), palette='Reds', legend='brief'
    )
    
    for _, row in regional_risk.iterrows():
        plt.text(row['Lon']+0.5, row['Lat'], f"{row['Region/State']}\n{row['Res_Pct']:.1f}%", fontsize=9)
        
    plt.title('Regional AMR Risk Map (Aggregated 2017-2024)')
    plt.savefig('outputs/figures/spatial_risk_map_new.png')
    print("Saved outputs/figures/spatial_risk_map_new.png")

if __name__ == "__main__":
    analyze_molecular_geospatial()
