# SLIIT Codefest Datathon 2026: Urban Flow Analytics Data Challenge 🚖📊

## Overview
This repository contains the end-to-end data pipeline, anomaly quantification framework, and exploratory data analysis (EDA) for **Round 1 of the Urban Flow Analytics Data Challenge** (Datathon 2026).

The challenge analyzes high-volume urban taxi trip records from NYC across a full 12-month period (April 2025 – March 2026) totaling **48,601,782 rides** joined with spatial taxi zone metadata across 265 discrete geographical zones.

---

## Key Achievements & Technical Architecture

### 1. High-Performance Columnar Merging (DuckDB + Apache Parquet)
- Merged **12 monthly CSV files (~4.97 GB)** and performed two relational `LEFT JOIN` operations with the spatial zone lookup dataset (for origin and destination boroughs, zones, and service zones).
- Persisted to **ZSTD-compressed Apache Parquet**, reducing file size to **838 MB (83.1% storage reduction)** while enabling sub-second analytical queries across 48.6 million rows without out-of-memory overhead.

### 2. Rigorous Data Quality Audit & Anomaly Quantification (Challenge Section 1)
Audited all **48,601,782 records** with precise row counts, percentage impacts, and technical/business justifications:
- **Negative Base Fares (`base_fare < 0`)**: 2,400,031 rows (4.94%) $\rightarrow$ *Drop* (meter reversals/disputes).
- **Negative Total Charges (`charge_total < 0`)**: 875,399 rows (1.80%) $\rightarrow$ *Drop* (voided transactions).
- **Zero Distance with Non-Zero Fare**: 1,267,110 rows (2.61%) $\rightarrow$ *Filter* (waiting time/cancellations; isolated from distance regression).
- **Zero/Null Rider Count**: 12,636,846 rows (26.00%) $\rightarrow$ *Impute (Median = 1)* (preserves 12.6M valid trips without discarding signal).
- **Drop-off $\le$ Pickup Timestamp**: 651,610 rows (1.34%) $\rightarrow$ *Drop* (temporal impossibility/meter reset).
- **Unrealistic Speeds (> 65 mph)**: 15,866 rows (0.03%) $\rightarrow$ *Filter* (GPS jumps/clock glitches).
- **Extreme Durations (> 24 hours)**: 405 rows (0.0008%) $\rightarrow$ *Filter* (stuck meters).

### 3. Exploratory Data Analysis & Visualizations
- **Baseline Trip Dynamics**: Median trip distance is **1.63 miles** (mean: 3.39 miles), median duration is **11.23 minutes**, and median total fare is **$19.80**.
- **Temporal Trends**: Distinct dual-peak commuter curves on weekdays (8-9 AM and 5-7 PM) vs. weekend nightlife peaks (11 PM - 2 AM). Peak monthly revenue reaches **$115M/month**.
- **Spatial Transit Corridors**: Over 85% of rides are concentrated in Manhattan; JFK Airport and LaGuardia routes generate the highest revenue per trip ($65–$85).
- **Traffic Congestion Profile**: Manhattan vehicle speeds drop by over **55%** during evening rush hours (from 19.2 mph at 4 AM to 8.4 mph at 6 PM), confirming the necessity of time-of-day traffic interaction features for arrival time prediction.

---

## Repository Structure

```
├── Urban_Flow_Analytics_Data_Merge_and_EDA.ipynb  # Primary executed Jupyter notebook
├── code/
│   └── TeamName_FinalNotebook.ipynb              # Competition submission-named notebook
├── eda_outputs/                                  # High-resolution output visualizations
│   ├── 01_anomaly_quantification_summary.png
│   ├── 02_temporal_demand_patterns.png
│   ├── 03_spatial_hotspots_and_od_corridors.png
│   ├── 04_borough_flow_matrix.png
│   ├── 05_pricing_and_payment_breakdown.png
│   ├── 06_traffic_speed_deceleration.png
│   └── 07_feature_correlation_matrix.png
├── Urban_Flow_Analytics_Zone_Dataset.csv          # 265 taxi zones metadata
├── Data_Dictionary.pdf                           # Competition data dictionary
├── Round 1 - Urban Flow Analytics...pdf          # Official problem statement
├── make_nb.py                                    # Automated notebook generation script
└── .gitignore                                    # Excludes heavy raw datasets (>100MB)
```

---

## Requirements & Reproduction

```bash
# Clone the repository
git clone https://github.com/thuva18/Datathon-2026-Urban-Flow-Analytics.git
cd Datathon-2026-Urban-Flow-Analytics

# Install dependencies
pip install duckdb pyarrow pandas numpy matplotlib seaborn scikit-learn jupyter nbformat nbclient

# Run notebook generation / analysis
python3 make_nb.py
```
