# SLIIT Codefest Datathon 2026: Urban Flow Analytics Data Challenge 🚖📊
### **Team: Gravitons**

## Overview
This repository contains the complete end-to-end data pipeline, anomaly quantification framework, exploratory data analysis (EDA), predictive machine learning modeling, and spatial-temporal clustering for **Round 1 of the Urban Flow Analytics Data Challenge** (Datathon 2026) developed by **Team Gravitons**.

The solution unifies high-volume urban taxi trip records from NYC across a full 12-month period (April 2025 – March 2026) totaling **48,601,782 rides** joined with spatial taxi zone metadata across 265 discrete geographical zones.

---

## Technical Architecture & Pipeline Stages

### 1. High-Performance Columnar Merging (DuckDB + Apache Parquet)
- Merged **12 monthly CSV files (~4.97 GB)** and performed two relational `LEFT JOIN` operations with the spatial zone lookup dataset (for origin and destination boroughs, zones, and service zones).
- Persisted to **ZSTD-compressed Apache Parquet**, reducing file size to **838 MB (83.1% storage reduction)** while enabling sub-second analytical queries across 48.6 million rows without out-of-memory overhead.

### 2. Rigorous Data Quality Audit & Anomaly Quantification (Challenge Section 1)
Audited all **48,601,782 records** with precise row counts, percentage impacts, and separated post-audit engineering justifications:
- **Negative Base Fares (`base_fare < 0`)**: 2,400,031 rows (4.94%) $\rightarrow$ *Drop* (meter reversals/disputes).
- **Negative Total Charges (`charge_total < 0`)**: 875,399 rows (1.80%) $\rightarrow$ *Drop* (voided transactions).
- **Zero Distance with Non-Zero Fare**: 1,267,110 rows (2.61%) $\rightarrow$ *Filter / Isolate* (waiting time/cancellations; isolated from distance regression).
- **Zero/Null Rider Count**: 12,636,846 rows (26.00%) $\rightarrow$ *Impute (Median = 1)* (preserves 12.6M valid trips without discarding mobility patterns).
- **Drop-off $\le$ Pickup Timestamp**: 651,610 rows (1.34%) $\rightarrow$ *Drop* (temporal causality violation/meter reset).
- **Unrealistic Speeds (> 65 mph)**: 15,866 rows (0.03%) $\rightarrow$ *Filter* (GPS jumps/clock glitches).
- **Extreme Durations (> 24 hours)**: 405 rows (0.0008%) $\rightarrow$ *Filter* (stuck meters).

### 3. Exploratory Data Analysis & Visualizations
- **Baseline Trip Dynamics**: Median trip distance is **1.63 miles** (mean: 3.39 miles), median duration is **11.23 minutes**, and median total fare is **$19.80**.
- **Temporal Trends**: Distinct dual-peak commuter curves on weekdays (8-9 AM and 5-7 PM) vs. weekend nightlife peaks (11 PM - 2 AM). Peak monthly revenue reaches **$115M/month**.
- **Spatial Transit Corridors**: Over 85% of rides are concentrated in Manhattan; JFK Airport and LaGuardia routes generate the highest revenue per trip ($65–$85).
- **Traffic Congestion Profile**: Manhattan vehicle speeds drop by over **55%** during evening rush hours (from 19.2 mph at 4 AM to 8.4 mph at 6 PM).

### 4. Predictive Machine Learning Pipelines & Results

#### Pre-Trip Distance Proxy (Preventing Target Leakage)
In real-world dispatch systems, the actual meter distance `distance_miles` is unknown before the trip begins. Using actual trip distance would represent strict target leakage. We construct an `estimated_route_distance` feature derived strictly from the **training set historical median OD distances** with hierarchical fallback.

#### Model Benchmarking & Selection (100k Sample)
Evaluated **Ridge Regression**, **Random Forest**, and **HistGradientBoostingRegressor (HGBR)** with `TargetEncoder` for high-cardinality zones. HGBR achieved superior accuracy and training scalability, with hyperparameter tuning via `RandomizedSearchCV`.

#### Track 2.1: Upfront Fare Prediction Model (Dhanus Architecture)
- **Model**: `HistGradientBoostingRegressor` (max_iter=300, learning_rate=0.1, max_leaf_nodes=255)
- **Feature Engineering**: `estimated_route_distance` (leakage-free historical median O-D distance proxy derived strictly from training data), categorical TargetEncoding for origin/destination zones.
- **Validation**: RMSE = \$8.50 | MAE = \$4.55 | $R^2$ = 0.7462
- **Test Set**: **RMSE = \$8.29 | MAE = \$4.41 | $R^2$ = 0.7653**

#### Track 2.2: On-Time Arrival Estimator (Shehan Advanced Corridor Architecture)
- **Model**: `HistGradientBoostingRegressor` with exact OD corridor lookups + dynamic network congestion state
- **Key Features**:
  1. `hist_od_duration_prior`: Historical median trip duration for exact $(O, D, \text{period})$ triplets across 48M rides (support $\ge 15$).
  2. `hist_od_pace_prior`: Historical congestion pace in min/mile for exact corridor triplets.
  3. `hourly_network_load`: Dynamic count of concurrent active trips across NYC in that departure hour.
- **Performance Progression**:
  - Baseline (Standard Features): $R^2 = 0.8049$, MAE = 3.73 mins
  - + Distance & Anomaly Cleaning: $R^2 = 0.8392$, MAE = 3.39 mins
  - **+ Historical Corridor Prior & Dynamic Load: $R^2 = 0.8686$, MAE = 3.10 mins ($+6.4\%$ lift in variance explained)**

#### Track 3.1: The Fleet Dispatcher (Multi-Horizon Demand Forecasting)
- **Official Problem Alignment**: Addresses the competition mandate to predict pickup volumes for the next 24 to 72 hours across top dispatch zones to eliminate deadheading and curb rider wait times.
- **Feature Engineering**: Autoregressive multi-horizon lag structure (`lag_24h`, `lag_48h`, `lag_72h`, `lag_168h` weekly cycle, and 24-hour moving rolling averages).
- **Evaluation on 72-Hour Forward Horizon**:
  - **$R^2 = 0.9324$** (Explains 93.2% of future pickup volume variance across NYC's busiest transit hubs).
  - **MAE = 25.28 pickups/hour** | **RMSE = 36.06 pickups/hour**.
- **Visualization Artifact**: [`eda_outputs/08_task_3_1_demand_forecast_72h.png`](eda_outputs/08_task_3_1_demand_forecast_72h.png) compares actual rider demand vs 72-hour forecast curves across JFK Airport, Midtown Center, Penn Station, and Upper East Side.

#### Track 3.2: Spatial-Temporal Clustering (Hotspots)
- K-Means clustering ($k=4$) on 24-hour diurnal zone demand profiles, categorizing 258 taxi zones into distinct behavioral archetypes (Morning Commuter Hubs, Daytime Commercial Districts, Evening Dining/Entertainment Hubs, Quiet Residential/Peripheral Zones).

---

## Serialized Models (Submission Requirement)

The trained models are serialized in `.pkl` format under `models/`:
- `models/fare_prediction_model.pkl` (4.7 MB) - Upfront Fare Prediction
- `models/duration_prediction_model.pkl` (8.2 MB) - On-Time Arrival Estimator
- `models/demand_forecasting_model.pkl` (984 KB) - Fleet Demand Forecaster
- `models/zone_clustering_model.pkl` (2.5 KB) - Spatial K-Means Clusterer

---

## Repository Structure

```
├── Urban_Flow_Analytics_Data_Merge_and_EDA.ipynb  # Primary master executed notebook (EDA + Models)
├── code/
│   ├── Gravitons_FinalNotebook.ipynb             # Official team submission notebook (Team Gravitons)
│   └── TeamName_FinalNotebook.ipynb              # Competition template submission notebook
├── models/                                       # Serialized model artifacts (.pkl format)
│   ├── fare_prediction_model.pkl
│   ├── duration_prediction_model.pkl
│   ├── demand_forecasting_model.pkl
│   └── zone_clustering_model.pkl
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
├── make_nb.py                                    # Automated pipeline script
└── .gitignore                                    # Excludes heavy raw datasets (>100MB)
```
