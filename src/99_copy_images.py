import shutil
import os
import glob

src_dir = r"d:\research-automation\TB multiomics\AMR_Hotspots_Prediction\outputs\figures"
dst_dir = r"C:\Users\hssli\.gemini\antigravity\brain\90c42530-5be5-49cb-a7b5-e960c5582f78"

# Search for pngs
pngs = glob.glob(os.path.join(src_dir, "*.png"))
print(f"Found {len(pngs)} images in {src_dir}")

for p in pngs:
    dst = os.path.join(dst_dir, os.path.basename(p))
    try:
        shutil.copy2(p, dst)
        print(f"Copied {os.path.basename(p)}")
    except Exception as e:
        print(f"Failed {p}: {e}")

# Verify
if os.path.exists(os.path.join(dst_dir, "epi_trend_overall.png")):
    print("Verification: epi_trend_overall.png EXISTS in destination.")
else:
    print("Verification: epi_trend_overall.png MISSING.")
