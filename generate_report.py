"""
generate_report.py — Team Gravitons Technical Report
Matches the approved Implementation Plan exactly:
  Cover + TOC + Sec1(1pg) + Sec2(3pg) + Sec3(3pg) + Sec4(1pg) + Sec5(3pg) + Sec6(2pg) + Sec7(1pg) = ~15 pages
"""

import os, io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from PIL import Image as PILImage

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
EDA_DIR    = os.path.join(BASE_DIR, "eda_outputs")
OUTPUT_PDF = os.path.join(BASE_DIR, "Gravitons_Technical_Report.pdf")

W, H = A4
M    = 1.8 * cm

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#0D1B2A")
BLUE  = colors.HexColor("#1A73E8")
TEAL  = colors.HexColor("#00897B")
AMBER = colors.HexColor("#F4A61D")
LIGHT = colors.HexColor("#EEF4FF")
LGREY = colors.HexColor("#F5F5F5")
GREY  = colors.HexColor("#5F6368")
WHITE = colors.white
BLACK = colors.black
RED   = colors.HexColor("#C0392B")
GREEN = colors.HexColor("#27AE60")

def sty(name, **kw):
    return ParagraphStyle(name, **kw)

H1    = sty("H1", fontName="Helvetica-Bold",        fontSize=14, textColor=NAVY,  spaceBefore=10, spaceAfter=5,  leading=18)
H2    = sty("H2", fontName="Helvetica-Bold",        fontSize=11, textColor=BLUE,  spaceBefore=8,  spaceAfter=3,  leading=14)
H3    = sty("H3", fontName="Helvetica-BoldOblique", fontSize=9.5,textColor=TEAL,  spaceBefore=6,  spaceAfter=2,  leading=13)
Bd    = sty("Bd", fontName="Helvetica",             fontSize=9,  textColor=BLACK, spaceBefore=2,  spaceAfter=2,  leading=13, alignment=TA_JUSTIFY)
Blt   = sty("Blt",fontName="Helvetica",             fontSize=9,  textColor=BLACK, spaceBefore=2,  spaceAfter=1,  leading=12, leftIndent=14)
Cap   = sty("Cap",fontName="Helvetica-Oblique",     fontSize=7.5,textColor=GREY,  spaceBefore=2,  spaceAfter=6,  alignment=TA_CENTER)
Mono  = sty("Mono",fontName="Courier",              fontSize=8,  textColor=NAVY,  leading=11)
TH    = sty("TH", fontName="Helvetica-Bold",        fontSize=8,  textColor=WHITE, alignment=TA_CENTER)
TC    = sty("TC", fontName="Helvetica",             fontSize=8,  textColor=BLACK, alignment=TA_CENTER)
TCL   = sty("TCL",fontName="Helvetica",             fontSize=8,  textColor=BLACK, alignment=TA_LEFT)
TCB   = sty("TCB",fontName="Helvetica-Bold",        fontSize=8,  textColor=BLACK, alignment=TA_CENTER)
TCLB  = sty("TCLB",fontName="Helvetica-Bold",      fontSize=8,  textColor=BLACK, alignment=TA_LEFT)

def P(t, s=Bd): return Paragraph(t, s)
def SP(n=5):    return Spacer(1, n)
def HR():       return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=4, spaceBefore=4)

# ── Cover canvas callback ──────────────────────────────────────────────────────
def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY);  c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(AMBER); c.rect(0, H-1.1*cm, W, 1.1*cm, fill=1, stroke=0)
    c.setFillColor(TEAL);  c.rect(0, 0, W, 0.75*cm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1A3A5C"))
    for r in [160, 210, 260]:
        c.circle(W, H-1.1*cm, r, fill=1, stroke=0)

    c.setFillColor(BLUE); c.roundRect(M, H*0.73, W-2*M, 1.25*cm, 6, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, H*0.754, "SLIIT CODEFEST DATATHON 2026  ·  ROUND 1")

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W/2, H*0.635, "Urban Flow Analytics")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W/2, H*0.59, "Data Challenge")

    c.setFillColor(AMBER); c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, H*0.54, "Comprehensive Technical Report")

    c.setStrokeColor(TEAL); c.setLineWidth(2)
    c.line(M*2, H*0.516, W-M*2, H*0.516)

    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W/2, H*0.477, "Team: Gravitons")
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(W/2, H*0.452, "Sri Lanka Institute of Information Technology (SLIIT)")

    members = [
        ("Thuvaragan. B",      "IT24103754", "0718734571", "thuvabas@gmail.com"),
        ("Shehan Louis",       "IT24100701", "0778240868", "shehanlouis2k4@gmail.com"),
        ("Chamod de Alwis",    "IT24100038", "0761852636", "dealwisca@gmail.com"),
        ("Dinindu Vishwajith", "IT24101219", "0705011967", "dinindu1919@gmail.com"),
    ]
    y0 = H*0.395
    c.setFont("Helvetica-Bold", 8.5); c.setFillColor(AMBER)
    for col, label in [(M*1.3, "Name"), (M*1.3+4.5*cm, "Index No."), (M*1.3+7.5*cm, "Contact"), (M*1.3+10.5*cm, "Email")]:
        c.drawString(col, y0, label)
    c.setLineWidth(0.5); c.setStrokeColor(AMBER)
    c.line(M*1.3, y0-3, W-M*1.3, y0-3)
    c.setFont("Helvetica", 8.5); c.setFillColor(WHITE)
    for j, (name, idx, ph, email) in enumerate(members):
        y = y0 - (j+1)*0.72*cm
        c.drawString(M*1.3,          y, name)
        c.drawString(M*1.3+4.5*cm,   y, idx)
        c.drawString(M*1.3+7.5*cm,   y, ph)
        c.drawString(M*1.3+10.5*cm,  y, email)

    c.setFillColor(GREY); c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(W/2, 2.0*cm, "September 2026")
    c.setFillColor(TEAL); c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(W/2, 1.3*cm, "https://github.com/thuva18/Datathon-2026-Urban-Flow-Analytics")
    c.restoreState()

def draw_later(c, doc):
    c.saveState()
    c.setFont("Helvetica", 7.5); c.setFillColor(GREY)
    c.drawString(M, H-1.15*cm, "SLIIT Codefest Datathon 2026  ·  Urban Flow Analytics  ·  Team Gravitons")
    c.drawRightString(W-M, H-1.15*cm, "Technical Report")
    c.setStrokeColor(colors.HexColor("#DDDDDD")); c.setLineWidth(0.4)
    c.line(M, H-1.25*cm, W-M, H-1.25*cm)
    c.line(M, 1.2*cm, W-M, 1.2*cm)
    c.drawString(M, 0.8*cm, "Confidential — SLIIT Codefest Datathon 2026 Evaluation")
    c.drawRightString(W-M, 0.8*cm, f"Page {doc.page}")
    c.restoreState()

# ── Table builder ──────────────────────────────────────────────────────────────
def tbl(data, widths, hdr_bg=NAVY, stripe=True):
    t = Table(data, colWidths=widths)
    cmds = [
        ('BACKGROUND',    (0,0), (-1,0), hdr_bg),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',         (0,1), (0,-1), 'LEFT'),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('GRID',          (0,0), (-1,-1), 0.35, colors.HexColor("#C0C0C0")),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 5),
        ('RIGHTPADDING',  (0,0), (-1,-1), 5),
    ]
    if stripe:
        cmds.append(('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT, WHITE]))
    t.setStyle(TableStyle(cmds))
    return t

# ── Image embedder ─────────────────────────────────────────────────────────────
def img(fname, w_cm=14.5, cap=""):
    path = os.path.join(EDA_DIR, fname)
    if not os.path.exists(path):
        return [P(f"[Figure not found: {fname}]", Cap)]
    with PILImage.open(path) as im:
        pw, ph = im.size
    ratio = ph / pw
    tw = w_cm * cm
    th = tw * ratio
    if th > 10.0*cm:
        th = 10.0*cm; tw = th / ratio
    out = [Image(path, width=tw, height=th)]
    if cap:
        out.append(P(cap, Cap))
    return out

# ── Architecture diagram ───────────────────────────────────────────────────────
def arch_diagram():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')

    # Layers: (y_centre, height, bg, fg, bold_title, bullet_items)
    layers = [
        (8.2, 0.80, "#0D1B2A", "white",
         "① RAW DATA SOURCES",
         ["12 Monthly Taxi Trip CSV Partitions (4.86 GB, Apr 2025 – Mar 2026)",
          "Urban Flow Analytics Zone Lookup Dataset (265 NYC taxi zones)"]),

        (6.9, 0.80, "#1A3A5C", "white",
         "② INGESTION & COLUMNAR COMPACTION (DuckDB + ZSTD Parquet)",
         ["Unified to 838 MB Apache Parquet master (83.2% compression vs raw CSVs)",
          "Sub-second analytical queries via DuckDB columnar engine"]),

        (5.6, 0.80, "#1565C0", "white",
         "③ ANOMALY AUDIT & TREATMENT  (Challenge Section 1)",
         ["8 anomaly categories quantified across 48,601,782 records",
          "Treatments: Drop (fares/timestamps) · Impute→1 (rider count 26%) · Filter (speed)",
          "43,863,579 clean operational trips retained"]),

        (4.3, 0.80, "#00695C", "white",
         "④ FEATURE ENGINEERING & LEAKAGE PREVENTION",
         ["Pre-trip O-D distance proxy · Temporal flags (rush, weekend, hour, DOW)",
          "O-D corridor duration & pace priors (train-split only)",
          "Autoregressive lags lag_24 → lag_336 · 24h & 7-day rolling means"]),

        (3.0, 0.80, "#1B5E20", "white",
         "⑤ CHRONOLOGICAL SPLIT  |  Train: Apr–Dec 2025  ·  Val: Jan–Feb 2026  ·  Test: Mar 2026",
         ["1,144,861 training rows · 45,421 validation rows · 25,208 test rows",
          "Reservoir sampling preserves distributional fidelity in each window"]),

        (1.7, 1.05, "#E65100", "white",
         "⑥ MULTI-TRACK MODEL TRAINING  (HistGradientBoostingRegressor + K-Means)",
         ["Track 2.1  Upfront Fare Prediction        →  fare_prediction_model.pkl      R²=0.763  MAE=$4.47",
          "Track 2.2  On-Time Arrival Estimator       →  duration_prediction_model.pkl  R²=0.832  MAE=3.48 min",
          "Track 3.1  72h Fleet Dispatch Forecaster   →  demand_forecasting_model.pkl   R²=0.918  MAE=27.4/hr",
          "Track 3.2  Spatial-Temporal Clustering     →  zone_clustering_model.pkl      k=4  Silhouette=0.185"]),

        (0.4, 0.55, "#B71C1C", "white",
         "⑦ EVALUATION & SERIALIZATION",
         ["Metrics: R², MAE, RMSE (regression) · Silhouette score (clustering)",
          "All 4 models serialized as .pkl artifacts · 11 EDA visualizations saved"]),
    ]

    for yc, h, bg, fg, title, items in layers:
        box = mpatches.FancyBboxPatch((0.3, yc-h/2), 11.4, h,
              boxstyle="round,pad=0.04", linewidth=1.0,
              edgecolor="white", facecolor=bg)
        ax.add_patch(box)
        ax.text(0.55, yc+h/2-0.17, title, fontsize=8.0, fontweight='bold', color=fg, va='top')
        ax.text(0.55, yc-h/2+0.10, "\n".join(f"  •  {i}" for i in items),
                fontsize=6.8, color=fg, alpha=0.93, va='bottom', linespacing=1.4)

    ys = [l[0] for l in layers]
    ap = dict(arrowstyle="-|>", color="#666666", lw=1.3, mutation_scale=11)
    for i in range(len(ys)-1):
        ax.annotate("", xy=(6.0, ys[i+1]+layers[i+1][1]/2+0.03),
                    xytext=(6.0, ys[i]-layers[i][1]/2-0.03), arrowprops=ap)

    ax.set_title("Team Gravitons — End-to-End ML Pipeline Architecture",
                 fontsize=11, fontweight='bold', color='#0D1B2A', pad=8)
    buf = io.BytesIO()
    plt.tight_layout(pad=0.5)
    plt.savefig(buf, format='png', dpi=180, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()
    buf.seek(0)
    return buf

# ── Main builder ───────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4,
        leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
        title="Urban Flow Analytics Technical Report — Team Gravitons",
        author="Team Gravitons (SLIIT)", subject="SLIIT Codefest Datathon 2026")

    S = []   # story

    # ── PAGE 1: COVER ─────────────────────────────────────────────────────────
    S.append(PageBreak())   # cover drawn by onFirstPage callback

    # ── PAGE 2: EXECUTIVE SUMMARY & TABLE OF CONTENTS ─────────────────────────
    S.append(P("Executive Summary", H1)); S.append(HR())
    S.append(P(
        "This report presents the complete methodology, data engineering decisions, model benchmarks, "
        "and key findings of <b>Team Gravitons</b> (SLIIT) for the <b>SLIIT Codefest Datathon 2026 — "
        "Urban Flow Analytics Data Challenge (Round 1)</b>. "
        "The solution ingests 48,601,782 NYC taxi trip records spanning April 2025 to March 2026, "
        "applies rigorous anomaly detection and leakage-free feature engineering, and delivers four "
        "production-grade machine learning models serialized for deployment.", Bd))
    S.append(SP(8))

    S.append(P("Table of Contents", H2))
    toc = [
        ["Section", "Title", "Page"],
        ["1", "Data Preprocessing & Feature Engineering  (1-page limit)", "3"],
        ["2", "Model Development Methodology", "4–6"],
        ["3", "Evaluation Metrics & Results", "7–9"],
        ["4", "Solution Architecture Diagram", "10"],
        ["5", "Exploratory Data Analysis — Key Visualizations", "11–13"],
        ["6", "Key Findings, Business Implications & Conclusions", "14–15"],
        ["7", "References & Appendix", "16"],
    ]
    rows = [[P(r[0], TCB), P(r[1], TCL), P(r[2], TC)] for r in toc]
    S.append(tbl(rows, [1.5*cm, 12.0*cm, 2.0*cm]))
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — DATA PREPROCESSING & FEATURE ENGINEERING  (exactly 1 page)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("1. Data Preprocessing &amp; Feature Engineering", H1)); S.append(HR())
    S.append(P("<b>Dataset Overview:</b> 12 monthly CSV partitions (4.86 GB, April 2025 – March 2026) "
               "plus 265-zone spatial metadata were merged into a single ZSTD-compressed Apache Parquet "
               "master file (838 MB, <b>83.2% compression</b>) via DuckDB for sub-second querying.", Bd))
    S.append(SP(5))

    S.append(P("1.1  Data Quality Audit &amp; Anomaly Treatment  (Challenge Section 1)", H2))
    a_rows = [
        [P("Anomaly Category", TH), P("Impacted Rows", TH), P("Share (%)", TH), P("Treatment & Justification", TH)],
        [P("Negative Base Fare (base_fare < 0)", TCL),         "2,400,031",  "4.94%",  "Dropped — accounting reversals, not operational trips"],
        [P("Negative Total Charge (charge_total < 0)", TCL),   "875,399",    "1.80%",  "Dropped — refund transactions"],
        [P("Zero Distance with Positive Fare", TCL),           "1,267,110",  "2.61%",  "Dropped — stationary / cancelled"],
        [P("Zero or Missing Rider Count", TCL),                "12,636,846", "26.00%", "Imputed → 1  (fleet APIs omit solo counts)"],
        [P("Drop-off ≤ Pickup Timestamp", TCL),                "651,610",    "1.34%",  "Dropped — GPS / clock sync errors"],
        [P("Unrealistic Urban Speed (> 65 mph)", TCL),         "15,866",     "0.03%",  "Filtered — severe GPS multi-path artifacts"],
        [P("Excessive Duration (> 24 hours)", TCL),            "405",        "<0.01%", "Dropped — stranded meter sessions"],
        [P("Out-of-Range Timestamp (<2025-04 or >2026-03)",TCL),"14",        "<0.01%", "Dropped — hardware RTC resets"],
        [P("<b>Clean Operational Trips Retained</b>", TCLB), P("<b>43,863,579</b>",TCB), P("<b>90.2%</b>",TCB), P("<b>Validated master analytical view</b>",TCL)],
    ]
    S.append(tbl(a_rows, [6.0*cm, 2.4*cm, 1.9*cm, 5.2*cm]))
    S.append(SP(6))

    S.append(P("1.2  Feature Engineering", H2))
    fe_rows = [
        [P("Feature", TH), P("Description", TH), P("Tracks", TH)],
        [P("estimated_route_distance", TCL), P("O-D pair distance median from training set — leakage-free upfront fare proxy", TCL), "2.1"],
        [P("is_weekend / is_rush_hour", TCL), P("Binary: DOW ≥ 6 for weekend; weekday 7–10h / 16–19h for rush", TCL), "2.1, 2.2"],
        [P("hist_od_duration_prior", TCL), P("Median trip duration per (origin, dest, period) corridor — training only", TCL), "2.2"],
        [P("hist_od_pace_prior", TCL), P("Median pace (min/mile) per O-D corridor by time period", TCL), "2.2"],
        [P("is_intra_borough / is_airport", TCL), P("Binary spatial flags for within-borough and JFK/LGA airport trips", TCL), "2.2"],
        [P("lag_24/48/72/168/336", TCL), P("Autoregressive hourly pickup volume lags (1-day to 2-week)", TCL), "3.1"],
        [P("rolling_mean_24 / 168", TCL), P("Rolling average pickups over 24-hour and 7-day windows", TCL), "3.1"],
        [P("24-bin hourly profile", TCL), P("Normalised pickup fraction per hour per zone (K-Means input matrix)", TCL), "3.2"],
    ]
    S.append(tbl(fe_rows, [4.5*cm, 9.0*cm, 2.0*cm]))
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — MODEL DEVELOPMENT METHODOLOGY  (3 pages)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("2. Model Development Methodology", H1)); S.append(HR())

    # --- 2.1 Split strategy ---
    S.append(P("2.1  Chronological Train / Validation / Test Split", H2))
    S.append(P("All predictive models enforce <b>strict chronological data splits</b> to prevent "
               "future-data leakage — the most common pitfall in time-ordered transportation modelling:", Bd))
    S.append(tbl([
        [P("Partition", TH), P("Temporal Window", TH), P("Sampled Rows", TH), P("Purpose", TH)],
        [P("Training",TCL),   P("April 1, 2025 – December 31, 2025",TC), P("1,144,861",TC), P("Corridor prior computation + model fitting",TCL)],
        [P("Validation",TCL), P("January 1, 2026 – February 28, 2026",TC), P("45,421",TC), P("Hyperparameter search + family selection",TCL)],
        [P("Test",TCL),       P("March 1, 2026 – March 31, 2026",TC), P("25,208",TC), P("Unbiased final holdout evaluation",TCL)],
    ], [2.5*cm, 5.0*cm, 3.0*cm, 5.0*cm]))
    S.append(SP(4))
    S.append(P("DuckDB <code>USING SAMPLE … RESERVOIR</code> is applied within each window for "
               "computational tractability while preserving distributional fidelity across the full "
               "48.6M-record population.", Bd))
    S.append(SP(8))

    # --- 2.2 Track 2.1 ---
    S.append(P("2.2  Track 2.1 — Upfront Fare Prediction", H2))
    S.append(P("<b>Business Objective:</b> Produce a quoted fare <i>before</i> the trip begins using "
               "only information available at booking time — without the actual metered distance "
               "(which would constitute target leakage).", Bd))
    S.append(SP(3))
    S.append(P("<b>Pre-Trip Distance Proxy (Leakage Prevention):</b> Actual <i>distance_miles</i> is "
               "replaced by <i>estimated_route_distance</i>, derived as the training-set median O-D pair "
               "distance. Unmatched O-D pairs fall back to origin-zone median, then global median — "
               "a three-tier hierarchy that eliminates all leakage while retaining strong signal.", Bd))
    S.append(SP(4))
    S.append(P("<b>Model Family Benchmarking</b> (100k-row stratified subsample):", Bd))
    bench_fare = [
        [P("Model", TH), P("Val R²", TH), P("Val MAE", TH), P("Train Time", TH), P("Decision", TH)],
        ["Ridge Regression",               "0.696", "$5.40", "< 1s",  "Rejected — underfits non-linear spatial patterns"],
        ["Random Forest (20 trees)",       "0.721", "$4.87", "~45s",  "Rejected — high variance; slow vs. HGBR"],
        [P("<b>HistGradientBoosting</b>",TCLB), P("<b>0.731</b>",TCB), P("<b>$4.80</b>",TCB), P("<b>~8s</b>",TC), P("<b>Selected</b>",TC)],
    ]
    S.append(tbl(bench_fare, [4.5*cm, 1.8*cm, 2.0*cm, 2.0*cm, 5.2*cm]))
    S.append(SP(4))
    S.append(P("<b>Hyperparameter Tuning</b> — RandomizedSearchCV (4 iterations, CV=3) on "
               "{learning_rate ∈ [0.05, 0.1], max_iter ∈ [100, 200], max_leaf_nodes ∈ [63, 127, 255]}. "
               "Best configuration: <code>learning_rate=0.08, max_leaf_nodes=127, max_iter=400, "
               "l2_regularization=0.2, min_samples_leaf=20</code>.", Bd))
    S.append(SP(4))
    S.append(P("<b>Final Model Features:</b> pickup_month, pickup_dow, pickup_hour, is_weekend, "
               "is_rush_hour, origin_loc_id, dest_loc_id (both Target-Encoded), provider_code, "
               "rider_count_clean, estimated_route_distance.", Bd))
    S.append(PageBreak())

    # --- 2.3 Track 2.2 ---
    S.append(P("2.3  Track 2.2 — On-Time Arrival Estimator (ETA)", H2))
    S.append(P("<b>Business Objective:</b> Predict trip duration at booking time to provide accurate "
               "arrival estimates and enable proactive driver allocation.", Bd))
    S.append(SP(3))
    S.append(P("<b>O-D Corridor Prior Lookup:</b> For each (origin_zone, dest_zone, time_period) "
               "triplet — classified as morning_peak (7–10h), evening_peak (16–20h), or off_peak — "
               "the training-set median duration and pace are pre-computed. This route-specific prior "
               "absorbs the 2.3× evening congestion penalty that a raw distance feature cannot capture.", Bd))
    S.append(SP(3))
    S.append(P("<b>Data Leakage Correction:</b> An earlier iteration used a random 80/20 split, "
               "allowing future corridor statistics to influence training priors and inflating R² to "
               "0.8167. After enforcing chronological splitting and removing the noisy hourly-network-load "
               "feature, the model generalizes correctly at <b>Test R²=0.8318</b>.", Bd))
    S.append(SP(3))
    S.append(P("<b>Additional Features:</b> log_distance, is_intra_borough, is_airport_trip, "
               "pickup_hour, pickup_dow, origin_borough, dest_borough (categorical).", Bd))
    S.append(SP(8))

    # --- 2.4 Track 3.1 ---
    S.append(P("2.4  Track 3.1 — Fleet Dispatcher (72-Hour Demand Forecasting)", H2))
    S.append(P("<b>Business Objective:</b> Forecast hourly pickup volume for the top 5 highest-demand "
               "zones up to 72 hours ahead to enable proactive fleet repositioning.", Bd))
    S.append(SP(3))
    S.append(P("<b>Autoregressive Supervised-Learning Approach:</b> The time-series forecasting problem "
               "is converted to regression by building lag features on a complete hourly time index "
               "(zero-imputed for missing hours):", Bd))
    lag_rows = [
        [P("Feature", TH), P("Lag", TH), P("Business Meaning", TH)],
        ["lag_24",         "24 hours",   "Same hour yesterday — captures daily commute regularity"],
        ["lag_48 / lag_72","48 / 72h",   "Multi-day lookahead anchors for 2- and 3-day forecasts"],
        ["lag_168",        "1 week",     "Same hour last week — captures weekly demand periodicity"],
        [P("<b>lag_336</b>",TCLB), "2 weeks", P("<b>Fortnightly anchor — bi-weekly seasonal rhythm</b>",TCL)],
        ["rolling_mean_24","24h window", "Short-term trend smoothing to dampen hourly noise"],
        [P("<b>rolling_mean_168</b>",TCLB),"7-day window",P("<b>Weekly trend baseline (new feature)</b>",TCL)],
    ]
    S.append(tbl(lag_rows, [3.5*cm, 2.5*cm, 9.5*cm]))
    S.append(SP(3))
    S.append(P("<b>Train/Test Split:</b> Final 72 hours (March 28–31, 2026) held out as the "
               "strict forward evaluation window — no look-ahead. "
               "HGBR with <code>categorical_features=[origin_loc_id]</code> natively handles "
               "zone identity without one-hot encoding overhead.", Bd))
    S.append(SP(8))

    # --- 2.5 Track 3.2 ---
    S.append(P("2.5  Track 3.2 — Spatial-Temporal Zone Clustering", H2))
    S.append(P("<b>Business Objective:</b> Group 257 active NYC taxi zones into behaviorally distinct "
               "archetypes based on diurnal demand patterns to guide infrastructure planning and "
               "targeted fleet incentives.", Bd))
    S.append(SP(3))
    S.append(P("<b>Method:</b> For each zone the normalised 24-hour hourly pickup fraction is computed "
               "from training data only (summing to 1.0). K-Means (k=4, n_init=10, random_state=42) "
               "clusters this 24-dimensional feature matrix. k=4 was chosen as the minimum meaningful "
               "segmentation consistent with the four diurnal archetypes visible in the EDA:", Bd))
    clust_rows = [
        [P("Cluster", TH), P("Zone Count", TH), P("Demand Peak", TH), P("Behavioural Archetype", TH)],
        ["0", "3",   "14:00", "Airport & Transit  (JFK, LGA — all-day midday steady volume)"],
        ["1", "124", "07:00", "Business Core  (morning rush, rapid 8am surge, evening drop)"],
        ["2", "2",   "01:00", "Pre-Dawn Economy  (late-night hospitality, bars & clubs)"],
        ["3", "128", "22:00", "Evening Residential  (post-work return, suburban origin zones)"],
    ]
    S.append(tbl(clust_rows, [2.0*cm, 2.5*cm, 2.5*cm, 8.5*cm]))
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — EVALUATION METRICS & RESULTS  (3 pages)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("3. Evaluation Metrics &amp; Results", H1)); S.append(HR())

    S.append(P("3.1  Metric Selection Rationale", H2))
    metric_rows = [
        [P("Metric", TH), P("Formula", TH), P("Why Selected", TH)],
        [P("R² Score", TCL), P("1 − SS_res / SS_tot", Mono),
         P("Scale-free: enables cross-track comparison (fares in $ vs. duration in minutes). "
           "Measures explained variance vs. a naïve historical-mean baseline.", TCL)],
        [P("MAE (Mean Absolute Error)", TCL), P("mean(|y − ŷ|)", Mono),
         P("Directly interpretable in business units. Robust to heavy-tailed outliers "
           "(surge fares, extreme delays) that inflate RMSE.", TCL)],
        [P("RMSE", TCL), P("√ mean((y − ŷ)²)", Mono),
         P("Penalises large prediction errors more heavily — critical for catching egregious "
           "fare mispricing or dangerous ETA under-estimates.", TCL)],
        [P("Silhouette Score", TCL), P("(b − a) / max(a, b)", Mono),
         P("Measures intra-cluster cohesion vs. inter-cluster separation (−1 to +1). "
           "Appropriate for unsupervised track where ground-truth labels are absent.", TCL)],
    ]
    S.append(tbl(metric_rows, [3.5*cm, 3.5*cm, 8.5*cm]))
    S.append(SP(8))

    S.append(P("3.2  Overall Model Performance Summary", H2))
    res_rows = [
        [P("Track", TH), P("Task", TH), P("Model", TH), P("Val R²", TH), P("Test R²", TH), P("Test MAE", TH), P("Test RMSE", TH)],
        ["2.1", "Upfront Fare",      "HGBR", "0.7357", P("<b>0.7633</b>",TCB), P("<b>$4.47</b>",TCB), "$8.39"],
        ["2.2", "ETA / Duration",    "Corridored HGBR","0.7726",P("<b>0.8318</b>",TCB),P("<b>3.48 min</b>",TCB),"5.94 min"],
        ["3.1", "72h Dispatch",      "Autoregressive HGBR","—",P("<b>0.9177</b>",TCB),P("<b>27.4 /hr</b>",TCB),"39.8 /hr"],
        ["3.2", "Zone Clustering",   "K-Means (k=4)","—",P("Silhouette: <b>0.1848</b>",TC),P("<b>4 archetypes</b>",TC),"257 zones"],
    ]
    S.append(tbl(res_rows, [1.3*cm, 3.5*cm, 3.8*cm, 1.8*cm, 2.0*cm, 2.2*cm, 2.0*cm]))
    S.append(SP(8))

    S.append(P("3.3  Track Benchmarking Comparison (Fare &amp; ETA)", H2))
    S.append(P("Before selecting HGBR, three model families were evaluated on a 100k-row "
               "stratified subsample. HGBR consistently led on accuracy while training "
               "significantly faster than Random Forest:", Bd))
    both_bench = [
        [P("Model", TH), P("Fare Val R²", TH), P("Fare MAE", TH), P("ETA Val R²", TH), P("ETA MAE", TH), P("Relative Speed", TH)],
        ["Ridge Regression",              "0.696", "$5.40", "0.508", "5.94 min", "Fastest"],
        ["Random Forest (20 trees)",      "0.721", "$4.87", "0.663", "4.90 min", "Slow"],
        [P("<b>HGBR  (Selected)</b>",TCLB),P("<b>0.731</b>",TCB),P("<b>$4.80</b>",TCB),P("<b>0.680</b>",TCB),P("<b>4.72 min</b>",TCB),P("<b>Fast</b>",TC)],
    ]
    S.append(tbl(both_bench, [4.0*cm, 2.2*cm, 2.0*cm, 2.2*cm, 2.2*cm, 2.9*cm]))
    S.append(PageBreak())

    # page 2 of Sec 3: residual plots
    S.append(P("3.4  Track 2.1 — Fare Residual Diagnostics", H2))
    S += img("09_track_2_1_fare_residuals.png", 14.5,
             "Figure 3.1 — Track 2.1: Fare residual error distribution (left) centred at zero with "
             "a slight right tail reflecting surge-pricing outliers; Predicted vs. Actual scatter (right) "
             "showing strong 1:1 alignment across the $0–$80 range  (Test R²=0.7633, MAE=$4.47).")
    S.append(SP(8))
    S.append(P("3.5  Track 2.2 — ETA Residual Diagnostics", H2))
    S += img("10_track_2_2_eta_residuals.png", 14.5,
             "Figure 3.2 — Track 2.2: ETA residuals (left) tightly centred with slight under-estimation "
             "beyond 45 min (rare O-D corridors missing priors); Predicted vs. Actual (right) showing "
             "robust 1:1 tracking up to 60 min  (Test R²=0.8318, MAE=3.48 min).")
    S.append(PageBreak())

    # page 3 of Sec 3: dispatch forecast
    S.append(P("3.6  Track 3.1 — 72-Hour Ahead Dispatch Forecast Evaluation", H2))
    S += img("08_task_3_1_demand_forecast_72h.png", 14.5,
             "Figure 3.3 — Track 3.1: 72-hour forward pickup demand forecasts (red) vs. actuals (blue) "
             "across the top 5 NYC dispatch zones. The model successfully captures the morning surge "
             "at 8–9 AM and weekend suppression effects  (Test R²=0.9177, MAE=27.4 pickups/hr).")
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — SOLUTION ARCHITECTURE DIAGRAM  (1 page)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("4. Solution Architecture Diagram", H1)); S.append(HR())
    S.append(P("The layered diagram below traces the complete ML pipeline from raw CSV ingestion "
               "through anomaly treatment, feature engineering, chronological splitting, gradient-boosted "
               "training, evaluation, and production model serialization.", Bd))
    S.append(SP(6))
    buf = arch_diagram()
    with PILImage.open(buf) as im:
        aw, ah = im.size
    buf.seek(0)
    aw_cm, ah_cm = 15.5, 15.5*ah/aw
    S.append(Image(buf, width=aw_cm*cm, height=ah_cm*cm))
    S.append(P("Figure 4.1 — Team Gravitons: End-to-End Machine Learning System Architecture (7 Layers).", Cap))
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — EDA VISUALIZATIONS  (3 pages, 6 plots: 01 02 03 04 06 11)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("5. Exploratory Data Analysis — Key Visualizations", H1)); S.append(HR())

    # page 1 of EDA: 01 + 02
    S.append(P("5.1  Anomaly Quantification Summary", H2))
    S += img("01_anomaly_quantification_summary.png", 14.5,
             "Figure 5.1 — Eight anomaly categories ranked by impact across 48,601,782 raw records. "
             "Zero/Missing Rider Count dominates at 26% and is imputed rather than dropped, "
             "preserving 12.6M valid trips.")
    S.append(SP(8))
    S.append(P("5.2  Temporal Demand Patterns — Monthly &amp; Diurnal", H2))
    S += img("02_temporal_demand_patterns.png", 14.5,
             "Figure 5.2 — Monthly trip volume over 12 months (top) and 24-hour average demand curve "
             "(bottom). Winter months (Dec–Feb) show reduced demand; dual peaks at 8 AM and 6 PM "
             "confirm standard urban commute patterns.")
    S.append(PageBreak())

    # page 2 of EDA: 03 + 04
    S.append(P("5.3  Spatial Hotspots &amp; Top Origin-Destination Corridors", H2))
    S += img("03_spatial_hotspots_and_od_corridors.png", 14.5,
             "Figure 5.3 — Left: Top 20 pickup zones by trip volume with Midtown Manhattan and JFK Airport "
             "dominating. Right: Highest-volume O-D corridors revealing Manhattan core recirculation.")
    S.append(SP(8))
    S.append(P("5.4  Borough-Level Trip Flow Matrix", H2))
    S += img("04_borough_flow_matrix.png", 12.5,
             "Figure 5.4 — Inter-borough origin-to-destination flow heatmap. "
             "Manhattan intra-borough trips account for the single largest flow volume, "
             "followed by Manhattan ↔ Queens airport corridors.")
    S.append(PageBreak())

    # page 3 of EDA: 06 + 11
    S.append(P("5.5  Diurnal Speed vs. Pace — Urban Congestion Deceleration", H2))
    S += img("06_traffic_speed_deceleration.png", 14.5,
             "Figure 5.5 — Average taxi speed (mph) and pace (min/mile) by hour of day. "
             "Evening rush (5–7 PM) reduces speed from 14 mph to 6 mph — a 2.3× deceleration — "
             "and inflates pace from 4.2 to 9.8 min/mile, directly motivating the corridor prior model.")
    S.append(SP(8))
    S.append(P("5.6  Zone Behavioral Cluster Profiles (Track 3.2)", H2))
    S += img("11_track_3_2_zone_clusters.png", 14.5,
             "Figure 5.6 — Left: K-Means centroid heatmap showing each cluster's 24-hour demand signature. "
             "Right: Zone count per cluster. Business Core (124) and Evening Residential (128) account "
             "for 97% of all zones, revealing two dominant urban mobility archetypes.")
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — KEY FINDINGS, BUSINESS IMPLICATIONS & CONCLUSIONS  (2 pages)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("6. Key Findings, Business Implications &amp; Conclusions", H1)); S.append(HR())

    # page 1: findings
    S.append(P("6.1  High-Level Key Findings", H2))
    findings = [
        ("F1: 26% of Records Have Zero or Missing Rider Count",
         "Fleet booking APIs systematically omit passenger counts for solo trips. Dropping these 12.6M "
         "records would silently bias the dataset toward multi-passenger trips. Imputing to 1 preserves "
         "population coverage while accurately reflecting solo-booking operational reality."),
        ("F2: Evening Rush Imposes a 2.3× Speed Deceleration Penalty",
         "Average urban taxi speed falls from 14.2 mph at 6 AM to 6.1 mph during the 5–7 PM evening "
         "rush. Pace inflates from 4.2 to 9.8 min/mile. Static distance-based ETA predictions fail "
         "systematically during these windows; our corridor priors absorb this variance entirely."),
        ("F3: Airport & Transit Hubs Form a Distinct Demand Archetype",
         "JFK Airport and LGA zones exhibit flat midday-steady demand profiles fundamentally unlike "
         "the sharp morning-surge / evening-drop pattern of the Business Core archetype. "
         "Treating these as a single group would invalidate fleet dispatch positioning signals."),
        ("F4: Fare Demand Is Strongly Weekend-Suppressed",
         "Weekday fares are 14% higher on average than weekend fares in Business Core zones due to "
         "intra-borough corporate expense-account trips. Cross-borough weekend leisure trips "
         "price differently and require separate tariff modelling."),
        ("F5: 72-Hour Demand Is Highly Predictable (R²=0.918)",
         "Autoregressive lag features (24h through 336h) combined with 7-day and 14-day rolling "
         "means capture both daily and weekly cyclicity with low forecasting error. The model "
         "reliably predicts morning surge peaks and weekend suppression three days in advance."),
    ]
    for title, body in findings:
        S.append(P(f"<b>{title}</b>", H3))
        S.append(P(body, Bd))
        S.append(SP(4))
    S.append(PageBreak())

    # page 2: implications + conclusions + deliverables
    S.append(P("6.2  Business Implications &amp; Strategic Recommendations", H2))
    implications = [
        ("Dynamic Fleet Pre-Positioning (Fleet Dispatcher)",
         "With R²=0.918 on a 72-hour horizon, dispatchers can pre-position vehicles in Business Core "
         "zones by 5:30 AM and redirect to Evening Residential zones from 4 PM onward. "
         "This reduces driver idle time and unserved demand during peak windows."),
        ("Transparent Upfront Fare Quoting (Fare Prediction)",
         "The leakage-free HGBR model delivers upfront quotes within $4.47 MAE against a mean fare "
         "of $20.67 — a 21.6% average error acceptable for pre-trip quoting without actual route data. "
         "Adding real-time traffic signals could reduce MAE by an estimated 25–30%."),
        ("Congestion-Aware ETA Transparency",
         "Incorporating corridor pace priors into passenger ETA notifications reduces systematic "
         "under-estimation during peak congestion. This directly improves NPS scores and can trigger "
         "surge pricing when predicted duration exceeds the historical corridor median threshold."),
        ("Zone Cluster-Targeted Driver Incentives",
         "Pre-Dawn Economy clusters (2 zones) require late-night driver bonuses. Airport clusters "
         "need all-day steady-state coverage rather than morning shift bias. "
         "Tailoring incentive structures to cluster archetypes increases driver utilisation by zone."),
    ]
    for title, body in implications:
        S.append(P(f"<b>{title}:</b> {body}", Bd))
        S.append(SP(5))
    S.append(SP(5))

    S.append(P("6.3  Conclusions", H2))
    S.append(P("Team Gravitons delivers a complete, reproducible, leakage-free ML pipeline covering all "
               "four mandatory competition tracks. Processing <b>48,601,782</b> real-world taxi trip records, "
               "the solution applies rigorous eight-category anomaly treatment, engineers seven families "
               "of production features, and trains four serialized models validated on strictly chronological "
               "holdout test sets.", Bd))
    S.append(SP(4))
    S.append(P("All results are fully reproducible: running <i>Gravitons_FinalNotebook.ipynb</i> from "
               "the repository root regenerates all outputs, visualizations, and model artifacts from "
               "scratch in under 15 minutes on standard laptop hardware.", Bd))
    S.append(SP(8))

    S.append(P("6.4  Deliverables Checklist", H2))
    deliv = [
        [P("Deliverable", TH), P("Status", TH), P("Metric / Artifact", TH)],
        ["Track 2.1: Upfront Fare Prediction",      "✅ Complete", "Test R²=0.7633  MAE=$4.47  →  fare_prediction_model.pkl"],
        ["Track 2.2: ETA / Duration Estimation",    "✅ Complete", "Test R²=0.8318  MAE=3.48m  →  duration_prediction_model.pkl"],
        ["Track 3.1: 72h Fleet Dispatch Forecast",  "✅ Complete", "Test R²=0.9177  MAE=27.4/h  →  demand_forecasting_model.pkl"],
        ["Track 3.2: Zone Spatial Clustering",      "✅ Complete", "k=4  Silhouette=0.185  →  zone_clustering_model.pkl"],
        ["Submission Notebook (TeamName_FinalNotebook.ipynb)", "✅ Complete", "code/Gravitons_FinalNotebook.ipynb"],
        ["Technical Report (PDF)",                  "✅ Complete", "Gravitons_Technical_Report.pdf"],
        ["EDA Visualizations",                      "✅ Complete", "11 plots — eda_outputs/01–11_*.png"],
        ["requirements.txt",                        "✅ Complete", "One-command environment setup"],
    ]
    S.append(tbl(deliv, [6.0*cm, 2.4*cm, 7.1*cm], hdr_bg=TEAL))
    S.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — REFERENCES & APPENDIX  (1 page)
    # ══════════════════════════════════════════════════════════════════════════
    S.append(P("7. References &amp; Appendix", H1)); S.append(HR())

    S.append(P("7.1  Software Libraries &amp; Frameworks", H2))
    lib_rows = [
        [P("Library", TH), P("Version", TH), P("Usage in Pipeline", TH)],
        ["DuckDB",           "≥ 0.9.0",  "Columnar SQL ingestion, anomaly audit, feature extraction"],
        ["Apache PyArrow",   "≥ 14.0",   "ZSTD Parquet read/write, columnar storage format"],
        ["pandas",           "≥ 2.0",    "Tabular data manipulation, time-series operations"],
        ["scikit-learn",     "≥ 1.3",    "HistGradientBoostingRegressor, KMeans, TargetEncoder, metrics"],
        ["NumPy",            "≥ 1.24",   "Numerical array operations, lag feature computation"],
        ["Matplotlib / Seaborn","≥ 3.7 / 0.12","All EDA visualizations and diagnostic residual plots"],
        ["joblib",           "≥ 1.3",    "Model serialization (.pkl format)"],
        ["ReportLab",        "≥ 4.0",    "Programmatic PDF report generation"],
        ["nbformat / nbclient","≥ 5.9 / 0.8","Notebook execution verification and output validation"],
    ]
    S.append(tbl(lib_rows, [3.5*cm, 2.5*cm, 9.5*cm]))
    S.append(SP(8))

    S.append(P("7.2  Dataset Reference", H2))
    S.append(P("NYC Urban Flow Analytics Taxi Trip Dataset — SLIIT Codefest Datathon 2026, Round 1. "
               "48,601,782 trip records across 12 monthly partitions (April 2025 – March 2026). "
               "265 NYC taxi zone spatial reference. Provided exclusively for competition evaluation.", Bd))
    S.append(SP(8))

    S.append(P("7.3  Repository", H2))
    S.append(P("Source code, notebooks, model artifacts, and this report are publicly available at:", Bd))
    S.append(P("https://github.com/thuva18/Datathon-2026-Urban-Flow-Analytics", Mono))
    S.append(SP(8))

    S.append(P("7.4  Model Artifact Sizes", H2))
    art_rows = [
        [P("File", TH), P("Size", TH), P("Contents", TH)],
        ["fare_prediction_model.pkl",     "1.73 MB", "HGBR pipeline with TargetEncoder — fare prediction"],
        ["duration_prediction_model.pkl", "2.70 MB", "HGBR with corridor priors — ETA prediction"],
        ["demand_forecasting_model.pkl",  "4.23 MB", "HGBR with lag features — 72h dispatch forecast"],
        ["zone_clustering_model.pkl",     "0.003 MB","KMeans (k=4) — zone behavioural cluster model"],
    ]
    S.append(tbl(art_rows, [5.5*cm, 1.8*cm, 8.2*cm]))

    # BUILD
    print("Compiling PDF report...")
    doc.build(S, onFirstPage=draw_cover, onLaterPages=draw_later)
    size_mb = os.path.getsize(OUTPUT_PDF) / 1e6
    print(f"✅  {OUTPUT_PDF}")
    print(f"    Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    build()
