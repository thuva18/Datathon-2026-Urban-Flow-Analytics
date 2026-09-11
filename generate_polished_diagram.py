import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def draw_top_tier_architecture():
    # Ultra crisp canvas: 16 x 11.5 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(16, 11.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')  # Modern ultra-clean slate canvas

    # =========================================================================
    # 0. HEADER HERO BANNER
    # =========================================================================
    header_box = FancyBboxPatch((0.5, 10.45), 15.0, 0.85, boxstyle="round,pad=0.08",
                                facecolor='#0F172A', edgecolor='#1E293B', linewidth=1.5, zorder=2)
    ax.add_patch(header_box)
    
    gold_bar = FancyBboxPatch((0.5, 11.22), 15.0, 0.08, boxstyle="round,pad=0.02",
                             facecolor='#F59E0B', edgecolor='none', zorder=3)
    ax.add_patch(gold_bar)
    
    ax.text(8.0, 10.98, "TEAM GRAVITONS — END-TO-END SYSTEM & ML PIPELINE ARCHITECTURE",
            ha='center', va='center', fontsize=13, fontweight='bold', color='#FFFFFF', zorder=4)
    ax.text(8.0, 10.66, "SLIIT Codefest Datathon 2026  ·  48,601,782 Record Columnar Processing Engine  ·  Tracks 2.1, 2.2, 3.1 & 3.2",
            ha='center', va='center', fontsize=9, color='#94A3B8', zorder=4)

    # =========================================================================
    # DRAWING UTILITIES
    # =========================================================================
    def draw_container_card(x, y, w, h, title, subtitle, accent_color, bg_color='#FFFFFF'):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                              facecolor=bg_color, edgecolor=accent_color, linewidth=1.4, linestyle='--', zorder=1)
        ax.add_patch(card)
        
        badge_w = min(w * 0.45, len(title) * 0.11 + 1.2)
        badge = FancyBboxPatch((x + 0.35, y + h - 0.28), badge_w, 0.46, boxstyle="round,pad=0.05",
                               facecolor=accent_color, edgecolor='none', zorder=2)
        ax.add_patch(badge)
        ax.text(x + 0.35 + badge_w/2, y + h - 0.08, title,
                ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF', zorder=3)
        
        if subtitle:
            ax.text(x + 0.45 + badge_w + 0.2, y + h - 0.08, subtitle,
                    ha='left', va='center', fontsize=8, color='#64748B', fontstyle='italic', zorder=2)

    def draw_component_node(x, y, w, h, title, bullet_points, header_color='#1E293B', badge_tag=''):
        # Drop shadow
        shadow = FancyBboxPatch((x+0.05, y-0.05), w, h, boxstyle="round,pad=0.06",
                                facecolor='#E2E8F0', edgecolor='none', zorder=2)
        ax.add_patch(shadow)
        
        # Body
        node = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                              facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.2, zorder=3)
        ax.add_patch(node)
        
        # Header strip
        head_h = 0.38
        head = FancyBboxPatch((x, y + h - head_h), w, head_h, boxstyle="round,pad=0.04",
                              facecolor=header_color, edgecolor='none', zorder=4)
        ax.add_patch(head)
        
        ax.text(x + w/2, y + h - head_h/2, title,
                ha='center', va='center', fontsize=8.2, fontweight='bold', color='#FFFFFF', zorder=5)
        
        if badge_tag:
            tag_box = FancyBboxPatch((x + 0.12, y + h - 0.31), len(badge_tag)*0.07 + 0.2, 0.20,
                                     boxstyle="round,pad=0.02", facecolor='#FFFFFF', edgecolor='none', zorder=6)
            ax.add_patch(tag_box)
            ax.text(x + 0.12 + (len(badge_tag)*0.07 + 0.2)/2, y + h - 0.21, badge_tag,
                    ha='center', va='center', fontsize=6.2, fontweight='bold', color=header_color, zorder=7)

        # Content bullets
        y_pos = y + h - head_h - 0.16
        for pt in bullet_points:
            ax.text(x + 0.14, y_pos, pt, ha='left', va='top', fontsize=7.2, color='#334155', zorder=5)
            y_pos -= 0.19

    def draw_cylinder(x, y, w, h, color, label, subtext=''):
        shadow = FancyBboxPatch((x+0.05, y-0.05+0.12), w, h-0.12, boxstyle="square,pad=0",
                                facecolor='#E2E8F0', edgecolor='none', zorder=2)
        ax.add_patch(shadow)
        
        rect = FancyBboxPatch((x, y+0.12), w, h-0.12, boxstyle="square,pad=0",
                              facecolor=color, edgecolor='none', zorder=3)
        ax.add_patch(rect)
        
        bottom_ell = mpatches.Ellipse((x + w/2, y + 0.12), w, 0.26,
                                      facecolor=color, edgecolor='#0C4A6E', linewidth=1.2, zorder=3)
        ax.add_patch(bottom_ell)
        
        top_ell = mpatches.Ellipse((x + w/2, y + h), w, 0.26,
                                   facecolor='#38BDF8', edgecolor='#0C4A6E', linewidth=1.2, zorder=5)
        ax.add_patch(top_ell)
        
        ax.plot([x, x], [y+0.12, y+h], color='#0C4A6E', linewidth=1.2, zorder=4)
        ax.plot([x+w, x+w], [y+0.12, y+h], color='#0C4A6E', linewidth=1.2, zorder=4)
        
        ax.text(x + w/2, y + h/2 + 0.14, label,
                ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF', zorder=6)
        if subtext:
            ax.text(x + w/2, y + h/2 - 0.14, subtext,
                    ha='center', va='center', fontsize=7.0, color='#E0F2FE', zorder=6)

    def draw_pipe(x1, y1, x2, y2, label='', color='#475569', rad=0.0):
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                connectionstyle=f"arc3,rad={rad}",
                                arrowstyle='-|>', color=color,
                                mutation_scale=15, linewidth=1.6, zorder=4)
        ax.add_patch(arrow)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            badge = FancyBboxPatch((mx - len(label)*0.045 - 0.15, my - 0.11),
                                   len(label)*0.09 + 0.3, 0.25, boxstyle="round,pad=0.04",
                                   facecolor='#FFFFFF', edgecolor=color, linewidth=1.0, zorder=5)
            ax.add_patch(badge)
            ax.text(mx, my + 0.01, label, ha='center', va='center',
                    fontsize=6.8, fontweight='bold', color=color, zorder=6)

    def draw_metric_pill(x, y, text, bg_color='#10B981', text_color='#FFFFFF'):
        w_pill = len(text) * 0.085 + 0.28
        pill = FancyBboxPatch((x, y), w_pill, 0.26, boxstyle="round,pad=0.04",
                              facecolor=bg_color, edgecolor='none', zorder=6)
        ax.add_patch(pill)
        ax.text(x + w_pill/2, y + 0.13, text,
                ha='center', va='center', fontsize=7.0, fontweight='bold', color=text_color, zorder=7)

    # =========================================================================
    # TIER 1: RAW INGESTION & COLUMNAR STORAGE
    # =========================================================================
    draw_container_card(0.5, 8.45, 15.0, 1.80, "TIER 1: HIGH-THROUGHPUT COLUMNAR INGESTION & STORAGE",
                        "DuckDB unified engine processing 12 monthly CSV partitions into ZSTD columnar format",
                        "#0284C7", "#F0F9FF")

    draw_component_node(0.8, 8.62, 3.2, 1.30, "Raw Taxi Partitions",
                        ["• 12 Monthly CSVs (Apr 2025–Mar 2026)",
                         "• Volume: 4.86 GB uncompressed",
                         "• Total Rows: 48,601,782 records",
                         "• Raw timestamps, meters & fares"],
                        header_color='#0369A1')

    draw_component_node(4.4, 8.62, 2.9, 1.30, "Taxi Zone Reference",
                        ["• 265 Spatial Zones metadata",
                         "• Borough definitions & codes",
                         "• JFK & LGA Airport tags",
                         "• Geospatial boundary mapping"],
                        header_color='#0369A1')

    draw_component_node(7.8, 8.62, 3.4, 1.30, "DuckDB Ingestion Engine",
                        ["• Streaming columnar CSV parser",
                         "• Zero-copy schema alignment",
                         "• In-memory vectorized SQL scans",
                         "• Full dataset scan in 0.45s"],
                        header_color='#0284C7')

    draw_cylinder(11.7, 8.62, 3.5, 1.30, '#0369A1',
                  "ZSTD Master Parquet",
                  "837.72 MB  (83.2% Space Reduction)")

    draw_pipe(4.0, 9.27, 7.8, 9.27, "48.6M Rows")
    draw_pipe(7.3, 9.27, 7.8, 9.27)
    draw_pipe(11.2, 9.27, 11.7, 9.27, "ZSTD Encoded")

    # =========================================================================
    # TIER 2: ANOMALY REMEDIATION & OPERATIONAL VALIDATION (SEC 1)
    # =========================================================================
    draw_pipe(13.45, 8.62, 13.45, 8.10, color='#0284C7')

    draw_container_card(0.5, 6.45, 15.0, 1.65, "TIER 2: ANOMALY AUDIT & DATA REMEDIATION (CHALLENGE SEC 1)",
                        "Empirical classification and domain-driven remediation across 8 anomaly categories",
                        "#0D9488", "#F0FDFA")

    draw_component_node(0.8, 6.62, 3.4, 1.22, "Negative Fares & Refunds",
                        ["• Negative Base Fare: 2,400,031 (4.94%)",
                         "• Negative Total: 875,399 (1.80%)",
                         "• Action: DROPPED (accounting reversals)"],
                        header_color='#0F766E')

    draw_component_node(4.6, 6.62, 3.4, 1.22, "Sensor & Metering Errors",
                        ["• Zero Dist w/ Fare: 1,267,110 (2.61%)",
                         "• Dropoff <= Pickup: 651,610 (1.34%)",
                         "• Speed > 65 mph: 15,866 (0.03%)",
                         "• Action: FILTERED & DROPPED"],
                        header_color='#0F766E')

    draw_component_node(8.4, 6.62, 3.3, 1.22, "Solo Passenger Imputation",
                        ["• Zero / Missing Riders: 12.64M (26%)",
                         "• Fleet API solo-passenger omission",
                         "• Action: IMPUTED -> 1 (Preserved)",
                         "• Avoids 26% catastrophic row loss"],
                        header_color='#0F766E')

    draw_component_node(12.1, 6.62, 3.1, 1.22, "Clean Operational View",
                        ["• Retained: 43,863,579 trips",
                         "• Retention Ratio: 90.25%",
                         "• Mean Fare: $20.67 | Dist: 3.58 mi",
                         "• Mean Duration: 17.79 minutes"],
                        header_color='#115E59')

    draw_pipe(4.2, 7.23, 4.6, 7.23)
    draw_pipe(8.0, 7.23, 8.4, 7.23)
    draw_pipe(11.7, 7.23, 12.1, 7.23, "Validated")

    # =========================================================================
    # TIER 3: LEAKAGE-FREE FEATURE ENGINEERING & TEMPORAL SPLIT GATE
    # =========================================================================
    draw_pipe(13.65, 6.62, 13.65, 6.10, color='#0D9488')

    draw_container_card(0.5, 4.55, 15.0, 1.55, "TIER 3: FEATURE ENGINEERING & TARGET LEAKAGE CONTROL",
                        "Strict training-only priors and pre-trip quotation distance proxies",
                        "#7C3AED", "#F5F3FF")

    draw_component_node(0.8, 4.70, 3.4, 1.15, "Pre-Trip Distance Proxy",
                        ["• Historical O-D Median Distance",
                         "• Origin-Zone fallback hierarchy",
                         "• Replaces metered distance_miles",
                         "• 0% Target Leakage Guaranteed"],
                        header_color='#6D28D9')

    draw_component_node(4.5, 4.70, 3.4, 1.15, "Dynamic Corridor Priors",
                        ["• Training corridor median duration",
                         "• Corridor pace prior (min/mile)",
                         "• Peak (AM/PM) vs Off-Peak bins",
                         "• Intra-borough & airport flags"],
                        header_color='#6D28D9')

    draw_component_node(8.2, 4.70, 3.4, 1.15, "Deep Time-Series Lags",
                        ["• lag_24, lag_48, lag_72 (diurnal)",
                         "• lag_168 (weekly commuter rhythm)",
                         "• lag_336 (bi-weekly seasonal cycle)",
                         "• 24h & 7-day rolling window means"],
                        header_color='#6D28D9')

    draw_component_node(11.9, 4.70, 3.3, 1.15, "Chronological Split Gate",
                        ["• Train: Apr–Dec 2025 (1,144,861)",
                         "• Val: Jan–Feb 2026 (45,421)",
                         "• Test: Mar 2026 (25,208 holdout)",
                         "• Zero future lookahead bias"],
                        header_color='#4C1D95')

    draw_pipe(4.2, 5.27, 4.5, 5.27)
    draw_pipe(7.9, 5.27, 8.2, 5.27)
    draw_pipe(11.6, 5.27, 11.9, 5.27)

    # =========================================================================
    # TIER 4: PRODUCTION ML ENGINES & BENCHMARKING
    # =========================================================================
    draw_pipe(13.55, 4.70, 13.55, 4.15, color='#7C3AED')

    draw_container_card(0.5, 2.05, 15.0, 2.10, "TIER 4: PRODUCTION MACHINE LEARNING ENGINES (TUNED HGBR & K-MEANS)",
                        "Chronological holdout validation across all four competition challenge tracks",
                        "#EA580C", "#FFF7ED")

    # Track 2.1
    draw_component_node(0.8, 2.22, 3.3, 1.65, "Track 2.1: Upfront Fare",
                        ["• Model: HistGradientBoosting",
                         "• TargetEncoder(origin, destination)",
                         "• Hyperparams: lr=0.08, leaves=127",
                         "• l2_reg=0.2, min_samples_leaf=20",
                         "• Benchmarked vs Ridge & RF"],
                        header_color='#C2410C')
    draw_metric_pill(0.95, 2.28, "Test R² = 0.7633", bg_color='#10B981')
    draw_metric_pill(2.35, 2.28, "MAE = $4.47", bg_color='#0284C7')

    # Track 2.2
    draw_component_node(4.5, 2.22, 3.3, 1.65, "Track 2.2: Trip Duration / ETA",
                        ["• Model: Corridored HGBR",
                         "• Corridor pace & duration priors",
                         "• Absorbs 2.3x evening deceleration",
                         "• Strict chronological split fix",
                         "• Replaces leaky random split"],
                        header_color='#C2410C')
    draw_metric_pill(4.65, 2.28, "Test R² = 0.8318", bg_color='#10B981')
    draw_metric_pill(6.05, 2.28, "MAE = 3.48 min", bg_color='#0284C7')

    # Track 3.1
    draw_component_node(8.2, 2.22, 3.4, 1.65, "Track 3.1: 72h Fleet Dispatch",
                        ["• Model: Autoregressive HGBR",
                         "• Top 80 high-density hubs forecasting",
                         "• 72h out-of-sample forward horizon",
                         "• Multi-step lags (lag_24 to 336)",
                         "• Fortnightly cyclic memory"],
                        header_color='#C2410C')
    draw_metric_pill(8.35, 2.28, "Test R² = 0.9383", bg_color='#10B981')
    draw_metric_pill(9.85, 2.28, "MAE = 11.3 pkp/h", bg_color='#0284C7')

    # Track 3.2
    draw_component_node(12.0, 2.22, 3.2, 1.65, "Track 3.2: Spatial Clustering",
                        ["• Model: K-Means (k=4 Centroids)",
                         "• 24-hour diurnal demand profiles",
                         "• 257 discrete active taxi zones",
                         "• Archetypes: Business, Residential,",
                         "  Airports & Pre-Dawn Economy"],
                        header_color='#C2410C')
    draw_metric_pill(12.15, 2.28, "Silhouette = 0.185", bg_color='#10B981')
    draw_metric_pill(13.70, 2.28, "4 Clusters", bg_color='#8B5CF6')

    draw_pipe(12.0, 4.70, 2.45, 3.87, color='#EA580C', rad=0.08)
    draw_pipe(12.5, 4.70, 6.15, 3.87, color='#EA580C', rad=0.04)
    draw_pipe(13.0, 4.70, 9.90, 3.87, color='#EA580C', rad=-0.04)
    draw_pipe(13.5, 4.70, 13.60, 3.87, color='#EA580C', rad=-0.08)

    # =========================================================================
    # TIER 5: ARTIFACT SERIALIZATION & PRODUCTION PACKAGING
    # =========================================================================
    for xm in [2.45, 6.15, 9.90, 13.60]:
        draw_pipe(xm, 2.22, xm, 1.65, color='#EA580C')

    draw_container_card(0.5, 0.25, 15.0, 1.40, "TIER 5: MODEL SERIALIZATION & PRODUCTION ARTIFACTS",
                        "Production binaries (.pkl), complete Jupyter notebook, and publication-ready technical specifications",
                        "#16A34A", "#F0FDF4")

    draw_component_node(0.8, 0.40, 3.3, 0.98, "fare_prediction_model.pkl",
                        ["• Pipeline(TargetEncoder, HGBR)",
                         "• Serialized Size: 1.73 MB",
                         "• Sub-millisecond latency"],
                        header_color='#15803D')

    draw_component_node(4.5, 0.40, 3.3, 0.98, "duration_prediction_model.pkl",
                        ["• HGBR + Corridor Priors Matrix",
                         "• Serialized Size: 2.70 MB",
                         "• Dynamic traffic prior support"],
                        header_color='#15803D')

    draw_component_node(8.2, 0.40, 3.4, 0.98, "demand_forecasting_model.pkl",
                        ["• Autoregressive Multi-Lag Engine",
                         "• Serialized Size: 1.81 MB",
                         "• 72-hour forward projection"],
                        header_color='#15803D')

    draw_component_node(12.0, 0.40, 3.2, 0.98, "zone_clustering_model.pkl",
                        ["• Serialized K-Means Model",
                         "• Gravitons_FinalNotebook.ipynb",
                         "• Gravitons_Technical_Report.pdf"],
                        header_color='#15803D')

    plt.savefig("architecture_diagram.png", dpi=300, bbox_inches='tight', facecolor='#F8FAFC')
    plt.savefig("eda_outputs/architecture_diagram.png", dpi=300, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()
    print("✅ Ultra-clean architecture_diagram.png generated successfully with zero font warnings!")

if __name__ == "__main__":
    draw_top_tier_architecture()
