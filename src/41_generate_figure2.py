"""
Generate Figure 2 for Manuscript 2: Distribution of Carbapenem Resistance
"""
import matplotlib.pyplot as plt
import numpy as np
import os

# Create output directory if needed
output_dir = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\outputs\figures_manuscript2"
os.makedirs(output_dir, exist_ok=True)

# Data from manuscript (resistance percentages by region/year)
data = {
    'North': [54.0, 57.0, 75.0, 63.0, 52.0],
    'South': [36.0, 38.0, 44.0],
    'West': [41.5, 45.0],
    'East': [28.0, 48.0]
}

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Box plot
positions = [1, 2, 3, 4]
box_data = [data['North'], data['South'], data['West'], data['East']]
bp = ax.boxplot(box_data, positions=positions, patch_artist=True, widths=0.6)

# Colors
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Styling
ax.set_xticklabels(['North\n(n=5)', 'South\n(n=3)', 'West\n(n=2)', 'East\n(n=2)'], fontsize=12)
ax.set_ylabel('Carbapenem Resistance (%)', fontsize=14, fontweight='bold')
ax.set_xlabel('Geographic Region', fontsize=14, fontweight='bold')
ax.set_title('Distribution of Carbapenem Resistance in K. pneumoniae\nAcross ICMR-AMRSN Regional Centers (2017-2024)', 
             fontsize=14, fontweight='bold', pad=15)

# Add median annotations
for i, d in enumerate(box_data):
    median = np.median(d)
    ax.annotate(f'{median:.1f}%', xy=(positions[i], median), 
                xytext=(positions[i]+0.3, median+2),
                fontsize=10, color='black', fontweight='bold')

# Grid and styling
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(0, 90)

# Add reference lines
ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1.5, label='Critical Threshold (50%)')
ax.legend(loc='upper left', fontsize=10)

# Tight layout
plt.tight_layout()

# Save figure
output_path = os.path.join(output_dir, "fig1_resistance_distribution.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"Figure saved to: {output_path}")
