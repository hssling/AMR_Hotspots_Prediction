
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

def advanced_modeling():
    print("Running Advanced Modeling on Granular Dataset 3...")
    
    # 1. Load Data
    df = pd.read_csv('data/raw/dataset_3_granular.csv')
    print(f"Loaded {len(df)} rows.")
    
    # 2. Parsing Functions
    
    def parse_mt(val):
        # Mortality: "35% (fatal...)" or "36.6%"
        if pd.isna(val) or 'Not in source' in str(val): return None
        m = re.search(r'(\d+\.?\d*)', str(val))
        if m: return float(m.group(1))
        return None

    def parse_los(val):
        # LOS: "19 (Median...)"
        if pd.isna(val) or 'Not in source' in str(val): return None
        m = re.search(r'(\d+\.?\d*)', str(val))
        if m: return float(m.group(1))
        return None

    def parse_res(val):
        # Resistance: "37% (Imipenem)" or "20% Amikacin..."
        if pd.isna(val) or 'Not in source' in str(val): return None
        # Prioritize single percent if formatted like "37% (Drug)"
        # If multiple, look for Imipenem/Carbapenem/Meropenem
        val_str = str(val).lower()
        
        # Check for specific carbapenems first
        for drug in ['imipenem', 'meropenem', 'ertapenem', 'carbapenem']:
            if drug in val_str:
                # Find number near this drug? Or is the whole string relating to it?
                # Case: "14% (Imipenem)"
                m = re.search(r'(\d+\.?\d*)%?\s*[\(-]?\s*' + drug, val_str)
                if m: return float(m.group(1))
                # Case: "25% Imipenem" inside a list
                m2 = re.search(r'(\d+\.?\d*)%?\s*' + drug, val_str)
                if m2: return float(m2.group(1))
        
        # If no specific drug found, and it looks like "37% (Imipenem)", take the first number
        m = re.search(r'^(\d+\.?\d*)%', str(val))
        if m: return float(m.group(1))
        
        return None

    df['Mortality_Rate'] = df['Mortality_Rate_Percentage'].apply(parse_mt)
    df['LOS'] = df['Length_of_Stay_Days'].apply(parse_los)
    df['Resistance'] = df['Resistance_Percentage'].apply(parse_res)
    
    # 3. Model 1: Resistance Forecasting (Year, Pathogen -> Resistance)
    print("\n--- Model 1: Resistance Forecasting ---")
    df_res = df.dropna(subset=['Resistance', 'Year'])
    if len(df_res) > 5:
        # Encode Pathogen
        df_encoded = pd.get_dummies(df_res[['Year', 'Pathogen']], columns=['Pathogen'], drop_first=True)
        X = df_encoded
        y = df_res['Resistance']
        
        model_res = RandomForestRegressor(n_estimators=100, random_state=42)
        model_res.fit(X, y) # Train on full data for pilot
        r2 = model_res.score(X, y)
        print(f"Resistance Model R2 (Train): {r2:.2f} (N={len(df_res)})")
        
        # Plot
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='Year', y='Resistance', hue='Pathogen', data=df_res, s=100)
        # Add trend lines
        for p in df_res['Pathogen'].unique():
            sub = df_res[df_res['Pathogen']==p]
            if len(sub) > 1:
                sns.lineplot(x='Year', y='Resistance', data=sub, alpha=0.5, legend=False)
        plt.title('Granular Resistance Trends (2016-2024)')
        plt.ylabel('Resistance % (Carbapenem/Critical)')
        plt.savefig('outputs/figures/granular_resistance_trend.png')
        print("Saved outputs/figures/granular_resistance_trend.png")
    else:
        print("Not enough data for Resistance Model")

    # 4. Model 2: Impact Analysis (Resistance -> Mortality)
    print("\n--- Model 2: Mortality Impact ---")
    df_mort = df.dropna(subset=['Resistance', 'Mortality_Rate'])
    if len(df_mort) > 3:
        corr = df_mort['Resistance'].corr(df_mort['Mortality_Rate'])
        print(f"Correlation (Resistance vs Mortality): {corr:.2f}")
        
        plt.figure(figsize=(8, 6))
        sns.regplot(x='Resistance', y='Mortality_Rate', data=df_mort)
        plt.title(f'Impact of Resistance on Mortality (Corr={corr:.2f})')
        plt.xlabel('Resistance %')
        plt.ylabel('Mortality Rate %')
        plt.savefig('outputs/figures/mortality_impact.png')
        print("Saved outputs/figures/mortality_impact.png")
    else:
        print("Not enough data for Mortality Analysis")

if __name__ == "__main__":
    advanced_modeling()
