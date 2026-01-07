import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
from scipy.stats import pearsonr

def clean_percentage(x):
    if pd.isna(x) or str(x).lower().strip() in ['not in source', 'na', 'nan']:
        return None
    # Extract number before % or just number
    match = re.search(r'(\d+\.?\d*)', str(x))
    if match:
        return float(match.group(1))
    return None

def analyze_vast_data(excel_path, output_dir):
    print("Loading Vast Data (Table 1)...")
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, 'Table 1')
    
    print("Cleaning Data...")
    # Clean Columns
    df['Resistance_Clean'] = df['Resistance_Percentage'].apply(clean_percentage)
    df['Consumption_Clean'] = df['Antibiotic_Consumption_DDD'].apply(clean_percentage)
    df['Mortality_Clean'] = df['Mortality_Rate_Percentage'].apply(clean_percentage)
    
    # Filter for valid data
    # We create two subsets because some hospitals might have Res+Cons but not Mortality
    df_res_cons = df.dropna(subset=['Resistance_Clean', 'Consumption_Clean'])
    df_res_mort = df.dropna(subset=['Resistance_Clean', 'Mortality_Clean'])
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Consumption vs Resistance
    if len(df_res_cons) > 2:
        plt.figure(figsize=(8, 6))
        r, p = pearsonr(df_res_cons['Consumption_Clean'], df_res_cons['Resistance_Clean'])
        sns.regplot(data=df_res_cons, x='Consumption_Clean', y='Resistance_Clean', 
                    scatter_kws={'s':100}, line_kws={'color':'red', 'label': f'R={r:.2f}, p={p:.3f}'})
        plt.title('Antibiotic Consumption vs Resistance')
        plt.xlabel('Antibiotic Consumption (DDD)')
        plt.ylabel('Resistance (%)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'consumption_vs_resistance.png'))
        plt.close()
        print(f"Plot 1 Saved (N={len(df_res_cons)})")
    else:
        print("Not enough data for Consumption vs Resistance correlation.")

    # Plot 2: Resistance vs Mortality
    if len(df_res_mort) > 2:
        plt.figure(figsize=(8, 6))
        r2, p2 = pearsonr(df_res_mort['Resistance_Clean'], df_res_mort['Mortality_Clean'])
        sns.regplot(data=df_res_mort, x='Resistance_Clean', y='Mortality_Clean', 
                    scatter_kws={'s':100}, line_kws={'color':'purple', 'label': f'R={r2:.2f}, p={p2:.3f}'})
        plt.title('Resistance vs Mortality')
        plt.xlabel('Resistance (%)')
        plt.ylabel('Mortality Rate (%)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'resistance_vs_mortality.png'))
        plt.close()
        print(f"Plot 2 Saved (N={len(df_res_mort)})")
    else:
        print("Not enough data for Resistance vs Mortality correlation.")
        
    print("Vast Data Analysis Complete.")

if __name__ == "__main__":
    excel_path = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\data\raw\Hospital-Level AMR Resistance, Consumption, and Clinical Burden Metrics.xlsx"
    out_dir = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\outputs\advanced_analytics"
    analyze_vast_data(excel_path, out_dir)
