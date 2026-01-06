
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
import os

def analyze_real_trends():
    print("Analyzing Real National AMR Trends (2019-2023)...")
    os.makedirs('outputs/figures', exist_ok=True)
    
    # Load Data
    try:
        df = pd.read_csv('data/raw/real_amr_national.csv')
    except:
        print("Real data missing.")
        return

    print("Data Loaded:")
    print(df)
    
    # Reshape for plotting
    df_long = df.melt(id_vars='Year', var_name='Pathogen_Drug', value_name='Resistance_Percentage')
    
    # Plot 1: Trend Lines
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_long, x='Year', y='Resistance_Percentage', hue='Pathogen_Drug', marker='o', linewidth=2.5)
    plt.title('National Antimicrobial Resistance Trends (India, 2019-2023)', fontsize=14)
    plt.ylabel('Resistance (%)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(df['Year'].unique())
    plt.ylim(0, 100)
    plt.legend(title='Pathogen - Antibiotic')
    plt.tight_layout()
    plt.savefig('outputs/figures/real_amr_trends.png', dpi=300)
    print("Saved Trend Plot to outputs/figures/real_amr_trends.png")
    
    # Forecasting 2024-2025 (Simple Linear)
    future_years = np.array([[2024], [2025]])
    predictions = []
    
    print("\n--- Projecting Future Resistance ---")
    for pathogen in df.columns[1:]:
        X = df[['Year']].values
        y = df[pathogen].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        preds = model.predict(future_years)
        slope = model.coef_[0]
        
        print(f"{pathogen}: 2024={preds[0]:.1f}%, 2025={preds[1]:.1f}% (Slope={slope:.2f}/year)")
        
        predictions.append({
            'Pathogen_Drug': pathogen,
            'Slope': slope,
            'Pred_2024': preds[0],
            'Pred_2025': preds[1]
        })
        
    # Save Projections
    pred_df = pd.DataFrame(predictions)
    pred_df.to_csv('outputs/real_amr_projections.csv', index=False)

if __name__ == "__main__":
    analyze_real_trends()
