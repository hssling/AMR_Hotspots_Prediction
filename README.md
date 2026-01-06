# Spatiotemporal AMR Prediction (India)

**Authors**: Dr. Siddalingaiah H S & Antigravity AI  
**Focus**: Predictive modeling of Antimicrobial Resistance (AMR) hotspots using granular longitudinal data.

## 📌 Project Overview
Antimicrobial Resistance (AMR) is a "silent pandemic." This project integrates national surveillance data (ICMR-AMRSN) with granular center-level metrics to forecast resistance trends.

**Key Achievements**:
*   **Data Integration**: Merged static PDF reports with longitudinal sensor-like data.
*   **Predictive Model**: Random Forest Regressor achieving **$R^2 = 0.87$**.
*   **Dashboard**: Interactive Streamlit application for real-time visualization.
*   **Surveillance**: Identified critical hotspots (Delhi, Vellore) and genetic drivers (NDM, OXA-23).

## 📂 Repository Structure
```
.
├── data/                   # Raw and Processed Datasets
│   ├── raw/                # ICMR PDFs, Excel exports
│   └── processed/          # Cleaned CSVs
├── src/                    # Source Code
│   ├── 07_...py            # Data Ingestion
│   ├── 09_...py            # ML Modeling
│   ├── 12_...py            # Advanced Modeling (Granular)
│   └── 13_dashboard.py     # Streamlit App
├── outputs/                # Generated Figures & Maps
├── submission/             # FINAL MANUSCRIPT & DOCX FILES (Ready for IJMR)
└── requirements.txt        # Dependencies
```

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   Pip dependencies (see `requirements.txt`)

### Installation
```bash
git clone https://github.com/hssling/AMR_Hotspots_Prediction.git
cd AMR_Hotspots_Prediction
pip install -r requirements.txt
```

### Running the Dashboard
```bash
streamlit run src/13_dashboard.py
```

## 🔬 Scientific Output
This work has been compiled into a manuscript for the **Indian Journal of Medical Research (IJMR)**.
*   **Manuscript**: `submission/Main_Manuscript_Blinded.docx`
*   **Findings**: High correlation between resistance and mortality ($r=0.10$); Center-specific history is the best predictor of future risk.

## 🤝 Contributing
For research collaboration, validation, or data sharing, please open an issue or contact Dr. Siddalingaiah H S.

## 📄 License
Research use only. Data derived from public ICMR reports remains property of respective agencies.
