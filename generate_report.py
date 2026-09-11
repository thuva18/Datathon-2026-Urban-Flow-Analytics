"""
generate_report.py
==================
Generates Gravitons_Technical_Report.pdf for SLIIT Codefest Datathon 2026.
Run from project root: python3 generate_report.py
"""

import os, io, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from PIL import Image as PILImage

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
EDA_DIR    = os.path.join(BASE_DIR, "eda_outputs")
OUTPUT_PDF = os.path.join(BASE_DIR, "Gravitons_Technical_Report.pdf")

# Colour palette
NAVY   = colors.HexColor("#0D1B2A")
BLUE   = colors.HexColor("#1A73E8")
TEAL   = colors.HexColor("#00897B")
AMBER  = colors.HexColor("#F4A61D")
LIGHT  = colors.HexColor("#F0F4FF")
GREY   = colors.HexColor("#5F6368")
WHITE  = colors.white
BLACK  = colors.black

W, H   = A4
M      = 1.8 * cm   # margin

styles = getSampleStyleSheet()

def style(name, **kw):
    return ParagraphStyle(name, **kw)

H1           = style("H1",          fontName="Helvetica-Bold",  fontSize=14, textColor=NAVY,    spaceBefore=12, spaceAfter=4, leading=18)
H2           = style("H2",          fontName="Helvetica-Bold",  fontSize=11, textColor=BLUE,    spaceBefore=8, spaceAfter=3, leading=15)
H3           = style("H3",          fontName="Helvetica-BoldOblique", fontSize=9.5, textColor=TEAL, spaceBefore=6, spaceAfter=2)
Body         = style("Body",        fontName="Helvetica",       fontSize=8.5, textColor=BLACK,  leading=12.5, spaceBefore=2, spaceAfter=2, alignment=TA_JUSTIFY)
Bullet       = style("Bullet",      fontName="Helvetica",       fontSize=8.5, textColor=BLACK,  leading=12, leftIndent=14, bulletIndent=4, spaceBefore=2)
Caption      = style("Caption",     fontName="Helvetica-Oblique", fontSize=7.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
Mono         = style("Mono",        fontName="Courier",         fontSize=7.5, textColor=NAVY,   leading=10, leftIndent=8)
TableHeader  = style("TH",          fontName="Helvetica-Bold",  fontSize=8,  textColor=WHITE,   alignment=TA_CENTER)
TableCell    = style("TC",          fontName="Helvetica",       fontSize=8,  textColor=BLACK,   alignment=TA_CENTER)
TableCellL   = style("TCL",         fontName="Helvetica",       fontSize=8,  textColor=BLACK,   alignment=TA_LEFT)

def P(text, sty=Body): return Paragraph(text, sty)
def SP(n=4): return Spacer(1, n)
def HR(): return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=4, spaceBefore=4)

def draw_cover(canvas, doc):
    canvas.saveState()
    # Navy background
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Amber accent bar top
    canvas.setFillColor(AMBER)
    canvas.rect(0, H - 1.2*cm, W, 1.2*cm, fill=1, stroke=0)
    # Teal accent bar bottom
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, W, 0.8*cm, fill=1, stroke=0)
    # Decorative circle pattern (top-right)
    canvas.setFillColor(colors.HexColor("#1A3A5C"))
    for r in [180, 230, 280]:
        canvas.circle(W, H - 1.2*cm, r, fill=1, stroke=0)

    # Header badge
    canvas.setFillColor(BLUE)
    canvas.roundRect(M, H*0.74, W - 2*M, 1.3*cm, 6, fill=1, stroke=0)

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawCentredString(W/2, H*0.762, "SLIIT CODEFEST DATATHON 2026  ·  ROUND 1")

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawCentredString(W/2, H*0.65, "Urban Flow Analytics")
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawCentredString(W/2, H*0.605, "Data Challenge")

    canvas.setFillColor(AMBER)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(W/2, H*0.555, "Comprehensive Technical Report & Architecture Specification")

    # Divider
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(2)
    canvas.line(M*2, H*0.53, W - M*2, H*0.53)

    # Team block
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawCentredString(W/2, H*0.485, "Team: Gravitons")
    canvas.setFont("Helvetica", 10.5)
    canvas.drawCentredString(W/2, H*0.46, "Sri Lanka Institute of Information Technology (SLIIT)")

    # Member table
    members = [
        ("Thuvaragan. B",      "IT24103754", "0718734571", "thuvabas@gmail.com"),
        ("Shehan Louis",      "IT24100701", "0778240868", "shehanlouis2k4@gmail.com"),
        ("Chamod de Alwis",   "IT24100038", "0761852636", "dealwisca@gmail.com"),
        ("Dinindu Vishwajith", "IT24101219", "0705011967", "dinindu1919@gmail.com"),
    ]
    y0 = H*0.40
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.setFillColor(AMBER)
    canvas.drawString(M*1.4, y0, "Name")
    canvas.drawString(M*1.4 + 4.5*cm, y0, "Index No.")
    canvas.drawString(M*1.4 + 7.5*cm, y0, "Contact")
    canvas.drawString(M*1.4 + 10.5*cm, y0, "Email")
    canvas.setLineWidth(0.5)
    canvas.setStrokeColor(AMBER)
    canvas.line(M*1.4, y0 - 3, W - M*1.4, y0 - 3)

    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(WHITE)
    for j, (name, idx, phone, email) in enumerate(members):
        yy = y0 - (j+1)*0.75*cm
        canvas.drawString(M*1.4,           yy, name)
        canvas.drawString(M*1.4 + 4.5*cm,  yy, idx)
        canvas.drawString(M*1.4 + 7.5*cm,  yy, phone)
        canvas.drawString(M*1.4 + 10.5*cm, yy, email)

    # Date + repo
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica-Oblique", 8.5)
    canvas.drawCentredString(W/2, 2.2*cm, "September 2026")
    canvas.setFillColor(TEAL)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawCentredString(W/2, 1.5*cm, "Repository: https://github.com/thuva18/Datathon-2026-Urban-Flow-Analytics")
    canvas.restoreState()

def draw_later_pages(canvas, doc):
    canvas.saveState()
    # Running header
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(M, H - 1.2*cm, "SLIIT Codefest Datathon 2026  ·  Urban Flow Analytics  ·  Team Gravitons")
    canvas.drawRightString(W - M, H - 1.2*cm, "Technical Report")
    canvas.setStrokeColor(colors.HexColor("#E0E0E0"))
    canvas.setLineWidth(0.4)
    canvas.line(M, H - 1.3*cm, W - M, H - 1.3*cm)

    # Running footer
    canvas.line(M, 1.3*cm, W - M, 1.3*cm)
    canvas.drawString(M, 0.9*cm, "Confidential — Evaluated for SLIIT Datathon 2026 Leaderboard")
    canvas.drawRightString(W - M, 0.9*cm, f"Page {doc.page}")
    canvas.restoreState()

def build_architecture_diagram():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 11); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')

    LAYERS = [
        (6.3, 0.75,  "#0D1B2A", "white",             "1. DATA INGESTION & MASTER COMPACTION",
         ["12 Monthly Taxi Trip CSVs (4.86 GB)", "Zone Lookup Metadata (265 zones)", "DuckDB -> ZSTD Parquet (838 MB, 83.2% compression)"]),
        (5.1, 0.75,  "#1A3A5C", "white",             "2. DATA QUALITY AUDIT & TREATMENT (SEC 1)",
         ["8 Anomaly Checks on 48.6M rows", "Zero Distance & Neg Fares Treated", "Rider Count Imputed to 1 (26%)", "43.86M Clean Trips"]),
        (3.9, 0.75,  "#1A73E8", "white",             "3. FEATURE ENGINEERING & LEAKAGE PREVENTION",
         ["Pre-Trip Distance Proxy (O-D Medians)", "O-D Corridor Dynamic Priors", "Temporal Diurnal & Rush Flags", "Multi-Horizon Lags (24h to 336h)"]),
        (2.7, 0.75,  "#00897B", "white",             "4. CHRONOLOGICAL DATA SPLITS",
         ["Train: Apr 2025 - Dec 2025 (1.14M)", "Validation: Jan 2026 - Feb 2026 (45.4K)", "Test: March 2026 (25.2K)"]),
        (1.5, 0.75,  "#F4A61D", "#0D1B2A",           "5. MULTI-MODEL PREDICTIVE PIPELINE (HGBR & K-Means)",
         ["Track 2.1: Fare (R²=0.763, MAE=$4.47)", "Track 2.2: ETA (R²=0.832, MAE=3.48m)", "Track 3.1: 72h Dispatch (R²=0.918)", "Track 3.2: Cluster (k=4)"]),
        (0.3, 0.75,  "#D32F2F", "white",             "6. MODEL SERIALIZATION & PRODUCTION ARTIFACTS",
         ["fare_prediction_model.pkl", "duration_prediction_model.pkl", "demand_forecasting_model.pkl", "zone_clustering_model.pkl"]),
    ]

    for (yc, h, bg, fg, title, items) in LAYERS:
        rect = mpatches.FancyBboxPatch((0.4, yc - h/2), 10.2, h,
            boxstyle="round,pad=0.03", linewidth=1.0,
            edgecolor="#FFFFFF", facecolor=bg)
        ax.add_patch(rect)
        ax.text(0.65, yc + h/2 - 0.16, title,
                fontsize=8.0, fontweight='bold', color=fg, va='top')
        item_text = "   •   ".join(items)
        ax.text(0.65, yc - 0.08, item_text,
                fontsize=6.8, color=fg, alpha=0.95, va='center')

    arrow_props = dict(arrowstyle="-|>", color="#555555", lw=1.2,
                       mutation_scale=10, connectionstyle="arc3,rad=0.0")
    ys = [l[0] for l in LAYERS]
    for i in range(len(ys)-1):
        ax.annotate("", xy=(5.5, ys[i+1] + LAYERS[i+1][1]/2 + 0.03),
                    xytext=(5.5, ys[i] - LAYERS[i][1]/2 - 0.03),
                    arrowprops=arrow_props)

    ax.set_title("Team Gravitons — End-to-End Urban Flow ML System Architecture",
                 fontsize=10.5, fontweight='bold', color='#0D1B2A', pad=8)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=180, bbox_inches='tight', facecolor='#F8F9FA')
    plt.close()
    buf.seek(0)
    return buf

def make_table(data, col_widths, header_bg=NAVY):
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ('BACKGROUND', (0,0), (-1,0), header_bg),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',      (0,1), (0,-1), 'LEFT'),
        ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,1), (-1,-1), 7.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT, WHITE]),
        ('GRID',       (0,0), (-1,-1), 0.3, colors.HexColor("#CCCCCC")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t

def eda_image(filename, width_cm=14.5, caption=""):
    path = os.path.join(EDA_DIR, filename)
    if not os.path.exists(path):
        return [P(f"[Image not found: {filename}]", Caption)]
    with PILImage.open(path) as im:
        w_px, h_px = im.size
    ratio = h_px / w_px
    target_w = width_cm * cm
    target_h = target_w * ratio
    if target_h > 9.5 * cm:
        target_h = 9.5 * cm
        target_w = target_h / ratio
    img = Image(path, width=target_w, height=target_h)
    flowables = [img]
    if caption:
        flowables.append(P(caption, Caption))
    return flowables

def build():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=M, bottomMargin=M,
        title="Urban Flow Analytics Technical Report - Team Gravitons",
        author="Team Gravitons (SLIIT)",
        subject="SLIIT Codefest Datathon 2026",
    )

    story = []

    # Page 1: Dedicated Cover Page handled via canvas onFirstPage.
    # We push an initial PageBreak so story starts on Page 2.
    story.append(PageBreak())

    # Page 2: Executive Summary & Table of Contents
    story.append(P("Executive Summary &amp; Table of Contents", H1))
    story.append(HR())
    story.append(P("This comprehensive technical report presents the architecture, data engineering, "
                   "anomaly justification, predictive machine learning benchmarks, and spatial-temporal clustering "
                   "developed by <b>Team Gravitons</b> (SLIIT) for the <b>Urban Flow Analytics Data Challenge (Datathon 2026)</b>. "
                   "The pipeline ingests 48,601,782 raw trip records, enforces rigorous data cleansing and target leakage prevention, "
                   "and operationalizes four core machine learning tracks with serialized production models.", Body))
    story.append(SP(6))

    toc_data = [
        ["Section 1", "Data Preprocessing & Feature Engineering (Page Limit: 1 Page)", "Page 3"],
        ["Section 2", "Model Development Methodology & Hyperparameter Optimization", "Page 4"],
        ["Section 3", "Evaluation Metrics & Results Benchmarking", "Page 5"],
        ["Section 4", "Solution Architecture Diagram (Layered Pipeline)", "Page 6"],
        ["Section 5", "Exploratory Data Analysis — Key Visualizations & Kinematics", "Page 7"],
        ["Section 6", "Key Findings, Business Implications & Strategic Recommendations", "Page 10"],
    ]
    t_toc = Table([[P(f"<b>{r[0]}</b>", TableCellL), P(r[1], TableCellL), P(f"<b>{r[2]}</b>", TableCell)] for r in toc_data],
                  colWidths=[2.8*cm, 10.5*cm, 2.0*cm])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # Page 3: Section 1 (Strict 1 Page Requirement)
    story.append(P("1. Data Preprocessing &amp; Feature Engineering", H1))
    story.append(HR())
    story.append(P("<b>Ingestion & Master Merging:</b> 12 monthly CSVs spanning April 2025 to March 2026 (4.86 GB) "
                   "and 265 spatial zone definitions were consolidated into an Apache Parquet master dataset (838 MB) "
                   "via DuckDB with ZSTD compression, slashing disk footprint by <b>83.2%</b> and enabling sub-second analytical querying.", Body))
    story.append(SP(3))

    story.append(P("1.1 Data Quality Audit &amp; Treatment Justification (Challenge Section 1)", H2))
    anomaly_table = [
        [P("Anomaly Category", TableHeader), P("Impacted Rows", TableHeader), P("Share (%)", TableHeader), P("Engineering Treatment", TableHeader)],
        [P("Negative Base Fare (base_fare < 0)", TableCellL), "2,400,031", "4.94%", "Dropped: Accounting reversals / chargebacks"],
        [P("Negative Total Charge (charge_total < 0)", TableCellL), "875,399", "1.80%", "Dropped: Refund transactions, non-operational"],
        [P("Zero Distance with Positive Fare", TableCellL), "1,267,110", "2.61%", "Dropped: Stationary waiting / cancellations"],
        [P("Zero or Missing Rider Count", TableCellL), "12,636,846", "26.00%", "Imputed -> 1: Sensor/fleet API default omissions"],
        [P("Drop-off <= Pickup Timestamp", TableCellL), "651,610", "1.34%", "Dropped: Clock sync & GPS logging glitches"],
        [P("Unrealistic Urban Speed (> 65 mph)", TableCellL), "15,866", "0.03%", "Filtered: Severe GPS multi-path errors"],
        [P("Excessive Duration (> 24 Hours)", TableCellL), "405", "<0.01%", "Dropped: Stranded meter sessions"],
        [P("Out-of-Range Timestamp (<2025-04 or >2026-03)", TableCellL), "14", "<0.01%", "Dropped: Hardware RTC reset artifacts"],
        [P("<b>Clean Operational Trips Retained</b>", TableCellL), "<b>43,863,579</b>", "<b>90.2%</b>", "<b>Validated Master Analytical View</b>"],
    ]
    story.append(make_table(anomaly_table, [5.8*cm, 2.5*cm, 2.0*cm, 5.0*cm]))
    story.append(SP(3))

    story.append(P("1.2 Feature Engineering Suite &amp; Leakage Prevention", H2))
    story.append(P("• <b>Pre-Trip Distance Proxy (Track 2.1):</b> Actual metered <i>distance_miles</i> is absent at upfront quotation. "
                   "We map historical median corridor distances <code>estimated_route_distance</code> strictly computed from the training split, "
                   "falling back to origin median, then global median to guarantee zero test leakage.", Body))
    story.append(P("• <b>Dynamic O-D Corridor Priors (Track 2.2):</b> Computed median trip duration and pace priors across "
                   "peak (morning/evening) and off-peak windows for all 265x265 corridors, providing high-capacity prior features.", Body))
    story.append(P("• <b>Autoregressive Lags & Rolling Statistics (Track 3.1):</b> Multi-step time-series lags "
                   "<code>lag_24</code>, <code>lag_48</code>, <code>lag_72</code>, <code>lag_168</code> (weekly), and <code>lag_336</code> (fortnightly) "
                   "paired with 24-hour and 7-day rolling means to capture diurnal and seasonal periodicity.", Body))
    story.append(PageBreak())

    # Page 4: Section 2: Model Development Methodology
    story.append(P("2. Model Development Methodology", H1))
    story.append(HR())

    story.append(P("2.1 Chronological Split Architecture", H2))
    story.append(P("To guarantee that evaluation metrics reflect real-world predictive utility without lookahead bias, "
                   "data partitions were structured strictly chronologically across the 12-month operational timeline:", Body))
    split_info = [
        [P("Split Partition", TableHeader), P("Temporal Window", TableHeader), P("Sample Size", TableHeader), P("Purpose", TableHeader)],
        ["Training Set", "April 1, 2025 – Dec 31, 2025", "1,144,861 trips", "Corridor prior generation, baseline & tree fitting"],
        ["Validation Set", "January 1, 2026 – Feb 28, 2026", "45,421 trips", "Hyperparameter tuning & family benchmarking"],
        ["Test Set", "March 1, 2026 – March 31, 2026", "25,208 trips", "Unbiased out-of-time production holdout evaluation"],
    ]
    story.append(make_table(split_info, [2.8*cm, 4.4*cm, 2.8*cm, 5.3*cm]))
    story.append(SP(4))

    story.append(P("2.2 Track 2.1: Upfront Fare Prediction (HistGradientBoosting)", H2))
    story.append(P("We benchmarked Ridge Regression, Random Forest, and Histogram-based Gradient Boosting (HGBR) "
                   "with Target Encoding on origin and destination locations. HGBR demonstrated superior non-linear fitting and runtime efficiency. "
                   "Hyperparameters tuned via RandomizedSearchCV (CV=3): <code>learning_rate=0.08</code>, <code>max_leaf_nodes=127</code>, "
                   "<code>l2_regularization=0.2</code>, and <code>min_samples_leaf=20</code>, avoiding overfitting on high-density routes.", Body))
    story.append(SP(4))

    story.append(P("2.3 Track 2.2: On-Time Arrival Estimator (ETA)", H2))
    story.append(P("Duration modeling requires isolating route-specific traffic bottlenecks. We integrated O-D corridor duration priors, "
                   "pace priors, airport trip indicators, and intra-borough flags. Crucially, the model was migrated from random splitting "
                   "to a strict chronological holdout, eliminating subtle leakage and delivering stable generalization.", Body))
    story.append(SP(4))

    story.append(P("2.4 Track 3.1: The Fleet Dispatcher (72-Hour Ahead Demand Forecasting)", H2))
    story.append(P("Constructed a multi-horizon autoregressive time series model across the highest-demand zones. "
                   "Holding out the final 72 hours (March 28–31, 2026), the model projects 24- to 72-hour forward hourly demand "
                   "utilizing deep lag structures (up to 336h), hour-of-day cyclicity, and weekend indicators.", Body))
    story.append(SP(4))

    story.append(P("2.5 Track 3.2: Spatial-Temporal Clustering (Urban Hotspots)", H2))
    story.append(P("Normalized 24-hour pickup profiles across 257 active zones were segmented using K-Means (k=4). "
                   "Cluster centroids reveal distinct diurnal signatures: Morning Business Rush, Evening Residential Peaks, "
                   "Midday-Steady Transit Hubs (JFK/LGA), and Late-Night Entertainment nodes.", Body))
    story.append(PageBreak())

    # Page 5: Section 3: Evaluation Metrics & Results
    story.append(P("3. Evaluation Metrics &amp; Results", H1))
    story.append(HR())

    story.append(P("3.1 Metric Selection Rationale", H2))
    story.append(P("• <b>R² Score (Coefficient of Determination):</b> Measures explained variance against the historical mean baseline, "
                   "enabling cross-track comparison across fare ($) and duration (minutes).<br/>"
                   "• <b>MAE (Mean Absolute Error):</b> Intuitive operational loss metric that directly translates to financial quotation risk ($) "
                   "and passenger scheduling buffer (minutes) without excessive outlier distortion.<br/>"
                   "• <b>RMSE (Root Mean Squared Error):</b> Penalizes severe forecasting failures, critical for catching surge anomalies and large delays.", Body))
    story.append(SP(4))

    story.append(P("3.2 Track Benchmark Summary", H2))
    res_table = [
        [P("Track & Task", TableHeader), P("Model Architecture", TableHeader), P("Validation R²", TableHeader), P("Test R²", TableHeader), P("Test MAE", TableHeader), P("Test RMSE", TableHeader)],
        ["Track 2.1: Upfront Fare", "HistGradientBoostingRegressor", "0.7357", P("<b>0.7633</b>", TableCell), P("<b>$4.47</b>", TableCell), "$8.39"],
        ["Track 2.2: Trip Duration (ETA)", "Corridored HistGradientBoosting", "0.7726", P("<b>0.8318</b>", TableCell), P("<b>3.48 min</b>", TableCell), "5.94 min"],
        ["Track 3.1: 72h Fleet Dispatch", "Autoregressive HGBR (Lag 24–336h)", "—", P("<b>0.9177</b>", TableCell), P("<b>27.37 trips/h</b>", TableCell), "39.78 trips/h"],
        ["Track 3.2: Hotspot Clustering", "K-Means (k=4 Centroids)", "—", P("Silhouette: <b>0.1848</b>", TableCell), P("<b>4 Archetypes</b>", TableCell), "257 Zones"],
    ]
    story.append(make_table(res_table, [3.8*cm, 4.0*cm, 1.8*cm, 1.8*cm, 2.0*cm, 1.9*cm]))
    story.append(SP(6))

    story.append(P("3.3 Fare &amp; ETA Residual Diagnostics", H2))
    story += eda_image("09_track_2_1_fare_residuals.png", width_cm=14.0,
                      caption="Figure 3.1: Track 2.1 Upfront Fare Residual Error Distribution and Predicted vs. Actual Calibration Curve.")
    story.append(SP(4))
    story += eda_image("10_track_2_2_eta_residuals.png", width_cm=14.0,
                      caption="Figure 3.2: Track 2.2 Trip Duration Residuals (MAE = 3.48 min) with 1:1 Actual vs. Predicted Alignment.")
    story.append(PageBreak())

    # Page 6: Section 4: Architecture Diagram
    story.append(P("4. Solution Architecture Diagram", H1))
    story.append(HR())
    story.append(P("The layered architecture below illustrates the complete data lifecycle—from high-throughput columnar ingestion "
                   "to feature engineering, chronological partitioning, gradient-boosted training, and model serialization.", Body))
    story.append(SP(4))

    arch_buf = build_architecture_diagram()
    arch_img = Image(arch_buf, width=15.0*cm, height=9.5*cm)
    story.append(arch_img)
    story.append(SP(4))
    story.append(P("Figure 4.1: End-to-End System Architecture for Team Gravitons ML Platform.", Caption))
    story.append(PageBreak())

    # Page 7: Section 5: EDA & Kinematics Part 1
    story.append(P("5. Exploratory Data Analysis &amp; Kinematics", H1))
    story.append(HR())

    story.append(P("5.1 Anomaly Quantification &amp; Temporal Demand Dynamics", H2))
    story += eda_image("01_anomaly_quantification_summary.png", width_cm=14.0,
                      caption="Figure 5.1: Anomaly category distribution across the 48.6M raw record audit.")
    story.append(SP(6))
    story += eda_image("02_temporal_demand_patterns.png", width_cm=14.0,
                      caption="Figure 5.2: Monthly seasonality and 24-hour diurnal pickup volume profiles.")
    story.append(PageBreak())

    # Page 8: Section 5: EDA & Kinematics Part 2
    story.append(P("5.2 Spatial Corridors &amp; Urban Congestion Deceleration", H2))
    story.append(HR())
    story += eda_image("03_spatial_hotspots_and_od_corridors.png", width_cm=14.0,
                      caption="Figure 5.3: Top origin-destination corridors and high-density pickup zones.")
    story.append(SP(6))
    story += eda_image("06_traffic_speed_deceleration.png", width_cm=14.0,
                      caption="Figure 5.4: Diurnal Speed vs. Pace (min/mile) Deceleration showing the 2.3x evening congestion penalty.")
    story.append(PageBreak())

    # Page 9: Section 5: Demand Forecasting & Clustering
    story.append(P("5.3 Multi-Horizon Demand Forecasting &amp; Zone Clustering", H1))
    story.append(HR())
    story += eda_image("08_task_3_1_demand_forecast_72h.png", width_cm=14.0,
                      caption="Figure 5.5: Task 3.1 72-Hour Ahead Dispatch Demand Forecast across Top Hubs (R² = 0.9177).")
    story.append(SP(6))
    story += eda_image("11_track_3_2_zone_clusters.png", width_cm=14.0,
                      caption="Figure 5.6: Task 3.2 Diurnal Demand Centroid Heatmaps for the 4 K-Means Behavioral Zone Clusters.")
    story.append(PageBreak())

    # Page 10: Section 6: Key Findings & Recommendations
    story.append(P("6. Key Findings, Business Implications &amp; Recommendations", H1))
    story.append(HR())

    story.append(P("6.1 High-Level Key Findings", H2))
    findings = [
        ("The 2.3x Evening Urban Deceleration Penalty",
         "Kinematic profiling reveals average taxi speeds plunge from 14.2 mph at dawn to 6.1 mph during 5–7 PM rush hours, "
         "inflating citywide pace from 4.2 to 9.8 min/mile. Static distance-based ETA engines fail during these windows, "
         "whereas our time-period corridor priors absorb this variance to keep MAE at 3.48 minutes."),
        ("Target Leakage in Upfront Pricing",
         "Models trained on actual meter distance report artificially inflated R² (>0.95) that collapses in production. "
         "Using our training-derived pre-trip O-D distance proxy guarantees zero test-time leakage while sustaining R²=0.7633."),
        ("Diurnal Predictability of Fleet Demand (R²=0.918)",
         "Transit volume across major hubs follows strong 24-hour and 168-hour periodicities. Integrating deep autoregressive lags "
         "empowers fleet dispatchers to position vehicles 72 hours in advance, reducing unserved demand."),
        ("Four Behavioral Archetypes of Urban Zones",
         "Clustering partitions 257 zones into Business Core (124 zones, 7 AM peak), Evening Residential (128 zones, 10 PM peak), "
         "Airport Hubs (3 zones, steady midday flow), and Pre-Dawn nightlife centers (2 zones)."),
    ]
    for title, text in findings:
        story.append(P(f"• <b>{title}:</b> {text}", Body))
        story.append(SP(3))

    story.append(SP(4))
    story.append(P("6.2 Strategic Business Implications &amp; Action Plan", H2))
    implications = [
        ("Dynamic Fleet Rebalancing", "Pre-dispatch vehicles from evening residential clusters to morning business nodes between 5:30 AM and 6:30 AM to capture high-fare commuter volume and cut wait times."),
        ("Transparent Upfront Quoting", "Deploy the leakage-free HGBR fare model into consumer booking apps to deliver transparent upfront fares with an average error margin of only $4.47 on trips averaging $20.67."),
        ("Congestion Buffer Scheduling", "Incorporate the dynamic corridor pace priors into ETA quotes to avoid late-arrival penalties and maintain customer trust during peak evening deceleration."),
    ]
    for title, text in implications:
        story.append(P(f"• <b>{title}:</b> {text}", Body))
        story.append(SP(3))

    story.append(SP(6))
    story.append(P("6.3 Conclusion &amp; Deliverables Checklist", H2))
    summary_data = [
        [P("Deliverable Item", TableHeader), P("Implementation Status", TableHeader), P("Artifact Reference", TableHeader)],
        ["Track 2.1 Upfront Fare Model", "Trained & Validated (R²=0.7633, MAE=$4.47)", "models/fare_prediction_model.pkl"],
        ["Track 2.2 Trip Duration Model", "Trained & Validated (R²=0.8318, MAE=3.48m)", "models/duration_prediction_model.pkl"],
        ["Track 3.1 Demand Forecaster", "Trained & Validated (R²=0.9177, MAE=27.37/h)", "models/demand_forecasting_model.pkl"],
        ["Track 3.2 Spatial Clustering", "Trained & Validated (k=4 clusters)", "models/zone_clustering_model.pkl"],
        ["Submission Notebook", "Formatted with Team Branding", "code/Gravitons_FinalNotebook.ipynb"],
        ["Technical Report & Architecture", "Compiled PDF Specification", "Gravitons_Technical_Report.pdf"],
    ]
    story.append(make_table(summary_data, [4.8*cm, 5.2*cm, 5.3*cm], header_bg=TEAL))

    print("Compiling PDF...")
    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_later_pages)
    print(f"✅ Technical Report successfully built: {OUTPUT_PDF}")
    size_mb = os.path.getsize(OUTPUT_PDF) / (1024*1024)
    print(f"File Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    build()
