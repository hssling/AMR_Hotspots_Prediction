
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import learning_curve
from sklearn.ensemble import RandomForestRegressor
import re
import os

# Ensure output dir
os.makedirs('outputs/figures', exist_ok=True)

def parse_res(val):
    if pd.isna(val): return None
    m = re.search(r'(\d+\.?\d*)', str(val))
    if m: 
        val_float = float(m.group(1))
        # Logic for "Susceptible" vs "Resistant"
        # If text says "Susceptible" and value is 90%, Resistance might be 10%. 
        # But for this dataset, we assume columns are "Resistance %" unless specified.
        # Quick standardization for the supplementary plots
        return val_float
    return None

def generate_supp_figures():
    print("Generating Supplementary Figures...")
    df = pd.read_csv('data/raw/dataset_3_granular.csv')
    df['Resistance'] = df['Resistance_Percentage'].apply(parse_res)
    df = df.dropna(subset=['Resistance', 'Year'])
    
    # 1. Learning Curve
    # Prepare X, y
    df_encoded = pd.get_dummies(df[['Year', 'Pathogen']], columns=['Pathogen'], drop_first=True)
    X = df_encoded
    y = df['Resistance']
    
    train_sizes, train_scores, test_scores = learning_curve(
        RandomForestRegressor(n_estimators=100, random_state=42), 
        X, y, cv=5, scoring='neg_mean_squared_error', 
        train_sizes=np.linspace(0.1, 1.0, 5)
    )
    
    train_scores_mean = -np.mean(train_scores, axis=1)
    test_scores_mean = -np.mean(test_scores, axis=1)
    
    plt.figure(figsize=(8, 6))
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training error")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation error")
    plt.xlabel("Training examples")
    plt.ylabel("MSE")
    plt.title("Figure S1: Learning Curve (Random Forest)")
    plt.legend(loc="best")
    plt.grid(True)
    plt.savefig('outputs/figures/supplementary_learning_curve.png')
    print("Generated: outputs/figures/supplementary_learning_curve.png")
    
    # 2. Correlation Matrix
    # Pivot to get Pathogens as columns to see correlations between bugs?
    # Or just feature correlations?
    # Let's do correlation between resistance of different pathogens over years if possible.
    # Group by Year
    
    try:
        pivot_df = df.pivot_table(index='Year', columns='Pathogen', values='Resistance', aggfunc='mean')
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot_df.corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title("Figure S2: Resistance Correlation Matrix")
        plt.savefig('outputs/figures/supplementary_corr_matrix.png')
        print("Generated: outputs/figures/supplementary_corr_matrix.png")
    except Exception as e:
        print(f"Could not generate correlation matrix (maybe not enough overlap): {e}")

if __name__ == "__main__":
    generate_supp_figures()
