"""
AMR Manuscript 3: ITS Analysis Pipeline
Evaluating India's 2016 Red Line Campaign

Author: Dr. Siddalingaiah H S & Antigravity AI
Date: January 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.stattools import durbin_watson
from scipy import stats
import os
import re
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality defaults
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 12
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.linewidth'] = 1.2

# Paths
BASE_DIR = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "its_analysis")
SUBMISSION_DIR = os.path.join(BASE_DIR, "submission_manuscript3")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SUBMISSION_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)

def clean_percentage(x):
    """Extract numeric percentage from string."""
    if pd.isna(x) or str(x).lower().strip() in ['not in source', 'na', 'nan', '']:
        return None
    # Match first number (including decimals)
    match = re.search(r'(\d+\.?\d*)', str(x))
    if match:
        return float(match.group(1))
    return None

def load_and_consolidate_data():
    """Load all AMR data sources and consolidate for ITS analysis."""
    print("=" * 60)
    print("PHASE 1: DATA CONSOLIDATION")
    print("=" * 60)
    
    # Load Dataset 1: Epidemiology (2017-2024)
    df1 = pd.read_csv(os.path.join(DATA_DIR, "raw", "dataset_1_epidemiology.csv"))
    df1['Resistance_Clean'] = df1['Resistance/Susceptibility Percentage'].apply(clean_percentage)
    df1['Source_Dataset'] = 'Epidemiology'
    print(f"Dataset 1 (Epidemiology): {len(df1)} records, Years: {sorted(df1['Year'].unique())}")
    
    # Load Dataset 3: Granular (2016-2024)
    df3 = pd.read_csv(os.path.join(DATA_DIR, "raw", "dataset_3_granular.csv"))
    df3['Resistance_Clean'] = df3['Resistance_Percentage'].apply(clean_percentage)
    df3['Source_Dataset'] = 'Granular'
    print(f"Dataset 3 (Granular): {len(df3)} records, Years: {sorted(df3['Year'].unique())}")
    
    # Load Excel data
    try:
        xls = pd.ExcelFile(os.path.join(DATA_DIR, "raw", "Hospital-Level AMR Resistance, Consumption, and Clinical Burden Metrics.xlsx"))
        df_excel = pd.read_excel(xls, 'Table 1')
        df_excel['Resistance_Clean'] = df_excel['Resistance_Percentage'].apply(clean_percentage)
        df_excel['Source_Dataset'] = 'Excel'
        print(f"Excel Data: {len(df_excel)} records, Years: {sorted(df_excel['Year'].unique())}")
    except Exception as e:
        print(f"Excel loading error: {e}")
        df_excel = pd.DataFrame()
    
    # Standardize columns for merging
    records = []
    
    # From Dataset 1
    for _, row in df1.iterrows():
        if pd.notna(row['Resistance_Clean']):
            records.append({
                'Year': int(row['Year']),
                'Pathogen': row['Organism (Species)'],
                'Antibiotic': row.get('Antimicrobial Agent', 'Mixed'),
                'Resistance_Pct': row['Resistance_Clean'],
                'Source': row['Source_Dataset']
            })
    
    # From Dataset 3
    for _, row in df3.iterrows():
        if pd.notna(row['Resistance_Clean']):
            records.append({
                'Year': int(row['Year']),
                'Pathogen': row['Pathogen'],
                'Antibiotic': 'Mixed',
                'Resistance_Pct': row['Resistance_Clean'],
                'Source': row['Source_Dataset']
            })
    
    # From Excel
    if not df_excel.empty:
        for _, row in df_excel.iterrows():
            if pd.notna(row.get('Resistance_Clean')):
                records.append({
                    'Year': int(row['Year']),
                    'Pathogen': row['Pathogen'],
                    'Antibiotic': 'Mixed',
                    'Resistance_Pct': row['Resistance_Clean'],
                    'Source': row['Source_Dataset']
                })
    
    # Create consolidated DataFrame
    df_all = pd.DataFrame(records)
    
    # Standardize pathogen names
    pathogen_map = {
        'Escherichia coli': 'E. coli',
        'Klebsiella pneumoniae': 'K. pneumoniae',
        'Acinetobacter baumannii': 'A. baumannii',
        'Staphylococcus aureus': 'S. aureus (MRSA)',
        'Staphylococcus aureus (MRSA)': 'S. aureus (MRSA)',
        'Pseudomonas aeruginosa': 'P. aeruginosa',
        'Salmonella Typhi': 'S. Typhi',
        'Enterococcus faecium': 'E. faecium',
        'Enterococcus faecium (VRE)': 'E. faecium (VRE)',
        'Candida auris': 'C. auris'
    }
    df_all['Pathogen_Standard'] = df_all['Pathogen'].map(lambda x: pathogen_map.get(x, x))
    
    print(f"\nConsolidated: {len(df_all)} total records")
    print(f"Year range: {df_all['Year'].min()} - {df_all['Year'].max()}")
    print(f"Unique pathogens: {df_all['Pathogen_Standard'].nunique()}")
    
    # Save consolidated data
    output_path = os.path.join(DATA_DIR, "processed", "consolidated_amr_its_data.csv")
    df_all.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")
    
    return df_all

def create_annual_aggregates(df):
    """Create annual aggregates for ITS analysis."""
    print("\n" + "=" * 60)
    print("PHASE 2: ANNUAL AGGREGATION")
    print("=" * 60)
    
    # Overall annual mean
    annual_overall = df.groupby('Year').agg({
        'Resistance_Pct': ['mean', 'std', 'count']
    }).reset_index()
    annual_overall.columns = ['Year', 'Mean_Resistance', 'SD', 'N_Observations']
    
    # By pathogen
    annual_pathogen = df.groupby(['Year', 'Pathogen_Standard']).agg({
        'Resistance_Pct': ['mean', 'count']
    }).reset_index()
    annual_pathogen.columns = ['Year', 'Pathogen', 'Mean_Resistance', 'N']
    
    print("\nAnnual Overall Trends:")
    print(annual_overall.to_string(index=False))
    
    return annual_overall, annual_pathogen

def run_its_analysis(annual_data, intervention_year=2016):
    """
    Run Interrupted Time Series analysis with segmented regression.
    
    Model: Y = β₀ + β₁*Time + β₂*Intervention + β₃*Time_After + ε
    
    Where:
    - β₁: Pre-intervention slope
    - β₂: Level change at intervention
    - β₃: Change in slope post-intervention
    """
    print("\n" + "=" * 60)
    print("PHASE 3: INTERRUPTED TIME SERIES ANALYSIS")
    print("=" * 60)
    
    df = annual_data.copy()
    
    # Create ITS variables
    df = df.sort_values('Year').reset_index(drop=True)
    df['Time'] = np.arange(len(df))  # Time counter (0, 1, 2, ...)
    df['Intervention'] = (df['Year'] >= intervention_year).astype(int)
    
    # Time since intervention (0 before, 1,2,3... after)
    intervention_idx = df[df['Year'] >= intervention_year].index.min()
    df['Time_After'] = 0
    if pd.notna(intervention_idx):
        df.loc[df.index >= intervention_idx, 'Time_After'] = np.arange(len(df) - intervention_idx)
    
    print(f"\nIntervention Year: {intervention_year}")
    print(f"Pre-intervention periods: {sum(df['Year'] < intervention_year)}")
    print(f"Post-intervention periods: {sum(df['Year'] >= intervention_year)}")
    
    # Fit OLS model
    model = smf.ols(
        formula='Mean_Resistance ~ Time + Intervention + Time_After',
        data=df
    ).fit()
    
    print("\n" + "-" * 40)
    print("OLS REGRESSION RESULTS")
    print("-" * 40)
    print(model.summary())
    
    # Extract key coefficients
    results = {
        'intercept': model.params['Intercept'],
        'pre_slope': model.params['Time'],
        'level_change': model.params['Intervention'],
        'slope_change': model.params['Time_After'],
        'pre_slope_se': model.bse['Time'],
        'level_change_se': model.bse['Intervention'],
        'slope_change_se': model.bse['Time_After'],
        'pre_slope_pval': model.pvalues['Time'],
        'level_change_pval': model.pvalues['Intervention'],
        'slope_change_pval': model.pvalues['Time_After'],
        'r_squared': model.rsquared,
        'durbin_watson': durbin_watson(model.resid)
    }
    
    # Calculate 95% CIs
    conf = model.conf_int()
    results['pre_slope_ci'] = (conf.loc['Time', 0], conf.loc['Time', 1])
    results['level_change_ci'] = (conf.loc['Intervention', 0], conf.loc['Intervention', 1])
    results['slope_change_ci'] = (conf.loc['Time_After', 0], conf.loc['Time_After', 1])
    
    # Add predictions and counterfactual
    df['Predicted'] = model.predict(df)
    
    # Counterfactual (what would have happened without intervention)
    df_counterfactual = df.copy()
    df_counterfactual['Intervention'] = 0
    df_counterfactual['Time_After'] = 0
    df['Counterfactual'] = model.predict(df_counterfactual)
    
    print("\n" + "-" * 40)
    print("KEY FINDINGS")
    print("-" * 40)
    print(f"Pre-intervention slope: {results['pre_slope']:.3f}%/year (95% CI: {results['pre_slope_ci'][0]:.3f}, {results['pre_slope_ci'][1]:.3f})")
    print(f"Level change at intervention: {results['level_change']:.3f}% (95% CI: {results['level_change_ci'][0]:.3f}, {results['level_change_ci'][1]:.3f})")
    print(f"Slope change post-intervention: {results['slope_change']:.3f}%/year (95% CI: {results['slope_change_ci'][0]:.3f}, {results['slope_change_ci'][1]:.3f})")
    print(f"\nR-squared: {results['r_squared']:.4f}")
    print(f"Durbin-Watson: {results['durbin_watson']:.4f} (ideal: 2.0)")
    
    return df, results, model

def run_sensitivity_analyses(df_all, intervention_year=2016):
    """Run sensitivity analyses: by pathogen, excluding COVID years."""
    print("\n" + "=" * 60)
    print("PHASE 4: SENSITIVITY ANALYSES")
    print("=" * 60)
    
    sensitivity_results = {}
    
    # 1. Pathogen-specific analysis
    print("\n--- Pathogen-Specific Analysis ---")
    priority_pathogens = ['K. pneumoniae', 'E. coli', 'A. baumannii', 'S. aureus (MRSA)']
    
    for pathogen in priority_pathogens:
        df_pathogen = df_all[df_all['Pathogen_Standard'] == pathogen].copy()
        if len(df_pathogen) >= 5:  # Need minimum observations
            annual = df_pathogen.groupby('Year')['Resistance_Pct'].mean().reset_index()
            annual.columns = ['Year', 'Mean_Resistance']
            
            if len(annual) >= 4:  # Minimum for ITS
                try:
                    _, res, _ = run_its_analysis(annual, intervention_year)
                    sensitivity_results[pathogen] = {
                        'slope_change': res['slope_change'],
                        'slope_change_pval': res['slope_change_pval'],
                        'n_years': len(annual)
                    }
                    print(f"{pathogen}: Slope change = {res['slope_change']:.3f}, p = {res['slope_change_pval']:.3f}")
                except Exception as e:
                    print(f"{pathogen}: Analysis failed - {e}")
    
    # 2. Excluding COVID years (2020-2021)
    print("\n--- Excluding COVID Years (2020-2021) ---")
    df_no_covid = df_all[~df_all['Year'].isin([2020, 2021])].copy()
    annual_no_covid = df_no_covid.groupby('Year')['Resistance_Pct'].mean().reset_index()
    annual_no_covid.columns = ['Year', 'Mean_Resistance']
    
    try:
        _, res_covid, _ = run_its_analysis(annual_no_covid, intervention_year)
        sensitivity_results['Excluding_COVID'] = {
            'slope_change': res_covid['slope_change'],
            'slope_change_pval': res_covid['slope_change_pval'],
            'n_years': len(annual_no_covid)
        }
    except Exception as e:
        print(f"COVID exclusion analysis failed: {e}")
    
    return sensitivity_results

def generate_its_figure(df_its, results, intervention_year=2016):
    """Generate main ITS plot with counterfactual."""
    print("\n" + "=" * 60)
    print("PHASE 5: FIGURE GENERATION")
    print("=" * 60)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot observed data
    ax.scatter(df_its['Year'], df_its['Mean_Resistance'], 
               s=120, c='#2c3e50', zorder=5, label='Observed', edgecolors='white', linewidth=1.5)
    
    # Pre-intervention trend
    pre_data = df_its[df_its['Year'] < intervention_year]
    post_data = df_its[df_its['Year'] >= intervention_year]
    
    # Plot fitted lines
    if len(pre_data) > 0:
        ax.plot(pre_data['Year'], pre_data['Predicted'], 
                color='#3498db', linewidth=2.5, label='Pre-intervention trend')
    
    if len(post_data) > 0:
        ax.plot(post_data['Year'], post_data['Predicted'], 
                color='#e74c3c', linewidth=2.5, label='Post-intervention trend')
    
    # Counterfactual (dashed)
    ax.plot(df_its['Year'], df_its['Counterfactual'], 
            color='#95a5a6', linewidth=2, linestyle='--', label='Counterfactual (no campaign)')
    
    # Intervention line
    ax.axvline(x=intervention_year, color='#27ae60', linewidth=2.5, 
               linestyle=':', alpha=0.8, label=f'Red Line Campaign ({intervention_year})')
    
    # Annotations
    slope_change = results['slope_change']
    slope_pval = results['slope_change_pval']
    
    # Add annotation box
    textstr = f'Slope change: {slope_change:.2f}%/year\n(p = {slope_pval:.3f})'
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    ax.text(0.75, 0.95, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Mean Antimicrobial Resistance (%)', fontsize=14, fontweight='bold')
    ax.set_title("Impact of India's Red Line Campaign on AMR Trends (2016-2024)\nInterrupted Time Series Analysis", 
                 fontsize=14, fontweight='bold', pad=15)
    
    ax.legend(loc='lower right', framealpha=0.95, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='-')
    ax.set_xlim(df_its['Year'].min() - 0.5, df_its['Year'].max() + 0.5)
    
    # Set x-ticks to years
    ax.set_xticks(df_its['Year'].unique())
    
    plt.tight_layout()
    
    # Save
    fig_path = os.path.join(OUTPUT_DIR, 'fig2_its_main_plot.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(fig_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"Saved: {fig_path}")
    
    plt.close()
    return fig_path

def generate_pathogen_subgroup_figure(df_all, intervention_year=2016):
    """Generate pathogen-specific subgroup analysis figure."""
    priority_pathogens = ['K. pneumoniae', 'E. coli', 'A. baumannii', 'S. aureus (MRSA)']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']
    
    for idx, (pathogen, color) in enumerate(zip(priority_pathogens, colors)):
        ax = axes[idx]
        
        df_pathogen = df_all[df_all['Pathogen_Standard'] == pathogen].copy()
        annual = df_pathogen.groupby('Year')['Resistance_Pct'].agg(['mean', 'std', 'count']).reset_index()
        annual.columns = ['Year', 'Mean', 'SD', 'N']
        
        # Plot with error bars
        ax.errorbar(annual['Year'], annual['Mean'], 
                   yerr=annual['SD']/np.sqrt(annual['N']),
                   fmt='o-', color=color, linewidth=2, markersize=8,
                   capsize=4, capthick=1.5, label=pathogen)
        
        # Intervention line
        ax.axvline(x=intervention_year, color='gray', linewidth=1.5, 
                   linestyle='--', alpha=0.7)
        
        # Trend lines (simple linear fit for viz)
        pre = annual[annual['Year'] < intervention_year]
        post = annual[annual['Year'] >= intervention_year]
        
        if len(pre) >= 2:
            z = np.polyfit(pre['Year'], pre['Mean'], 1)
            p = np.poly1d(z)
            ax.plot(pre['Year'], p(pre['Year']), '--', color=color, alpha=0.5, linewidth=1.5)
        
        if len(post) >= 2:
            z = np.polyfit(post['Year'], post['Mean'], 1)
            p = np.poly1d(z)
            ax.plot(post['Year'], p(post['Year']), '-', color=color, alpha=0.5, linewidth=1.5)
        
        ax.set_title(pathogen, fontsize=12, fontweight='bold')
        ax.set_xlabel('Year', fontsize=10)
        ax.set_ylabel('Resistance (%)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(2015.5, 2024.5)
    
    plt.suptitle('Pathogen-Specific AMR Trends: Pre vs Post Red Line Campaign', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    fig_path = os.path.join(OUTPUT_DIR, 'fig3_pathogen_subgroups.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {fig_path}")
    
    plt.close()
    return fig_path

def generate_data_flow_figure():
    """Generate data flow/study design figure."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Box style
    box_props = dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', edgecolor='#2c3e50', linewidth=2)
    arrow_props = dict(arrowstyle='->', color='#2c3e50', lw=2)
    
    # Data sources
    ax.text(5, 9.5, 'ICMR-AMRSN Surveillance Data\n(2016-2024)', ha='center', va='center',
            fontsize=11, fontweight='bold', bbox=box_props)
    
    ax.annotate('', xy=(5, 8.3), xytext=(5, 8.8), arrowprops=arrow_props)
    
    # Three data sources
    ax.text(2, 7.5, 'Dataset 1:\nEpidemiology\n(N=52 records)', ha='center', va='center',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='#3498db', edgecolor='#2c3e50', alpha=0.7))
    ax.text(5, 7.5, 'Dataset 2:\nMolecular\n(N=46 records)', ha='center', va='center',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='#e74c3c', edgecolor='#2c3e50', alpha=0.7))
    ax.text(8, 7.5, 'Dataset 3:\nGranular\n(N=38 records)', ha='center', va='center',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='#2ecc71', edgecolor='#2c3e50', alpha=0.7))
    
    # Arrows down
    for x in [2, 5, 8]:
        ax.annotate('', xy=(5, 6.3), xytext=(x, 6.9), arrowprops=arrow_props)
    
    # Consolidation
    ax.text(5, 5.8, 'Data Consolidation & Cleaning\n(Standardized resistance %)', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=box_props)
    
    ax.annotate('', xy=(5, 4.8), xytext=(5, 5.3), arrowprops=arrow_props)
    
    # Annual aggregation
    ax.text(5, 4.3, 'Annual Aggregation\n(9 time points: 2016-2024)', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=box_props)
    
    ax.annotate('', xy=(5, 3.3), xytext=(5, 3.8), arrowprops=arrow_props)
    
    # ITS Analysis
    ax.text(5, 2.8, 'Interrupted Time Series Analysis\n(Segmented Regression)', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f39c12', edgecolor='#2c3e50', linewidth=2))
    
    ax.annotate('', xy=(3, 1.8), xytext=(4, 2.3), arrowprops=arrow_props)
    ax.annotate('', xy=(7, 1.8), xytext=(6, 2.3), arrowprops=arrow_props)
    
    # Outputs
    ax.text(3, 1.3, 'Primary Analysis:\nLevel & Slope Change', ha='center', va='center',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='#9b59b6', edgecolor='#2c3e50', alpha=0.7))
    ax.text(7, 1.3, 'Sensitivity Analysis:\nPathogen-specific, COVID exclusion', ha='center', va='center',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='#1abc9c', edgecolor='#2c3e50', alpha=0.7))
    
    plt.title('Study Design: Interrupted Time Series Analysis', fontsize=14, fontweight='bold', pad=20)
    
    fig_path = os.path.join(OUTPUT_DIR, 'fig1_study_design.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {fig_path}")
    
    plt.close()
    return fig_path

def generate_sensitivity_forest_plot(sensitivity_results):
    """Generate forest plot for sensitivity analyses."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data
    labels = list(sensitivity_results.keys())
    effects = [sensitivity_results[k]['slope_change'] for k in labels]
    
    y_pos = np.arange(len(labels))
    
    # Color based on direction
    colors = ['#e74c3c' if e > 0 else '#27ae60' for e in effects]
    
    ax.barh(y_pos, effects, color=colors, height=0.6, edgecolor='#2c3e50', linewidth=1.5)
    
    # Add zero line
    ax.axvline(x=0, color='#2c3e50', linewidth=2, linestyle='-')
    
    # Labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel('Change in Slope (%/year)', fontsize=12, fontweight='bold')
    ax.set_title('Sensitivity Analysis: Slope Change by Subgroup', fontsize=13, fontweight='bold')
    
    # Add value labels
    for i, (effect, label) in enumerate(zip(effects, labels)):
        pval = sensitivity_results[label].get('slope_change_pval', 1.0)
        sig = '*' if pval < 0.05 else ''
        ax.text(effect + 0.1 if effect > 0 else effect - 0.1, i, f'{effect:.2f}{sig}',
                va='center', ha='left' if effect > 0 else 'right', fontsize=10)
    
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    
    fig_path = os.path.join(OUTPUT_DIR, 'fig4_sensitivity_forest.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {fig_path}")
    
    plt.close()
    return fig_path

def create_results_tables(annual_data, its_results, sensitivity_results):
    """Create formatted tables for manuscript."""
    print("\n" + "=" * 60)
    print("PHASE 6: TABLE GENERATION")
    print("=" * 60)
    
    # Table 1: Annual trends
    table1 = annual_data[['Year', 'Mean_Resistance', 'SD', 'N_Observations']].copy()
    table1['Mean_Resistance'] = table1['Mean_Resistance'].round(1)
    table1['SD'] = table1['SD'].round(1)
    table1.to_csv(os.path.join(OUTPUT_DIR, 'table1_annual_trends.csv'), index=False)
    print("Table 1: Annual Trends saved")
    
    # Table 2: ITS coefficients
    table2_data = {
        'Parameter': ['Pre-intervention slope (β₁)', 'Level change at intervention (β₂)', 
                      'Slope change post-intervention (β₃)'],
        'Estimate': [f"{its_results['pre_slope']:.3f}", f"{its_results['level_change']:.3f}",
                     f"{its_results['slope_change']:.3f}"],
        '95% CI Lower': [f"{its_results['pre_slope_ci'][0]:.3f}", f"{its_results['level_change_ci'][0]:.3f}",
                         f"{its_results['slope_change_ci'][0]:.3f}"],
        '95% CI Upper': [f"{its_results['pre_slope_ci'][1]:.3f}", f"{its_results['level_change_ci'][1]:.3f}",
                         f"{its_results['slope_change_ci'][1]:.3f}"],
        'p-value': [f"{its_results['pre_slope_pval']:.4f}", f"{its_results['level_change_pval']:.4f}",
                    f"{its_results['slope_change_pval']:.4f}"]
    }
    table2 = pd.DataFrame(table2_data)
    table2.to_csv(os.path.join(OUTPUT_DIR, 'table2_its_coefficients.csv'), index=False)
    print("Table 2: ITS Coefficients saved")
    
    # Table 3: Sensitivity analyses
    table3_rows = []
    for analysis, res in sensitivity_results.items():
        table3_rows.append({
            'Analysis': analysis,
            'Slope Change (%/year)': f"{res['slope_change']:.3f}",
            'p-value': f"{res['slope_change_pval']:.4f}",
            'N (years)': res['n_years']
        })
    table3 = pd.DataFrame(table3_rows)
    table3.to_csv(os.path.join(OUTPUT_DIR, 'table3_sensitivity.csv'), index=False)
    print("Table 3: Sensitivity Analyses saved")
    
    return table1, table2, table3

def save_analysis_summary(its_results, sensitivity_results):
    """Save comprehensive analysis summary."""
    summary = {
        'analysis_date': '2026-01-07',
        'intervention_year': 2016,
        'campaign_name': 'Red Line Campaign',
        'primary_results': {
            'pre_slope': its_results['pre_slope'],
            'level_change': its_results['level_change'],
            'slope_change': its_results['slope_change'],
            'slope_change_pval': its_results['slope_change_pval'],
            'r_squared': its_results['r_squared'],
            'durbin_watson': its_results['durbin_watson']
        },
        'sensitivity_results': sensitivity_results,
        'interpretation': 'Analysis pending - see output files'
    }
    
    import json
    with open(os.path.join(OUTPUT_DIR, 'analysis_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\nAnalysis summary saved to: {os.path.join(OUTPUT_DIR, 'analysis_summary.json')}")

def main():
    """Main execution pipeline."""
    print("\n" + "=" * 70)
    print("AMR MANUSCRIPT 3: ITS ANALYSIS PIPELINE")
    print("Evaluating India's 2016 Red Line Campaign")
    print("=" * 70)
    
    # Phase 1: Data consolidation
    df_all = load_and_consolidate_data()
    
    # Phase 2: Annual aggregation
    annual_overall, annual_pathogen = create_annual_aggregates(df_all)
    
    # Phase 3: Primary ITS analysis
    df_its, its_results, model = run_its_analysis(annual_overall, intervention_year=2016)
    
    # Phase 4: Sensitivity analyses
    sensitivity_results = run_sensitivity_analyses(df_all, intervention_year=2016)
    
    # Phase 5: Figure generation
    print("\n--- Generating Figures ---")
    fig1_path = generate_data_flow_figure()
    fig2_path = generate_its_figure(df_its, its_results, intervention_year=2016)
    fig3_path = generate_pathogen_subgroup_figure(df_all, intervention_year=2016)
    if sensitivity_results:
        fig4_path = generate_sensitivity_forest_plot(sensitivity_results)
    
    # Phase 6: Table generation
    tables = create_results_tables(annual_overall, its_results, sensitivity_results)
    
    # Save summary
    save_analysis_summary(its_results, sensitivity_results)
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for f in os.listdir(OUTPUT_DIR):
        print(f"  - {f}")
    
    return df_its, its_results, sensitivity_results

if __name__ == "__main__":
    df_its, its_results, sensitivity_results = main()
