import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_amr_scorecard(input_file, output_dir):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # 1. Pivot Data: Center x (Pathogen_ABX)
    df['Feature'] = df['Pathogen'] + "_" + df['Antibiotic_Gene']
    df_pivot = df.pivot_table(index=['RC_Code', 'Center_Name'], columns='Feature', values='Resistance_Percentage')
    
    # 2. Impute with Mean (if any missing)
    df_pivot = df_pivot.fillna(df_pivot.mean())
    
    # 3. PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_pivot)
    
    pca = PCA(n_components=2)
    pcs = pca.fit_transform(X_scaled)
    
    # 4. AMR Burden Score (PC1)
    # We assume PC1 correlates with overall resistance. 
    # Check correlation with mean resistance to ensure directionality.
    pc1 = pcs[:, 0]
    mean_resistance = df_pivot.mean(axis=1)
    correlation = np.corrcoef(pc1, mean_resistance)[0, 1]
    
    if correlation < 0:
        pc1 = -pc1 # Flip sign so higher score = higher resistance
        
    # Scale 0-100
    score = (pc1 - pc1.min()) / (pc1.max() - pc1.min()) * 100
    
    results = df_pivot.reset_index()[['RC_Code', 'Center_Name']]
    results['AMR_Burden_Score'] = score
    results['Rank'] = results['AMR_Burden_Score'].rank(ascending=False)
    results = results.sort_values('Rank')
    
    # 5. Save Scorecard
    os.makedirs(output_dir, exist_ok=True)
    results.to_csv(os.path.join(output_dir, 'hospital_amr_scorecard.csv'), index=False)
    print("Scorecard saved.")
    
    # 6. Visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(data=results, x='AMR_Burden_Score', y='Center_Name', palette='viridis')
    plt.title('Hospital AMR Burden Scorecard (PCA-Derived)')
    plt.xlabel('Composite Resistance Score (0-100)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'amr_scorecard_plot.png'))
    print("Plot saved.")
    
    # 7. Print Top 5
    print("\nTop 5 High-Burden Centers:")
    print(results.head())

if __name__ == "__main__":
    base_path = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\data\processed\amr_data_real.csv"
    out_dir = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\outputs\scorecard"
    generate_amr_scorecard(base_path, out_dir)
