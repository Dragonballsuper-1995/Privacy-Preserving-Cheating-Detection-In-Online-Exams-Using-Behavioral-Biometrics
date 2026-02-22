"""
Scoring Pipeline Visualization Generator
Generates publication-ready plots for the Cheating Detector project submission.

Usage:
    cd backend
    python -m docs.generate_scoring_plots     (or just run this file directly)

All plots are saved to docs/plots/
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np
import os

# ── Config ──────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color palette - professional dark theme
COLORS = {
    "bg": "#0f1117",
    "card": "#1a1d29",
    "accent1": "#6c5ce7",   # Purple
    "accent2": "#00cec9",   # Teal
    "accent3": "#fd79a8",   # Pink
    "accent4": "#fdcb6e",   # Gold
    "accent5": "#55efc4",   # Mint
    "accent6": "#74b9ff",   # Blue
    "text": "#e0e0e0",
    "text_dim": "#8a8a9a",
    "danger": "#ff6b6b",
    "warning": "#ffa502",
    "success": "#2ed573",
    "grid": "#2d2d3d",
}

PIE_COLORS = ["#6c5ce7", "#00cec9", "#fd79a8", "#fdcb6e", "#55efc4", "#74b9ff", "#e17055", "#a29bfe"]


def style_ax(ax, title="", xlabel="", ylabel=""):
    """Apply consistent dark styling to an axis."""
    ax.set_facecolor(COLORS["bg"])
    ax.tick_params(colors=COLORS["text"], labelsize=10)
    ax.xaxis.label.set_color(COLORS["text"])
    ax.yaxis.label.set_color(COLORS["text"])
    ax.title.set_color(COLORS["text"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["grid"])
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", color=COLORS["text"], pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✅ Saved: {path}")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 1 — Layer 1: Heuristic Fallback Weights (Bar Chart)
# ════════════════════════════════════════════════════════════════════════
def plot_heuristic_weights():
    labels = [
        "Paste Score\n(amplified)", "Focus Score\n(amplified)", "Hesitation Score\n(amplified)",
        "Typing Score", "Paste After\nBlur Ratio", "Text Score",
        "Paste-to-Typing\nRatio", "Burst\nDensity"
    ]
    weights = [0.30, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05]
    colors = PIE_COLORS[:len(labels)]

    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor=COLORS["bg"])
    style_ax(ax, "Layer 1 — Heuristic Fallback Score Weights", ylabel="Weight in Final Score")

    bars = ax.bar(labels, weights, color=colors, edgecolor="#ffffff22", linewidth=0.5, width=0.65)
    for bar, w in zip(bars, weights):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f"{w:.0%}", ha="center", va="bottom", fontsize=10,
                fontweight="bold", color=COLORS["text"])

    ax.set_ylim(0, 0.38)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.5, alpha=0.5)
    save(fig, "01_heuristic_weights.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 2 — Layer 1: Non-Linear Amplifier Function
# ════════════════════════════════════════════════════════════════════════
def plot_amplifier():
    x = np.linspace(0, 1, 500)

    def amplifier(s):
        if s >= 0.8: return 1.5
        elif s >= 0.6: return 1.2
        else: return 1.0

    amplified = np.array([s * amplifier(s) for s in x])
    linear = x.copy()

    fig, ax = plt.subplots(figsize=(8, 5.5), facecolor=COLORS["bg"])
    style_ax(ax, "Non-Linear Amplifier Function", xlabel="Raw Score", ylabel="Amplified Score")

    ax.plot(x, linear, "--", color=COLORS["text_dim"], linewidth=1.5, label="Linear (no boost)")
    ax.plot(x, amplified, color=COLORS["accent1"], linewidth=2.5, label="Amplified score")

    # Highlight zones
    ax.axvspan(0, 0.6, alpha=0.06, color=COLORS["success"], label="Normal (×1.0)")
    ax.axvspan(0.6, 0.8, alpha=0.10, color=COLORS["warning"], label="High (×1.2)")
    ax.axvspan(0.8, 1.0, alpha=0.14, color=COLORS["danger"], label="Extreme (×1.5)")

    # Annotations
    ax.annotate("×1.0", xy=(0.3, 0.3), fontsize=13, color=COLORS["success"],
                fontweight="bold", ha="center")
    ax.annotate("×1.2", xy=(0.7, 0.7 * 1.2 + 0.04), fontsize=13, color=COLORS["warning"],
                fontweight="bold", ha="center")
    ax.annotate("×1.5", xy=(0.9, 0.9 * 1.5 + 0.04), fontsize=13, color=COLORS["danger"],
                fontweight="bold", ha="center")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.6)
    ax.legend(loc="upper left", fontsize=9, facecolor=COLORS["card"],
              edgecolor=COLORS["grid"], labelcolor=COLORS["text"])
    ax.grid(color=COLORS["grid"], linewidth=0.4, alpha=0.5)
    save(fig, "02_amplifier_function.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 3 — Layer 1: Score Combination (Pie Chart)
# ════════════════════════════════════════════════════════════════════════
def plot_score_combination():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor=COLORS["bg"])

    # With Isolation Forest
    ax1 = axes[0]
    labels1 = ["Random Forest\n(60%)", "Isolation Forest\n(20%)", "Burst Bonus\n(20%)"]
    sizes1 = [60, 20, 20]
    colors1 = [COLORS["accent1"], COLORS["accent2"], COLORS["accent3"]]
    wedges1, texts1, autotexts1 = ax1.pie(
        sizes1, labels=labels1, colors=colors1, autopct="%1.0f%%",
        startangle=90, textprops={"color": COLORS["text"], "fontsize": 10},
        wedgeprops={"edgecolor": COLORS["bg"], "linewidth": 2},
        pctdistance=0.55
    )
    for t in autotexts1:
        t.set_fontweight("bold")
        t.set_fontsize(11)
    ax1.set_title("With Isolation Forest Model", fontsize=12,
                   fontweight="bold", color=COLORS["text"], pad=12)

    # Without Isolation Forest (current default)
    ax2 = axes[1]
    labels2 = ["Random Forest\n(80%)", "Burst Bonus\n(20%)"]
    sizes2 = [80, 20]
    colors2 = [COLORS["accent1"], COLORS["accent3"]]
    wedges2, texts2, autotexts2 = ax2.pie(
        sizes2, labels=labels2, colors=colors2, autopct="%1.0f%%",
        startangle=90, textprops={"color": COLORS["text"], "fontsize": 10},
        wedgeprops={"edgecolor": COLORS["bg"], "linewidth": 2},
        pctdistance=0.55
    )
    for t in autotexts2:
        t.set_fontweight("bold")
        t.set_fontsize(11)
    ax2.set_title("Without Isolation Forest (Default)", fontsize=12,
                   fontweight="bold", color=COLORS["text"], pad=12)

    fig.suptitle("Layer 1 — Score Combination Weights", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=1.02)
    fig.tight_layout()
    save(fig, "03_score_combination_pie.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 4 — Layer 1: Anomaly Thresholds
# ════════════════════════════════════════════════════════════════════════
def plot_anomaly_thresholds():
    metrics = ["Paste Score", "Focus Score", "Hesitation Score"]
    thresholds = [0.85, 0.70, 0.80]
    bar_colors = [COLORS["accent3"], COLORS["accent2"], COLORS["accent4"]]

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=COLORS["bg"])
    style_ax(ax, "Layer 1 — Single-Metric Anomaly Thresholds",
             xlabel="Threshold to Trigger Anomaly Flag", ylabel="")

    y_pos = np.arange(len(metrics))
    bars = ax.barh(y_pos, thresholds, color=bar_colors, height=0.45,
                   edgecolor="#ffffff22", linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=11)
    ax.set_xlim(0, 1.0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))

    for bar, t in zip(bars, thresholds):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                f"≥ {t:.0%}", va="center", fontsize=11, fontweight="bold",
                color=COLORS["text"])

    ax.axvline(x=0.6, color=COLORS["danger"], linestyle="--", linewidth=1, alpha=0.6)
    ax.text(0.6, len(metrics) - 0.15, "  min floor = 60%", fontsize=9,
            color=COLORS["danger"], va="top")

    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.4, alpha=0.5)
    save(fig, "04_anomaly_thresholds.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 5 — Layer 1: Confidence Bands (FIXED OVERLAPS v2)
# ════════════════════════════════════════════════════════════════════════
def plot_confidence_bands():
    # Increased height from 3.5 to 5.5 to prevent overlap
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=COLORS["bg"])
    # Pass empty title to style_ax so we can manually place it
    style_ax(ax, "", xlabel="Final Probability Score")

    # Staggered labeling to prevent ANY overlap
    # Format: (start, end, text, color, y_position)
    bands = [
        (0.0, 0.2, "High\n(Not Cheating)", COLORS["success"], 0.25),
        (0.2, 0.4, "Medium", COLORS["accent6"], 0.75),    
        (0.4, 0.6, "Low Confidence\nRange", COLORS["text_dim"], 0.4), # Merged 0.4-0.6
        (0.6, 0.8, "Medium", COLORS["warning"], 0.75),
        (0.8, 1.0, "High\n(Cheating)", COLORS["danger"], 0.25),
    ]

    for left, right, label, color, y_pos in bands:
        ax.axvspan(left, right, alpha=0.25, color=color)
        ax.text((left + right) / 2, y_pos, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=color)

    # Flag threshold line - Moved completely OUT of the plot area
    ax.axvline(x=0.5, color=COLORS["danger"], linewidth=2, linestyle="-")
    
    # SWAPPED POSITIONS:
    # 1. Box is now closer to the plot (y=1.08)
    ax.text(0.5, 1.08, "FLAG THRESHOLD (0.50)", ha="center", va="bottom", fontsize=10,
            fontweight="bold", color=COLORS["bg"],
            bbox=dict(facecolor=COLORS["danger"], edgecolor="none", boxstyle="round,pad=0.3"),
            transform=ax.get_xaxis_transform())

    # 2. Title is now at the very top (y=1.22)
    ax.text(0.5, 1.22, "Layer 1 — Confidence & Flagging Bands", ha="center", va="bottom",
            fontsize=14, fontweight="bold", color=COLORS["text"],
            transform=ax.get_xaxis_transform())

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.1))
    
    # Expand margins to fit both top elements
    plt.subplots_adjust(top=0.82)
    
    save(fig, "05_confidence_bands.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 6 — Layer 2: Fusion Weights (Donut)
# ════════════════════════════════════════════════════════════════════════
def plot_fusion_weights():
    fig, ax = plt.subplots(figsize=(7, 5.5), facecolor=COLORS["bg"])

    labels = ["Behavioral\n(35%)", "Anomaly\n(35%)", "Similarity\n(30%)"]
    sizes = [35, 35, 30]
    colors = [COLORS["accent1"], COLORS["accent2"], COLORS["accent4"]]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, textprops={"color": COLORS["text"], "fontsize": 11},
        wedgeprops={"edgecolor": COLORS["bg"], "linewidth": 2, "width": 0.45},
        pctdistance=0.78
    )
    for t in autotexts:
        t.set_fontweight("bold")
        t.set_fontsize(12)

    ax.set_title("Layer 2 — Risk Fusion Weights\n(Weighted Average Fallback)",
                 fontsize=14, fontweight="bold", color=COLORS["text"], pad=16)
    save(fig, "06_fusion_weights_donut.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 7 — Layer 2: Risk Level Bands (FIXED OVERLAPS)
# ════════════════════════════════════════════════════════════════════════
def plot_risk_levels():
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=COLORS["bg"])
    style_ax(ax, "Layer 2 — Risk Level Classification", xlabel="Final Risk Score")

    levels = [
        (0.0, 0.3, "LOW", COLORS["success"]),
        (0.3, 0.6, "MEDIUM", COLORS["accent4"]),
        (0.6, 0.8, "HIGH", COLORS["warning"]),
        (0.8, 1.0, "CRITICAL", COLORS["danger"]),
    ]

    for left, right, label, color in levels:
        ax.axvspan(left, right, alpha=0.3, color=color)
        # Shift High/Critical labels slightly to avoid line clash
        x_pos = (left + right) / 2
        ax.text(x_pos, 0.5, label, ha="center", va="center",
                fontsize=11, fontweight="bold", color=color)

    # Flag threshold - Moved label to bottom to separate from band labels
    ax.axvline(x=0.75, color="#ffffff", linewidth=2, linestyle="--")
    ax.text(0.75, -0.15, "FLAG THRESHOLD (≥ 0.75)", ha="center", va="top",
            fontsize=10, fontweight="bold", color="#ffffff",
            transform=ax.get_xaxis_transform())

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.1))
    save(fig, "07_risk_levels.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 8 — Example Scenarios Comparison (FIXED COLOR CONTRAST)
# ════════════════════════════════════════════════════════════════════════
def plot_example_scenarios():
    scenarios = [
        "Honest\nStudent",
        "Light\nCopy-Paste",
        "Tab-Switching\n+ Paste",
        "Heavy\nCheater",
    ]

    # Simulated component scores for each scenario
    paste = [0.05, 0.45, 0.30, 0.92]
    focus = [0.08, 0.10, 0.72, 0.85]
    hesitation = [0.12, 0.20, 0.15, 0.78]
    final = [0.07, 0.28, 0.51, 0.89]

    x = np.arange(len(scenarios))
    w = 0.18

    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=COLORS["bg"])
    style_ax(ax, "Example Scoring Scenarios", ylabel="Score (0–1)")

    ax.bar(x - 1.5 * w, paste, w, label="Paste Score", color=COLORS["accent1"],
           edgecolor="#ffffff22")
    ax.bar(x - 0.5 * w, focus, w, label="Focus Score", color=COLORS["accent2"],
           edgecolor="#ffffff22")
    ax.bar(x + 0.5 * w, hesitation, w, label="Hesitation Score", color=COLORS["accent4"],
           edgecolor="#ffffff22")
    bars_final = ax.bar(x + 1.5 * w, final, w, label="Final Probability",
                        color=COLORS["accent3"], edgecolor="#ffffff44", linewidth=1.2)

    # Add value labels on final bars
    for bar, v in zip(bars_final, final):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.2f}", ha="center", va="bottom", fontsize=9,
                fontweight="bold", color=COLORS["accent3"])

    # Flag threshold line - FIXED: Yellow with shadow for visibility
    # Shadow line
    ax.axhline(y=0.5, color="black", linewidth=3.0, linestyle="-", alpha=0.5)
    # Main line
    ax.axhline(y=0.5, color="#f1c40f", linewidth=2.0, linestyle="--", alpha=1.0)
    
    ax.text(len(scenarios) - 0.5, 0.52, "Flag Threshold (0.50)", fontsize=10,
            fontweight="bold", color="#f1c40f", ha="right",
            bbox=dict(facecolor=COLORS["bg"], edgecolor="none", alpha=0.7))

    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=10)
    ax.set_ylim(0, 1.1)
    ax.legend(loc="upper left", fontsize=9, facecolor=COLORS["card"],
              edgecolor=COLORS["grid"], labelcolor=COLORS["text"], ncol=2)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.4, alpha=0.5)
    save(fig, "08_example_scenarios.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 9 — Split Flowcharts (3 Parts)
# ════════════════════════════════════════════════════════════════════════

def draw_box(ax, x, y, w, h, text, color, fontsize=9):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                         facecolor=color, edgecolor="#ffffff33",
                         linewidth=1.2, alpha=0.85)
    ax.add_patch(box)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        ax.text(x + w / 2, y + h / 2 + (len(lines) / 2 - i - 0.5) * 0.28,
                line, ha="center", va="center", fontsize=fontsize,
                fontweight="bold", color="#ffffff")

def draw_arrow(ax, x1, y1, x2, y2, color=COLORS["text_dim"]):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                linewidth=1.5, mutation_scale=15))

def plot_pipeline_layer1():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("Layer 1 — MLPredictor Pipeline", fontsize=16,
                 fontweight="bold", color=COLORS["text"], pad=16)

    # Input
    draw_box(ax, 0.5, 6.0, 2.5, 1.0, "Raw Session\nFeatures", COLORS["accent6"], 10)
    
    # Processing
    draw_arrow(ax, 3.0, 6.5, 4.0, 6.5)
    draw_box(ax, 4.0, 6.0, 3.0, 1.0, "Derived Features\n+ Amplifier", COLORS["accent1"], 10)
    
    # Burst Detection path
    draw_box(ax, 0.5, 3.5, 2.5, 1.0, "Raw Events\n(timestamps)", COLORS["accent6"], 10)
    draw_arrow(ax, 3.0, 4.0, 4.0, 4.0)
    draw_box(ax, 4.0, 3.5, 3.0, 1.0, "Burst Pattern\nDetection", COLORS["accent3"], 10)

    # Models
    draw_arrow(ax, 7.0, 6.5, 8.0, 7.0)
    draw_box(ax, 8.0, 6.5, 3.0, 1.0, "Random Forest\n(rf_score)", COLORS["accent1"], 10)
    
    draw_arrow(ax, 7.0, 6.2, 8.0, 5.5)
    draw_box(ax, 8.0, 5.0, 3.0, 1.0, "Isolation Forest\n(if_score)", COLORS["accent2"], 10)
    
    draw_arrow(ax, 7.0, 4.0, 8.0, 4.0)
    draw_box(ax, 8.0, 3.5, 3.0, 1.0, "Burst Bonus\n(capped 0.3)", COLORS["accent3"], 10)

    # Output Combination
    draw_arrow(ax, 9.5, 6.5, 9.5, 2.5) # RF down
    draw_arrow(ax, 9.5, 5.0, 9.5, 2.5) # IF down
    draw_arrow(ax, 9.5, 3.5, 9.5, 2.5) # Burst down
    
    draw_box(ax, 6.0, 0.5, 5.0, 1.5, "Weighted Combination\nRF×0.8 + Burst×0.2\n(Anomaly floor 60%)", "#4a3d8f", 11)
    
    draw_arrow(ax, 6.0, 1.25, 4.0, 1.25)
    draw_box(ax, 1.0, 0.75, 3.0, 1.0, "Output Probability\n(0–1)", COLORS["success"], 11)

    save(fig, "09a_layer1_pipeline.png")


def plot_pipeline_layer2():
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Layer 2 — RiskFusionModel Pipeline", fontsize=16,
                 fontweight="bold", color=COLORS["text"], pad=16)

    # Inputs
    draw_box(ax, 0.5, 4.5, 2.5, 0.8, "Behavioral\nScore", COLORS["accent1"], 10)
    draw_box(ax, 3.75, 4.5, 2.5, 0.8, "Anomaly\nScore", COLORS["accent2"], 10)
    draw_box(ax, 7.0, 4.5, 2.5, 0.8, "Similarity\nScore", COLORS["accent4"], 10)

    # Fusion
    draw_arrow(ax, 1.75, 4.5, 4.0, 2.8)
    draw_arrow(ax, 5.0, 4.5, 5.0, 2.8)
    draw_arrow(ax, 8.25, 4.5, 6.0, 2.8)
    
    draw_box(ax, 3.0, 1.8, 4.0, 1.0, "Weighted Fusion\n35% / 35% / 30%", "#1a6b5a", 11)

    # Output
    draw_arrow(ax, 5.0, 1.8, 5.0, 1.2)
    draw_box(ax, 3.5, 0.2, 3.0, 1.0, "Final Risk Score\n+ Risk Level", COLORS["danger"], 11)

    save(fig, "09b_layer2_pipeline.png")


def plot_pipeline_combined():
    fig, ax = plt.subplots(figsize=(12, 3), facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.set_title("Combined Scoring Architecture", fontsize=16,
                 fontweight="bold", color=COLORS["text"], pad=16)

    # Simple high level flow
    draw_box(ax, 0.5, 1.0, 2.0, 1.0, "Session\nData", COLORS["accent6"], 10)
    draw_arrow(ax, 2.5, 1.5, 3.5, 1.5)
    
    draw_box(ax, 3.5, 1.0, 2.5, 1.0, "Layer 1\nMLPredictor", COLORS["accent1"], 10)
    draw_arrow(ax, 6.0, 1.5, 7.0, 1.5)
    
    draw_box(ax, 7.0, 1.0, 2.5, 1.0, "Layer 2\nRiskFusionModel", COLORS["accent2"], 10)
    draw_arrow(ax, 9.5, 1.5, 10.5, 1.5)
    
    draw_box(ax, 10.5, 1.0, 1.0, 1.0, "Risk\nScore", COLORS["danger"], 10)

    save(fig, "09c_combined_pipeline.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 10 — Burst Patterns
# ════════════════════════════════════════════════════════════════════════
def plot_burst_patterns():
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=COLORS["bg"])
    style_ax(ax, "Temporal Burst Pattern Detection", xlabel="", ylabel="Boost Value")

    patterns = ["Copy-Paste Burst\n(paste after blur\nwithin 5s)", "Tab Switch Storm\n(≥5 blurs in\n60 seconds)"]
    boosts = [0.15, 0.12]
    colors = [COLORS["accent1"], COLORS["accent2"]]

    bars = ax.bar(patterns, boosts, color=colors, width=0.45,
                  edgecolor="#ffffff22", linewidth=0.5)

    for bar, b in zip(bars, boosts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"+{b:.2f}", ha="center", va="bottom", fontsize=12,
                fontweight="bold", color=COLORS["text"])

    ax.axhline(y=0.30, color=COLORS["danger"], linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(1.35, 0.305, "Total cap = 0.30", fontsize=9, color=COLORS["danger"], ha="right")

    ax.set_ylim(0, 0.38)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.4, alpha=0.5)
    save(fig, "10_burst_patterns.png")


# ════════════════════════════════════════════════════════════════════════
#  PLOT 11 — Overall Project Architecture
# ════════════════════════════════════════════════════════════════════════
def plot_project_architecture():
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Cheating Detector System Architecture", fontsize=18,
                 fontweight="bold", color=COLORS["text"], pad=20)

    # ── User Tier ──
    draw_box(ax, 0.5, 1.5, 2.5, 3.0, "USER\n(Browser)", COLORS["card"], 12)
    draw_box(ax, 0.8, 3.2, 1.9, 0.8, "Next.js Client", COLORS["accent6"], 10)
    draw_box(ax, 0.8, 2.0, 1.9, 0.8, "Sensors\n(Input/Camera)", COLORS["accent5"], 10)

    # ── Middleware/Transport ──
    draw_arrow(ax, 3.0, 3.0, 4.5, 3.0, COLORS["text_dim"])
    ax.text(3.75, 3.2, "HTTP/WebSocket", ha="center", fontsize=9, color=COLORS["text_dim"])

    # ── Backend Tier ──
    draw_box(ax, 4.5, 0.5, 5.0, 5.0, "BACKEND\n(FastAPI / Python)", COLORS["card"], 12)
    
    # API Layer
    draw_box(ax, 4.8, 3.5, 2.0, 1.5, "API Routes\n(Events/Sessions)", COLORS["accent1"], 10)
    
    # Logic Layer
    draw_box(ax, 7.2, 3.5, 2.0, 1.5, "Core Logic\n(Validation)", COLORS["accent4"], 10)
    
    # ML Layer
    draw_box(ax, 4.8, 1.0, 4.4, 2.0, "ML Engine", "#2d3436", 11)
    draw_box(ax, 5.0, 1.2, 1.8, 1.3, "MLPredictor\n(RF/IF)", COLORS["accent1"], 9)
    draw_box(ax, 7.2, 1.2, 1.8, 1.3, "RiskFusion\nModel", COLORS["accent2"], 9)

    # ── Data Tier ──
    draw_arrow(ax, 9.5, 3.0, 11.0, 3.0, COLORS["text_dim"])
    ax.text(10.25, 3.2, "SQLQuery", ha="center", fontsize=9, color=COLORS["text_dim"])
    
    draw_box(ax, 11.0, 0.5, 2.5, 5.0, "DATA & AUTH\n(Supabase)", COLORS["card"], 12)
    draw_box(ax, 11.3, 3.0, 1.9, 1.5, "PostgreSQL\nDatabase", COLORS["accent6"], 10)
    draw_box(ax, 11.3, 1.0, 1.9, 1.5, "Auth & Storage", COLORS["warning"], 10)

    save(fig, "11_project_architecture.png")


# ════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n🎨 Generating Updated Scoring & Architecture Plots...\n")

    plot_heuristic_weights()
    plot_amplifier()
    plot_score_combination()
    plot_anomaly_thresholds()
    plot_confidence_bands()   # Fixed Overlap
    plot_fusion_weights()
    plot_risk_levels()        # Fixed Overlap
    plot_example_scenarios()  # Fixed Color
    
    # Split Flowcharts
    plot_pipeline_layer1()
    plot_pipeline_layer2()
    plot_pipeline_combined()
    
    plot_burst_patterns()
    plot_project_architecture() # New

    print(f"\n✅ All 13 plots saved to: {os.path.abspath(OUTPUT_DIR)}\n")
