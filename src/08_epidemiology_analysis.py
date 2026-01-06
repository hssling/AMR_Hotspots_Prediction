
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

def analyze_epidemiology():
    print("Analyzing Epidemiology Data (Dataset 1)...")
    
    # 1. Load Data
    df = pd.read_csv('data/raw/dataset_1_epidemiology.csv')
    
    # 2. Parse Resistance/Susceptibility Column
    # Format examples: "35% Susceptible", "91.0% Resistant", "11.1% S (Imipenem)..."
    
    def parse_resistance(val):
        val = str(val).lower()
        if 'not in source' in val:
            return None, None
            
        # Try to find a percentage number
        match = re.search(r'(\d+\.?\d*)', val)
        if match:
            num = float(match.group(1))
            
            # Determine if it represents Susceptibility (S) or Resistance (R)
            is_susceptible = 'susceptible' in val or ' s ' in val or val.endswith(' s') or 'sensitive' in val
            is_resistant = 'resistant' in val or ' r ' in val or val.endswith(' r')
            
            if is_susceptible:
                return 100 - num, 'Calculated (100-S)'
            elif is_resistant:
                return num, 'Direct (R)'
            else:
                # Ambiguous, assume Resistance if high? No, usually text says distinctively.
                # If just a number, check context? 
                # For now return None if ambiguous
                return None, 'Ambiguous'
        return None, 'No Number'

    df[['Resistance_Pct', 'Value_Type']] = df['Resistance/Susceptibility Percentage'].apply(
        lambda x: pd.Series(parse_resistance(x))
    )
    
    # Drop rows where Resistance could not be parsed
    df_clean = df.dropna(subset=['Resistance_Pct'])
    print(f"Parsed {len(df_clean)} valid resistance records out of {len(df)}.")
    
    # 3. Aggregate Trends by Year and Organism
    # We want average resistance per organism per year (across all antibiotics)
    # Or specific antibiotic class? The 'Antimicrobial Agent' column varies.
    # Let's focus on Critical Drugs: Carbapenems (Meropenem, Imipenem) vs Others.
    
    crit_drugs = ['meropenem', 'imipenem', 'carbapenems', 'ertapenem']
    df_clean['Is_Carbapenem'] = df_clean['Antimicrobial Agent'].str.lower().apply(
        lambda x: any(d in str(x) for d in crit_drugs)
    )
    
    # Aggregate: Year, Organism, Is_Carbapenem -> Mean Resistance
    trends = df_clean.groupby(['Year', 'Organism (Species)', 'Is_Carbapenem'])['Resistance_Pct'].mean().reset_index()
    
    # Filter for Top Pathogens
    top_pathogens = ['Escherichia coli', 'Klebsiella pneumoniae', 'Acinetobacter baumannii', 'Pseudomonas aeruginosa', 'Staphylococcus aureus']
    # Approximate matching
    def clean_pathogen(p):
        for tp in top_pathogens:
            if tp in str(p):
                return tp
        return p
        
    trends['Pathogen'] = trends['Organism (Species)'].apply(clean_pathogen)
    trends = trends[trends['Pathogen'].isin(top_pathogens)]
    
    os.makedirs('outputs/figures', exist_ok=True)
    
    # 4. Plot 1: Overall Resistance Trends (All Antibiotics)
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=trends, x='Year', y='Resistance_Pct', hue='Pathogen', marker='o')
    plt.title('Average Antibiotic Resistance Trends (2017-2024)')
    plt.ylabel('Mean Resistance %')
    plt.grid(True, alpha=0.3)
    plt.savefig('outputs/figures/epi_trend_overall.png')
    print("Saved outputs/figures/epi_trend_overall.png")
    
    # 5. Plot 2: Carbapenem Resistance Only (Gram Negatives)
    if not trends[trends['Is_Carbapenem']].empty:
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=trends[trends['Is_Carbapenem']], x='Year', y='Resistance_Pct', hue='Pathogen', marker='s')
        plt.title('CRITICAL: Carbapenem Resistance Trends (2017-2024)')
        plt.ylabel('Carbapenem Resistance %')
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.savefig('outputs/figures/epi_trend_carbapenem.png')
        print("Saved outputs/figures/epi_trend_carbapenem.png")
    
    # 6. Regional Analysis (2023-2024 Snapshot if possible)
    # Check 'Region/State' coverage
    print("Regions available:", df_clean['Region/State'].unique())
    
    # Pivot Heatmap: Pathogen vs Region (Mean Resistance)
    region_stats = df_clean.groupby(['Region/State', 'Organism (Species)'])['Resistance_Pct'].mean().reset_index()
    region_stats['Pathogen'] = region_stats['Organism (Species)'].apply(clean_pathogen)
    
    try:
        pivot = region_stats.pivot_table(index='Pathogen', columns='Region/State', values='Resistance_Pct')
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot, cmap='Reds', annot=True, fmt='.1f')
        plt.title('Resistance Heatmap by Region (Avg 2017-2024)')
        plt.savefig('outputs/figures/epi_heatmap_region.png')
        print("Saved outputs/figures/epi_heatmap_region.png")
    except Exception as e:
        print(f"Could not generate heatmap: {e}")

if __name__ == "__main__":
    analyze_epidemiology()
