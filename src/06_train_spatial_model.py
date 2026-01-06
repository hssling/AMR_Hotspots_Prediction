
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

def train_predictive_model():
    print("Training Spatial Random Forest Model...")
    
    # 1. Load Real Data
    data_path = 'data/processed/amr_data_real.csv'
    if not os.path.exists(data_path):
        print("Data missing.")
        return
        
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records.")
    
    # 2. Feature Engineering
    # Target: Resistance_Percentage
    # Features: Latitude, Longitude, Pathogen (OneHot), Antibiotic_Gene (OneHot)
    
    # Encode Categories
    df_encoded = pd.get_dummies(df, columns=['Pathogen', 'Antibiotic_Gene'], drop_first=False)
    
    # Keep Track of Feature Columns
    feature_cols = [c for c in df_encoded.columns if c not in ['RC_Code', 'Center_Name', 'Resistance_Percentage']]
    
    X = df_encoded[feature_cols]
    y = df_encoded['Resistance_Percentage']
    groups = df_encoded['Center_Name'] # Group by Center for Spatial CV
    
    # 3. Spatial Cross-Validation (LOCO)
    logo = LeaveOneGroupOut()
    scores = []
    
    print(f"Starting LOCO CV on {len(df)} samples...")
    
    y_true_all = []
    y_pred_all = []
    
    for train_idx, test_idx in logo.split(X, y, groups):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # Train
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Predict
        preds = model.predict(X_test)
        
        # Evaluate
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        scores.append(rmse)
        
        y_true_all.extend(y_test)
        y_pred_all.extend(preds)
        
    mean_rmse = np.mean(scores)
    r2 = r2_score(y_true_all, y_pred_all)
    
    print(f"\nModel Performance (Spatial CV):")
    print(f"Mean RMSE: {mean_rmse:.2f}%")
    print(f"Overall R2: {r2:.2f}")
    
    # 4. Final Training on All Data
    final_model = RandomForestRegressor(n_estimators=200, random_state=42)
    final_model.fit(X, y)
    
    # Save Model & Columns
    os.makedirs('models', exist_ok=True)
    joblib.dump(final_model, 'models/amr_spatial_rf.pkl')
    joblib.dump(feature_cols, 'models/model_features.pkl')
    print("Saved Model to models/amr_spatial_rf.pkl")
    
    # 5. Feature Importance Plot
    importances = final_model.feature_importances_
    indices = np.argsort(importances)[-10:]
    
    plt.figure(figsize=(10, 6))
    plt.title('Top 10 Feature Importances for AMR Prediction')
    plt.barh(range(len(indices)), importances[indices], align='center')
    plt.yticks(range(len(indices)), [feature_cols[i] for i in indices])
    plt.tight_layout()
    plt.savefig('outputs/figures/model_feature_importance.png')
    
    # 6. Generate Prediction Grid (Interpolation Map) for NDM
    # We want to predict NDM % for K. pneumo across a lat/long grid
    print("Generating Prediction Grid for NDM (K. pneumo)...")
    
    # Define Grid
    lat_range = np.linspace(8, 37, 50)
    lon_range = np.linspace(68, 97, 50)
    
    grid_preds = []
    
    # Prepare base feature vector
    # We need to match X structure. set Latitude/Longitude. Set Pathogen_K..=1, others=0. Gene_NDM=1, others=0.
    
    base_row = {col: 0 for col in feature_cols}
    # Set One-Hot specifics
    if 'Pathogen_K. pneumoniae' in base_row: base_row['Pathogen_K. pneumoniae'] = 1
    if 'Antibiotic_Gene_NDM' in base_row: base_row['Antibiotic_Gene_NDM'] = 1
    
    for lat in lat_range:
        for lon in lon_range:
            row = base_row.copy()
            row['Latitude'] = lat
            row['Longitude'] = lon
            
            # Predict
            # Need DataFrame with correct order
            row_df = pd.DataFrame([row], columns=feature_cols)
            pred = final_model.predict(row_df)[0]
            
            grid_preds.append({'Latitude': lat, 'Longitude': lon, 'Predicted_Resistance': pred})
            
    grid_df = pd.DataFrame(grid_preds)
    grid_df.to_csv('outputs/ndm_prediction_grid.csv', index=False)
    
    # Plot Heatmap
    plt.figure(figsize=(10, 10))
    pivot = grid_df.pivot(index='Latitude', columns='Longitude', values='Predicted_Resistance')
    # Use extent to map to coords
    sns.heatmap(pivot, cmap='RdYlGn_r', alpha=0.9, cbar_kws={'label': 'Predicted NDM %'})
    plt.title('Predicted NDM-1 Hotspot Risk Map (K. pneumoniae)')
    plt.gca().invert_yaxis() # Latitude up
    plt.savefig('outputs/figures/map_predicted_ndm_risk.png')
    print("Saved Prediction Map to outputs/figures/map_predicted_ndm_risk.png")

if __name__ == "__main__":
    train_predictive_model()
