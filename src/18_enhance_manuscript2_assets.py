
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import os

# Ensure output dir
os.makedirs('outputs/figures_manuscript2', exist_ok=True)

def parse_val(val):
    if pd.isna(val) or 'Not in source' in str(val): return None
    m = re.search(r'(\d+\.?\d*)', str(val))
    if m: return float(m.group(1))
    return None

def enhance_assets():
    print("Enhancing Manuscript 2 Assets...")
    df = pd.read_csv('data/raw/dataset_3_granular.csv')
    
    # Clean Data
    df['Resistance'] = df['Resistance_Percentage'].apply(parse_val)
    df['Mortality'] = df['Mortality_Rate_Percentage'].apply(parse_val)
    
    # Filter valid
    df_clean = df.dropna(subset=['Resistance', 'Mortality'])
    
    # Figure 1: Distribution of Key Variables (Boxplots)
    # This shows the "Heterogeneity" mentioned in the text
    plt.figure(figsize=(10, 6))
    
    # Melt for seaborn
    plot_data = pd.melt(df_clean[['Resistance', 'Mortality']], 
                        var_name='Metric', value_name='Percentage')
    
    sns.boxplot(x='Metric', y='Percentage', data=plot_data, palette="Set2")
    sns.swarmplot(x='Metric', y='Percentage', data=plot_data, color=".25")
    
    plt.title('Figure 1: Heterogeneity in Resistance and Mortality Rates across Centers')
    plt.ylabel('Percentage (%)')
    plt.xlabel('')
    plt.savefig('outputs/figures_manuscript2/fig1_distribution.png', dpi=300)
    print("Generated: outputs/figures_manuscript2/fig1_distribution.png")

    # Figure 2: Enhanced Scatter with Confidence Interval
    plt.figure(figsize=(8, 6))
    sns.regplot(x='Resistance', y='Mortality', data=df_clean, 
                scatter_kws={'s': 100, 'alpha': 0.7}, line_kws={'color': 'red'})
    
    # Add labels for points?
    # subset for a few labels if possible
    # Not easy without center names mapped perfectly, but dots are fine.
    
    plt.title('Figure 2: The Decoupling Paradox (Resistance vs Mortality)')
    plt.xlabel('Carbapenem Resistance (%)')
    plt.ylabel('All-Cause Mortality (%)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('outputs/figures_manuscript2/fig2_mortality_outcome_enhanced.png', dpi=300)
    print("Generated: outputs/figures_manuscript2/fig2_mortality_outcome_enhanced.png")

if __name__ == "__main__":
    enhance_assets()
