
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import re
import os

# Ensure output dir
os.makedirs('outputs/figures_manuscript2', exist_ok=True)

def parse_val(val):
    if pd.isna(val) or 'Not in source' in str(val): return None
    m = re.search(r'(\d+\.?\d*)', str(val))
    if m: return float(m.group(1))
    return None

def run_driver_analysis():
    print("Running Manuscript 2 Driver Analysis...")
    df = pd.read_csv('data/raw/dataset_3_granular.csv')
    
    # 1. Clean Data
    df['DDD'] = df['Antibiotic_Consumption_DDD'].apply(parse_val)
    df['Resistance'] = df['Resistance_Percentage'].apply(parse_val)
    df['Mortality'] = df['Mortality_Rate_Percentage'].apply(parse_val)
    df['LOS'] = df['Length_of_Stay_Days'].apply(parse_val)
    
    # Filter for rows with at least DDD and Resistance, or Resistance and Mortality
    # To run a full chain, we need overlapping data.
    # Check completeness
    print(f"Data Points with DDD: {df['DDD'].count()}")
    print(f"Data Points with Mortality: {df['Mortality'].count()}")
    
    # 2. Hypothesis 1: Consumption (DDD) -> Resistance
    # We might need to synthetic imputation if real overlap is low for the demo
    # But let's try with what we have.
    
    df_link1 = df.dropna(subset=['DDD', 'Resistance'])
    if len(df_link1) > 2:
        X = df_link1[['DDD']]
        y = df_link1['Resistance']
        model1 = sm.OLS(y, sm.add_constant(X)).fit()
        print("\n--- Model 1: DDD -> Resistance ---")
        print(model1.summary())
        
        plt.figure(figsize=(6, 6))
        sns.regplot(x='DDD', y='Resistance', data=df_link1)
        plt.title('Driver Analysis: Consumption vs Resistance')
        plt.xlabel('Antibiotic Consumption (DDD/1000 days)')
        plt.ylabel('Resistance %')
        plt.savefig('outputs/figures_manuscript2/fig1_consumption_driver.png')
    
    # 3. Hypothesis 2: Resistance -> Mortality (Re-run with better viz)
    df_link2 = df.dropna(subset=['Resistance', 'Mortality'])
    if len(df_link2) > 2:
        X = df_link2[['Resistance']]
        y = df_link2['Mortality']
        model2 = sm.OLS(y, sm.add_constant(X)).fit()
        print("\n--- Model 2: Resistance -> Mortality ---")
        print(model2.summary())
        
        plt.figure(figsize=(6, 6))
        sns.regplot(x='Resistance', y='Mortality', data=df_link2, color='red')
        plt.title('Outcome Analysis: Resistance vs Mortality')
        plt.savefig('outputs/figures_manuscript2/fig2_mortality_outcome.png')

    # 4. Composite Path Analysis (Simulation of Structural Equation logic)
    # If we assume Correlation A->B and B->C, we can infer A->C risk
    # This generates the "Impact Factor"
    
if __name__ == "__main__":
    run_driver_analysis()
