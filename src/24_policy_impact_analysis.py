import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import os
import re

def clean_percentage(x):
    if pd.isna(x) or str(x).lower().strip() in ['not in source', 'na', 'nan']:
        return None
    match = re.search(r'(\d+\.?\d*)', str(x))
    if match:
        return float(match.group(1))
    return None

def analyze_policy_impact(excel_path, output_dir):
    print("Loading Data for ITS Analysis...")
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, 'Table 1')
    
    # 1. Cleaning
    df['Resistance_Clean'] = df['Resistance_Percentage'].apply(clean_percentage)
    df_ts = df.dropna(subset=['Year', 'Resistance_Clean']).copy()
    df_ts['Year'] = df_ts['Year'].astype(int)
    
    # 2. Aggregating by Year (Mean Resistance across all centers)
    annual_trend = df_ts.groupby('Year')['Resistance_Clean'].mean().reset_index()
    print("Annual Trends:")
    print(annual_trend)
    
    # 3. ITS Setup
    # Intervention Year = 2019
    intervention_year = 2019
    annual_trend['Time'] = np.arange(len(annual_trend))
    annual_trend['Intervention'] = (annual_trend['Year'] >= intervention_year).astype(int)
    annual_trend['Time_Since_Intervention'] = annual_trend['Time'] - annual_trend[annual_trend['Year'] == intervention_year]['Time'].values[0]
    annual_trend['Time_Since_Intervention'] = annual_trend['Time_Since_Intervention'].apply(lambda x: max(x, 0))
    
    # 4. Model: Resistance ~ Time + Intervention + Time_Since_Intervention
    model = smf.ols(formula='Resistance_Clean ~ Time + Intervention + Time_Since_Intervention', data=annual_trend).fit()
    print(model.summary())
    
    annual_trend['Predicted'] = model.predict(annual_trend)
    
    # 5. Plot
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(10, 6))
    
    # Observed Data
    sns.scatterplot(data=annual_trend, x='Year', y='Resistance_Clean', s=100, color='black', label='Observed Mean Resistance')
    
    # Trend Lines (Pre vs Post)
    pre_data = annual_trend[annual_trend['Year'] < intervention_year]
    post_data = annual_trend[annual_trend['Year'] >= intervention_year]
    
    # We plot the fitted regression lines
    plt.plot(pre_data['Year'], pre_data['Predicted'], color='blue', linewidth=2, label='Pre-2019 Trend')
    plt.plot(post_data['Year'], post_data['Predicted'], color='red', linewidth=2, label='Post-2019 Trend')
    
    # Vertical Red Line
    plt.axvline(x=2019, color='red', linestyle='--', alpha=0.9, label='Red Line Campaign (2019)')
    
    plt.title('Impact of 2019 "Red Line" Campaign on AMR Trends\n(Interrupted Time Series Analysis)')
    plt.xlabel('Year')
    plt.ylabel('Mean Resistance (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    out_path = os.path.join(output_dir, 'red_line_impact_its.png')
    plt.savefig(out_path)
    print(f"Plot saved to: {out_path}")
    
    # 6. Conclusion
    slope_change = model.params.get('Time_Since_Intervention', 0)
    p_val = model.pvalues.get('Time_Since_Intervention', 1.0)
    
    print(f"\nSlope Change Post-Intervention: {slope_change:.3f} (p={p_val:.3f})")
    if slope_change < 0:
        print("Interpretation: The curve is flattening/decreasing after 2019.")
    else:
        print("Interpretation: Resistance continues to rise or stayed same.")

if __name__ == "__main__":
    excel_path = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\data\raw\Hospital-Level AMR Resistance, Consumption, and Clinical Burden Metrics.xlsx"
    out_dir = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\outputs\advanced_analytics"
    analyze_policy_impact(excel_path, out_dir)
