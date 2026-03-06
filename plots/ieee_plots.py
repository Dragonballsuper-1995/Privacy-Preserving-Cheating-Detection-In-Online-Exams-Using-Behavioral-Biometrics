"""
High-Fidelity, Publication-Ready IEEE Figures for Cheating Detection Paper.
Generates ultra-crisp (600 DPI) vector-style plots using advanced Matplotlib math.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)
DPI = 600 # IEEE Print Standard

def configure_ieee_typography():
    """Enforces strict IEEE academic typography and crisp vector stylings."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 11,
        "axes.titlesize": 16,
        "axes.labelsize": 12,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#111827", # High-contrast almost-black
    })

# ═══════════════════════════════════════════════════════════════════════════
# FIG 1 – Architectural Block Diagram (TikZ Vector Style)
# ═══════════════════════════════════════════════════════════════════════════
def draw_architecture():
    fig, ax = plt.subplots(figsize=(12.5, 10.5))
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 100)
    ax.axis("off")
    
    # Title
    ax.text(60, 96, "Three-Tier System Architecture", ha="center", va="center", 
            fontsize=18, fontweight="bold", color="#111827")

    # ── Tier Separators & Labels ──
    tier_lines = [68, 18]
    for y in tier_lines:
        ax.axhline(y, color="#94A3B8", linestyle="--", linewidth=1.5, alpha=0.8, xmin=0.05, xmax=0.95)

    def draw_tier_label(y_center, text):
        spaced_text = "\u200A".join(text.upper())
        ax.text(3, y_center, spaced_text, rotation=90, ha="center", va="center",
                fontsize=14, fontweight="bold", color="#64748B")

    draw_tier_label(84, "Client Tier")
    draw_tier_label(43, "Application Tier")
    draw_tier_label(9, "Data Tier")

    # ── Advanced Node & Routing Engine ──
    def draw_node(x, y, w, h, text, is_hero=False):
        border_color = "#2563EB" if is_hero else "#334155" 
        bg_color = "#F0F9FF" if is_hero else "#FFFFFF"
        line_weight = 2.5 if is_hero else 1.5

        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.3",
                             facecolor=bg_color, edgecolor=border_color, linewidth=line_weight, zorder=3)
        ax.add_patch(box)

        weight = "bold" if is_hero else "medium"
        color = "#1E3A8A" if is_hero else "#0F172A"
        ax.text(x, y, text, ha="center", va="center", color=color,
                fontsize=11.5, fontweight=weight, linespacing=1.5, zorder=4)
        
        return {"n": (x, y + h/2), "s": (x, y - h/2), "e": (x + w/2, y), "w": (x - w/2, y)}

    def draw_route(start, end, label=None, offset=(0,0)):
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="-|>,head_length=0.8,head_width=0.5",
                                    color="#475569", lw=1.8, shrinkA=1, shrinkB=1), zorder=2)
        if label:
            mx, my = (start[0]+end[0])/2 + offset[0], (start[1]+end[1])/2 + offset[1]
            halo = [pe.withStroke(linewidth=4, foreground="white")]
            ax.text(mx, my, label, ha="center", va="center", color="#334155",
                    fontsize=10.5, fontstyle="italic", fontweight="bold", path_effects=halo, zorder=5)

    # ── Layout Grid Variables ──
    W, H = 19, 7
    COL_L, COL_C, COL_R = 20, 60, 100
    ML_L, ML_R = 42, 78

    # ── Render Nodes ──
    n_brow  = draw_node(COL_L, 88, W, H, "Exam Interface\n(Browser Client)")
    n_admin = draw_node(COL_R, 88, W, H, "Admin Dashboard")
    n_sens  = draw_node(COL_L, 75, W, H, "Keystroke · Mouse\nFocus Sensors")
    n_api   = draw_node(COL_L, 56, W, H, "API Layer\n(REST Endpoints)")
    n_ext   = draw_node(COL_R, 56, W, H, "Feature Extraction\nPipeline")
    n_rf    = draw_node(ML_L,  41, W, H, "Random Forest\nClassifier")
    n_if    = draw_node(ML_R,  41, W, H, "Isolation Forest\nDetector")
    n_fus   = draw_node(COL_C, 27, 21, 7.5, "Risk Fusion Model", is_hero=True)
    n_sess  = draw_node(COL_L,  8, W, H, "Session &\nEvent Store")
    n_arts  = draw_node(COL_C,  8, W, H, "Model Artefacts")
    n_vecs  = draw_node(COL_R,  8, W, H, "Feature Vectors")

    # ── Render Perfect Vector Routes ──
    draw_route(n_brow["s"], n_sens["n"], "raw inputs", offset=(3.5, 0))
    draw_route(n_sens["s"], n_api["n"], "events", offset=(3.5, -2.5)) 
    draw_route(n_api["s"], n_sess["n"], "store session", offset=(4.5, 0))
    draw_route(n_admin["s"], n_ext["n"], "queries", offset=(3.5, 3.5))
    draw_route(n_ext["s"], n_vecs["n"], "store vectors", offset=(4.5, 0))
    draw_route(n_fus["s"], n_arts["n"], "model state", offset=(4.5, -2))
    draw_route(n_api["e"], n_ext["w"], "feature data", offset=(0, 1.5))
    draw_route((COL_R - W/2 + 2, 52.5), n_rf["n"], "data", offset=(-3, 2)) 
    draw_route((COL_R - W/2 + 6, 52.5), n_if["n"], "data", offset=(3, 2))
    draw_route(n_rf["s"], (COL_C - 4, 30.7), "RF score", offset=(-3.5, 0))
    draw_route(n_if["s"], (COL_C + 4, 30.7), "IF score", offset=(3.5, 0))

    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "fig01_system_architecture.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ High-Fidelity Architecture saved to {out}")

# ═══════════════════════════════════════════════════════════════════════════
# FIG 5 – Dimension Comparison (Grouped Bar Chart Alternative)
# ═══════════════════════════════════════════════════════════════════════════
def draw_dimension_bars():
    """Generates an academically rigorous grouped bar chart avoiding radar area-distortion."""
    categories = ["Typing\nDynamics", "Hesitation\nPatterns", "Paste &\nEditing", "Focus\nBehaviour"]
    honest = [0.10, 0.10, 0.00, 0.00]
    suspicious = [0.20, 0.10, 0.85, 0.50]
    
    x = np.arange(len(categories))  # Label locations
    width = 0.32                    # Width of the bars

    fig, ax = plt.subplots(figsize=(9, 6.5))

    # ── High-Contrast Grid ──
    # Only horizontal lines, keeping the X-axis clean
    ax.yaxis.grid(True, color="#E2E8F0", linewidth=1.2, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)

    # ── Publication Data Plotting ──
    c_honest = "#059669" # Emerald
    c_susp   = "#E11D48" # Crimson

    # Plot bars with subtle edge highlights for crispness
    rects1 = ax.bar(x - width/2, honest, width, label="Honest baseline", 
                    color=c_honest, edgecolor="white", linewidth=1.5, zorder=3)
    rects2 = ax.bar(x + width/2, suspicious, width, label="Anomalous session", 
                    color=c_susp, edgecolor="white", linewidth=1.5, zorder=3)

    # ── Data Labels ──
    # Adds the exact values on top of the bars for maximum clarity
    halo = [pe.withStroke(linewidth=3, foreground="white")]
    ax.bar_label(rects1, padding=5, fmt='%.2f', fontsize=11, fontweight="bold", color=c_honest, path_effects=halo)
    ax.bar_label(rects2, padding=5, fmt='%.2f', fontsize=11, fontweight="bold", color=c_susp, path_effects=halo)

    # ── Flag Threshold Strike ──
    ax.axhline(0.60, color="#64748B", linewidth=2.5, linestyle=(0, (5, 4)), zorder=4)
    
    # Place tau label on the far right edge of the line
    ax.text(x[-1] + width + 0.15, 0.60, r"$\tau = 0.60$", color="#334155", 
            va="center", ha="left", fontsize=13, fontweight="bold", path_effects=halo, zorder=5)

    # ── Typography & Limits ──
    ax.set_title("Per-Dimension Suspicion Scores", fontsize=18, fontweight="bold", pad=25, color="#111827")
    ax.set_ylabel("Risk Score", fontsize=13, fontweight="bold", color="#475569", labelpad=15)
    
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=11, fontweight="bold", color="#64748B")
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=13, fontweight="bold", color="#1E293B")
    ax.tick_params(axis='x', pad=10, bottom=False) # Remove x-axis tick lines for cleaner look

    # ── Elegant Legend ──
    from matplotlib.lines import Line2D
    thresh_line = Line2D([0], [0], color="#64748B", linewidth=2.5, linestyle=(0, (5, 4)), label=r"Flag threshold ($\tau$ = 0.60)")
    handles, labels = ax.get_legend_handles_labels()
    handles.insert(0, thresh_line)
    labels.insert(0, r"Flag threshold ($\tau$ = 0.60)")

    legend = ax.legend(
        handles=handles, labels=labels,
        loc="upper center", bbox_to_anchor=(0.5, -0.15),
        fontsize=12.5, frameon=True, edgecolor="#CBD5E1",
        facecolor="#F8FAFC", framealpha=1.0,
        ncol=3, columnspacing=2.0, handlelength=2.5, handleheight=1.5,
    )
    legend.get_frame().set_linewidth(1.5)

    fig.tight_layout()
    # Note: Filename updated to reflect the new chart type
    out = os.path.join(OUTPUT_DIR, "fig05_dimension_bars.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ High-Fidelity Dimension Bar Chart saved to {out}")

# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    configure_ieee_typography()
    print("Initiating 600 DPI rendering engine for IEEE publication ...")
    draw_architecture()
    draw_dimension_bars()
    print("Execution complete. Ready for LaTeX integration.")