import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch
from matplotlib.path import Path
import numpy as np

def create_architecture_diagram():
    # Large high-res canvas (16 x 11.5 inches)
    fig, ax = plt.subplots(figsize=(16, 11.5), dpi=220)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC') # Clean modern slate background

    # ── Header Banner ──
    banner = FancyBboxPatch((0.5, 10.45), 15.0, 0.85, boxstyle="round,pad=0.08",
                            facecolor='#0F172A', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(banner)
    ax.text(8.0, 10.95, "TEAM GRAVITONS — END-TO-END MACHINE LEARNING SYSTEM ARCHITECTURE",
            ha='center', va='center', fontsize=13, fontweight='bold', color='#FFFFFF')
    ax.text(8.0, 10.65, "SLIIT Codefest Datathon 2026  ·  Urban Flow Analytics  ·  48.6M Record Pipeline  ·  Tracks 2.1, 2.2, 3.1 & 3.2",
            ha='center', va='center', fontsize=9.5, color='#94A3B8')

    # Helper: draw tier container box
    def draw_tier(x, y, w, h, title, subtitle, color, bg_color='#FFFFFF'):
        container = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                   facecolor=bg_color, edgecolor=color, linewidth=1.4, linestyle='--')
        ax.add_patch(container)
        # Header tab
        tab_w = len(title) * 0.12 + 1.2
        tab = FancyBboxPatch((x + 0.3, y + h - 0.28), tab_w, 0.45, boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='none')
        ax.add_patch(tab)
        ax.text(x + 0.4 + tab_w/2, y + h - 0.08, title,
                ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF')
        if subtitle:
            ax.text(x + 0.5 + tab_w + 0.2, y + h - 0.08, subtitle,
                    ha='left', va='center', fontsize=8, color='#64748B', fontstyle='italic')

    # Helper: draw component node
    def draw_node(x, y, w, h, title, lines, header_color='#1E293B', body_color='#FFFFFF', border_color='#CBD5E1'):
        # Shadow
        shadow = FancyBboxPatch((x+0.04, y-0.04), w, h, boxstyle="round,pad=0.06",
                                facecolor='#E2E8F0', edgecolor='none', zorder=1)
        ax.add_patch(shadow)
        # Main body
        node = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                              facecolor=body_color, edgecolor=border_color, linewidth=1.2, zorder=2)
        ax.add_patch(node)
        # Header banner inside node
        head_h = 0.38
        head = FancyBboxPatch((x, y + h - head_h), w, head_h, boxstyle="round,pad=0.04",
                              facecolor=header_color, edgecolor='none', zorder=3)
        ax.add_patch(head)
        ax.text(x + w/2, y + h - head_h/2, title,
                ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF', zorder=4)
        # Body text
        y_text = y + h - head_h - 0.16
        for line in lines:
            ax.text(x + 0.14, y_text, line,
                    ha='left', va='top', fontsize=7.2, color='#334155', zorder=4)
            y_text -= 0.20

    # Helper: draw pill badge
    def draw_badge(x, y, text, bg='#10B981', fg='#FFFFFF'):
        badge = FancyBboxPatch((x, y), len(text)*0.09 + 0.3, 0.28, boxstyle="round,pad=0.04",
                               facecolor=bg, edgecolor='none', zorder=5)
        ax.add_patch(badge)
        ax.text(x + (len(text)*0.09 + 0.3)/2, y + 0.14, text,
                ha='center', va='center', fontsize=7.2, fontweight='bold', color=fg, zorder=6)

    # Helper: arrows
    def connect(x1, y1, x2, y2, text='', color='#475569', rad=0.0):
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                connectionstyle=f"arc3,rad={rad}",
                                arrowstyle='-|>', color=color,
                                mutation_scale=14, linewidth=1.5, zorder=4)
        ax.add_patch(arrow)
        if text:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 0.12, text, ha='center', va='bottom',
                    fontsize=7, fontweight='bold', color=color,
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor=color, lw=0.8), zorder=5)

    def ortho_v(x, y1, y2, color='#475569'):
        arrow = FancyArrowPatch((x, y1), (x, y2),
                                arrowstyle='-|>', color=color,
                                mutation_scale=14, linewidth=1.5, zorder=4)
        ax.add_patch(arrow)

    # =========================================================================
    # TIER 1: DATA INGESTION & MASTER COLUMNAR STORAGE
    # =========================================================================
    draw_tier(0.5, 8.45, 15.0, 1.80, "TIER 1: INGESTION & COLUMNAR STORAGE",
              "High-throughput unified storage & schema validation", "#0284C7", "#F0F9FF")

    draw_node(0.8, 8.62, 3.2, 1.30, "Raw Taxi Partitions",
              ["• 12 Monthly CSVs (Apr 2025–Mar 2026)",
               "• Size: 4.86 GB on disk",
               "• 48,601,782 raw trip rows",
               "• Timestamps, fares, O-D pairs"],
              header_color='#0369A1')

    draw_node(4.4, 8.62, 2.9, 1.30, "Spatial Zone Lookup",
              ["• 265 Taxi Zones metadata",
               "• NYC Borough mapping",
               "• Airport hub classifications",
               "• Boundary polygon lookups"],
              header_color='#0369A1')

    draw_node(7.8, 8.62, 3.5, 1.30, "DuckDB Ingestion Engine",
              ["• Streaming columnar scan",
               "• Zero-copy schema unification",
               "• Fast SQL analytical queries",
               "• In-memory aggregation views"],
              header_color='#0284C7')

    draw_node(11.8, 8.62, 3.4, 1.30, "ZSTD Master Parquet",
              ["• urban_flow_analytics_merged.parquet",
               "• Footprint: 837.72 MB (83.2% savings)",
               "• Dictionary & Snappy/ZSTD encoding",
               "• Full dataset scan in 0.45 sec"],
              header_color='#0C4A6E')

    connect(4.0, 9.27, 7.8, 9.27, "48.6M Rows")
    connect(7.3, 9.27, 7.8, 9.27)
    connect(11.3, 9.27, 11.8, 9.27, "ZSTD 83.2%")

    # =========================================================================
    # TIER 2: DATA QUALITY & ANOMALY TREATMENT
    # =========================================================================
    ortho_v(13.5, 8.62, 8.10, color='#0284C7')

    draw_tier(0.5, 6.45, 15.0, 1.65, "TIER 2: ANOMALY DETECTION & DATA REMEDIATION (CHALLENGE SECTION 1)",
              "Empirical quantification of 8 anomaly categories", "#0D9488", "#F0FDFA")

    draw_node(0.8, 6.62, 3.4, 1.22, "Negative Fare / Refunds",
              ["• Negative Base Fare: 2,400,031 (4.94%)",
               "• Negative Total Charge: 875,399 (1.80%)",
               "• Action: DROPPED (accounting edits)"],
              header_color='#0F766E')

    draw_node(4.6, 6.62, 3.4, 1.22, "Sensor & Meter Errors",
              ["• Zero Dist w/ Fare: 1,267,110 (2.61%)",
               "• Dropoff <= Pickup: 651,610 (1.34%)",
               "• Speed > 65mph: 15,866 (0.03%)",
               "• Action: FILTERED / DROPPED"],
              header_color='#0F766E')

    draw_node(8.4, 6.62, 3.3, 1.22, "Missing Passenger Imputation",
              ["• Zero / Null Rider Count: 12.63M (26%)",
               "• Fleet API solo-rider omission",
               "• Action: IMPUTED -> 1 (Preserved)",
               "• Avoids 26% catastrophic data loss"],
              header_color='#0F766E')

    draw_node(12.1, 6.62, 3.1, 1.22, "Clean Operational Trips",
              ["• Total Retained: 43,863,579 trips",
               "• 90.25% operational fidelity",
               "• Mean fare: $20.67 | Dist: 3.58 mi",
               "• Mean duration: 17.79 minutes"],
              header_color='#115E59')

    connect(4.2, 7.23, 4.6, 7.23)
    connect(8.0, 7.23, 8.4, 7.23)
    connect(11.7, 7.23, 12.1, 7.23, "Cleaned")

    # =========================================================================
    # TIER 3: FEATURE ENGINEERING & TARGET LEAKAGE CONTROL
    # =========================================================================
    ortho_v(13.65, 6.62, 6.10, color='#0D9488')

    draw_tier(0.5, 4.55, 15.0, 1.55, "TIER 3: FEATURE ENGINEERING & TARGET LEAKAGE CONTROL",
              "Production-valid feature derivation with zero lookahead bias", "#7C3AED", "#F5F3FF")

    draw_node(0.8, 4.70, 3.4, 1.15, "Pre-Trip Distance Proxy",
              ["• O-D Historical Median Distance",
               "• Origin-Zone fallback fallback",
               "• Replaces metered distance_miles",
               "• Guarantees 0% Upfront Leakage"],
              header_color='#6D28D9')

    draw_node(4.5, 4.70, 3.4, 1.15, "O-D Corridor Dynamic Priors",
              ["• Corridor duration prior (train-only)",
               "• Corridor pace prior (min/mi)",
               "• Peak (AM/PM) vs Off-Peak bins",
               "• Intra-borough & airport flags"],
              header_color='#6D28D9')

    draw_node(8.2, 4.70, 3.4, 1.15, "Deep Time-Series Lags",
              ["• lag_24, lag_48, lag_72 (daily)",
               "• lag_168 (weekly commuter rhythm)",
               "• lag_336 (bi-weekly seasonal cycle)",
               "• 24h & 7-day rolling window means"],
              header_color='#6D28D9')

    draw_node(11.9, 4.70, 3.3, 1.15, "Chronological Split Gate",
              ["• Train: Apr–Dec 2025 (1,144,861)",
               "• Val: Jan–Feb 2026 (45,421)",
               "• Test: Mar 2026 (25,208 holdout)",
               "• Zero test-window contamination"],
              header_color='#4C1D95')

    connect(4.2, 5.27, 4.5, 5.27)
    connect(7.9, 5.27, 8.2, 5.27)
    connect(11.6, 5.27, 11.9, 5.27)

    # =========================================================================
    # TIER 4: MULTI-TRACK MACHINE LEARNING ENGINES & BENCHMARKING
    # =========================================================================
    ortho_v(13.55, 4.70, 4.15, color='#7C3AED')

    draw_tier(0.5, 2.05, 15.0, 2.10, "TIER 4: PRODUCTION ML MODELS (TUNED HISTGRADIENTBOOSTING & K-MEANS)",
              "Rigorous chronological holdout validation across all four challenge tracks", "#EA580C", "#FFF7ED")

    # Track 2.1
    draw_node(0.8, 2.22, 3.3, 1.65, "Track 2.1: Upfront Fare",
              ["• Model: HistGradientBoostingRegressor",
               "• TargetEncoder(origin, destination)",
               "• Hyperparams: lr=0.08, leaves=127",
               "• l2_reg=0.2, min_samples_leaf=20",
               "• Benchmark vs Ridge & Random Forest"],
              header_color='#C2410C')
    draw_badge(0.95, 2.28, "Test R² = 0.7633", bg='#10B981')
    draw_badge(2.35, 2.28, "MAE = $4.47", bg='#0284C7')

    # Track 2.2
    draw_node(4.5, 2.22, 3.3, 1.65, "Track 2.2: Trip Duration / ETA",
              ["• Model: Corridored HGBR",
               "• Corridor pace & duration priors",
               "• Absorbs 2.3x evening deceleration",
               "• Strict chronological split fix",
               "• Replaces leaky random 80/20"],
              header_color='#C2410C')
    draw_badge(4.65, 2.28, "Test R² = 0.8318", bg='#10B981')
    draw_badge(6.05, 2.28, "MAE = 3.48 min", bg='#0284C7')

    # Track 3.1
    draw_node(8.2, 2.22, 3.4, 1.65, "Track 3.1: 72h Dispatch Forecast",
              ["• Model: Autoregressive HGBR",
               "• Top 5 high-density hub forecasting",
               "• 72h out-of-sample forward horizon",
               "• Multi-step lags (lag_24 to 336)",
               "• Weekly & fortnightly cyclic memory"],
              header_color='#C2410C')
    draw_badge(8.35, 2.28, "Test R² = 0.9177", bg='#10B981')
    draw_badge(9.85, 2.28, "MAE = 27.4 pkp/h", bg='#0284C7')

    # Track 3.2
    draw_node(12.0, 2.22, 3.2, 1.65, "Track 3.2: Spatial Clustering",
              ["• Model: K-Means (k=4 Centroids)",
               "• 24-hour diurnal demand profiles",
               "• 257 discrete active taxi zones",
               "• Archetypes: Business, Residential,",
               "  Airports & Pre-Dawn Economy"],
              header_color='#C2410C')
    draw_badge(12.15, 2.28, "Silhouette = 0.185", bg='#10B981')
    draw_badge(13.70, 2.28, "4 Clusters", bg='#8B5CF6')

    connect(12.0, 4.70, 2.45, 3.87, color='#EA580C', rad=0.08)
    connect(12.5, 4.70, 6.15, 3.87, color='#EA580C', rad=0.04)
    connect(13.0, 4.70, 9.90, 3.87, color='#EA580C', rad=-0.04)
    connect(13.5, 4.70, 13.60, 3.87, color='#EA580C', rad=-0.08)

    # =========================================================================
    # TIER 5: MODEL SERIALIZATION & PRODUCTION ARTIFACTS
    # =========================================================================
    for x_m in [2.45, 6.15, 9.90, 13.60]:
        ortho_v(x_m, 2.22, 1.65, color='#EA580C')

    draw_tier(0.5, 0.25, 15.0, 1.40, "TIER 5: SERIALIZED ARTIFACTS & COMPETITION DELIVERABLES",
              "Production-ready standalone binaries & fully reproducible Jupyter execution", "#16A34A", "#F0FDF4")

    draw_node(0.8, 0.40, 3.3, 0.98, "fare_prediction_model.pkl",
              ["• Pipeline(TargetEncoder, HGBR)",
               "• Size: 1.73 MB",
               "• Sub-millisecond latency"],
              header_color='#15803D')

    draw_node(4.5, 0.40, 3.3, 0.98, "duration_prediction_model.pkl",
              ["• HGBR + Corridor Priors Matrix",
               "• Size: 2.70 MB",
               "• Dynamic traffic prior support"],
              header_color='#15803D')

    draw_node(8.2, 0.40, 3.4, 0.98, "demand_forecasting_model.pkl",
              ["• Autoregressive Multi-Lag Engine",
               "• Size: 4.23 MB",
               "• 72-hour forward projections"],
              header_color='#15803D')

    draw_node(12.0, 0.40, 3.2, 0.98, "zone_clustering_model.pkl",
              ["• Serialized K-Means Model",
               "• Gravitons_FinalNotebook.ipynb",
               "• Gravitons_Technical_Report.pdf"],
              header_color='#15803D')

    # Save to high-res PNG
    plt.savefig("architecture_diagram.png", dpi=250, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()
    print("✅ Created architecture_diagram.png successfully!")

if __name__ == "__main__":
    create_architecture_diagram()
