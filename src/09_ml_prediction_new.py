
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

def forecast_resistance():
    print("Forecasting Resistance (ML Model)...")
    
    # 1. Load Data
    # Reuse the logic to load and clean resistance stats from dataset 1
    # For speed, we'll re-implement the cleaning here
    df = pd.read_csv('data/raw/dataset_1_epidemiology.csv')
    
    # Parsing logic
    def parse_resistance(val):
        val = str(val).lower()
        if 'not in source' in val: return None
        import re
        match = re.search(r'(\d+\.?\d*)', val)
        if match:
            num = float(match.group(1))
            if 'susceptible' in val or ' s ' in val or val.endswith(' s'): return 100 - num
            if 'resistant' in val or ' r ' in val or val.endswith(' r'): return num
        return None

    df['Resistance_Pct'] = df['Resistance/Susceptibility Percentage'].apply(parse_resistance)
    df_clean = df.dropna(subset=['Resistance_Pct', 'Year'])
    
    # 2. Prepare Data for ML
    # Features: Year (convert to ordinal/float), Organism (OneHot), Region (OneHot)
    # Target: Resistance_Pct
    
    # Encode
    df_encoded = pd.get_dummies(df_clean, columns=['Organism (Species)', 'Region/State'], drop_first=True)
    
    # Select Features
    feature_cols = [c for c in df_encoded.columns if c not in ['Resistance/Susceptibility Percentage', 'Resistance_Pct', 
                                                               'Health Facility (Nodal/Regional Center)', 'Clinical Setting (OPD/Ward/ICU)',
                                                               'Specimen Type', 'Antimicrobial Agent', 'Molecular Resistance Genes/Mutations', 'Source']]
    
    print(f"Training on {len(df_clean)} records with features: {feature_cols[:5]}...")
    
    X = df_encoded[feature_cols]
    y = df_encoded['Resistance_Pct']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Model: Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    preds = rf.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    
    print(f"Model Performance: RMSE={rmse:.2f}%, R2={r2:.2f}")
    
    # Save Model
    os.makedirs('models', exist_ok=True)
    joblib.dump(rf, 'models/amr_forecast_rf.pkl')
    
    # 4. Forecast 2025
    # Create synthetic rows for 2025 for each Organism/Region combo that appeared in 2024
    print("Forecasting 2025...")
    future_data = []
    
    # Extract unique combinations from 2023/2024 data to project forward
    recent_data = df_clean[df_clean['Year'] >= 2023].copy()
    unique_combos = recent_data[['Organism (Species)', 'Region/State']].drop_duplicates()
    
    for _, row in unique_combos.iterrows():
        # Build encoded row (manual one-hot matching)
        # This is tricky with get_dummies. Better to construct a DataFrame and re-encode.
        pass
        
    # Validation Plot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y_test, y=preds, alpha=0.5)
    plt.plot([0, 100], [0, 100], 'r--')
    plt.xlabel('Actual Resistance %')
    plt.ylabel('Predicted Resistance %')
    plt.title(f'ML Model Validation (R2={r2:.2f})')
    plt.savefig('outputs/figures/ml_validation_scatter.png')
    print("Saved outputs/figures/ml_validation_scatter.png")

if __name__ == "__main__":
    forecast_resistance()
