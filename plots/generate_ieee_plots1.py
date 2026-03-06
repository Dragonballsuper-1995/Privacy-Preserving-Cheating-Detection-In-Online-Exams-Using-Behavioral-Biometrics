import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.path import Path
import matplotlib.patches as patches

# Directory setup
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DPI = 600

def configure_aesthetics():
    """Ultra-premium academic aesthetics."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 10,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#1E293B",
    })

def draw_ortho_path(ax, points, label="", label_pos=None, arrow_at_end=True, color="#64748B", lw=1.8):
    codes = [Path.MOVETO] + [Path.LINETO] * (len(points) - 1)
    path = Path(points, codes)
    patch = patches.PathPatch(path, fill=False, edgecolor=color, lw=lw, zorder=2)
    ax.add_patch(patch)
    
    if arrow_at_end:
        p1, p2 = points[-2], points[-1]
        if p1[0] == p2[0]: # Vertical
            xytext = (p2[0], p2[1] + 0.1 if p1[1] > p2[1] else p2[1] - 0.1)
        else: # Horizontal
            xytext = (p2[0] + 0.1 if p1[0] > p2[0] else p2[0] - 0.1, p2[1])
            
        ax.annotate("", xy=p2, xytext=xytext,
                    arrowprops=dict(arrowstyle="-|>,head_length=0.7,head_width=0.4",
                                    color=color, lw=lw), zorder=3)
                                    
    if label and label_pos:
        ax.text(label_pos[0], label_pos[1], label, ha="center", va="center",
                color="#475569", fontsize=9, fontstyle="italic",
                bbox=dict(facecolor="#F8FAFC", edgecolor="#CBD5E0", alpha=0.95, pad=0.3, boxstyle="round,pad=0.2"),
                zorder=6)

def draw_node(ax, x, y, w, h, title, subtitle, accent_color, is_fusion=False):
    # Shadow
    shadow = FancyBboxPatch((x - w/2 + 0.08, y - h/2 - 0.08), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.15",
                            facecolor="#0F172A", alpha=0.05, edgecolor="none", zorder=2)
    ax.add_patch(shadow)
    
    # Main Box
    edge_color = "#E11D48" if is_fusion else "#94A3B8"
    lw = 1.8 if is_fusion else 1.2
    
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.0,rounding_size=0.15",
                         facecolor="#FFFFFF", edgecolor=edge_color, linewidth=lw, zorder=3)
    ax.add_patch(box)
    
    # Accent Bar
    ax.plot([x - w/2, x - w/2], [y - h/2 + 0.15, y + h/2 - 0.15],
            color=accent_color, linewidth=4, solid_capstyle="round", zorder=4)
            
    # Text
    weight = "bold" if is_fusion else "bold"
    ax.text(x, y + 0.12, title, ha="center", va="center", color="#0F172A",
            fontsize=10.5, fontweight=weight, zorder=5)
    if subtitle:
        ax.text(x, y - 0.20, subtitle, ha="center", va="center", color="#475569",
                fontsize=8.5, zorder=5)

def draw_tier(ax, y_bot, h, label):
    box = FancyBboxPatch((0.5, y_bot), 11.0, h,
                         boxstyle="round,pad=0.0,rounding_size=0.2",
                         facecolor="#F8FAFC", edgecolor="#CBD5E0", linewidth=1.5, linestyle="--", zorder=0)
    ax.add_patch(box)
    ax.text(0.8, y_bot + h - 0.35, label, ha="left", va="top",
            color="#64748B", fontsize=12, fontweight="bold", zorder=1)

def draw_architecture():
    fig, ax = plt.subplots(figsize=(11, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 13.5)
    ax.axis("off")
    ax.set_title("Three-Tier System Architecture", fontsize=18, fontweight="bold", pad=20, color="#0F172A")
    
    draw_tier(ax, y_bot=8.8, h=3.8, label="C L I E N T   T I E R")
    draw_tier(ax, y_bot=3.2, h=5.2, label="A P P L I C A T I O N   T I E R")
    draw_tier(ax, y_bot=0.4, h=2.4, label="D A T A   T I E R")
    
    # Client Tier
    draw_node(ax, 2.5, 11.7, 3.4, 0.9, "Exam Interface", "Browser Client", "#0EA5E9")
    draw_node(ax, 2.5, 9.8, 3.4, 0.9, "Event Sensors", "Keystrokes, Mouse, Focus", "#0EA5E9")
    draw_node(ax, 9.5, 11.7, 3.4, 0.9, "Admin Dashboard", "Proctoring View", "#0EA5E9")
    
    # App Tier
    draw_node(ax, 2.5, 7.5, 3.4, 1.0, "API Layer", "REST Event Ingestion", "#6366F1")
    draw_node(ax, 9.5, 7.5, 3.4, 1.0, "Feature Pipeline", "Windowing & Extraction", "#6366F1")
    draw_node(ax, 4.75, 5.5, 2.6, 1.0, "Random Forest", "Supervised Class.", "#6366F1")
    draw_node(ax, 7.25, 5.5, 2.6, 1.0, "Isolation Forest", "Unsupervised Det.", "#6366F1")
    draw_node(ax, 6.0, 4.0, 4.0, 1.0, "Risk Fusion Engine", "Weighted Confidence Scoring", "#E11D48", is_fusion=True)
    
    # Data Tier
    draw_node(ax, 2.5, 1.5, 3.4, 1.0, "Session Store", "Raw Event Logs", "#10B981")
    draw_node(ax, 6.0, 1.5, 3.4, 1.0, "Decision & Risk Logs", "Session Confidence Scores", "#10B981")
    draw_node(ax, 9.5, 1.5, 3.4, 1.0, "Feature Vectors", "Processed Matrices", "#10B981")

    # Connections
    # Client internals
    draw_ortho_path(ax, [(2.5, 11.25), (2.5, 10.25)], label="interact", label_pos=(2.5, 10.75))
    
    # Cross Tier (down)
    draw_ortho_path(ax, [(2.5, 9.35), (2.5, 8.0)], label="raw events", label_pos=(2.5, 8.65))
    draw_ortho_path(ax, [(9.5, 11.25), (9.5, 8.0)], label="queries", label_pos=(9.5, 9.5))
    
    # App internals
    draw_ortho_path(ax, [(4.2, 7.5), (7.8, 7.5)], label="event payloads", label_pos=(6.0, 7.5))
    
    # Feature Bus
    draw_ortho_path(ax, [(9.5, 7.0), (9.5, 2.0)], label="save embeddings", label_pos=(9.5, 3.25))
    
    # Model Tap
    draw_ortho_path(ax, [(9.5, 6.7), (4.75, 6.7), (4.75, 6.0)])
    draw_ortho_path(ax, [(9.5, 6.7), (7.25, 6.7), (7.25, 6.0)])
    ax.plot([9.5], [6.7], marker="o", markersize=6, color="#64748B", zorder=6)
    ax.text(6.0, 6.9, "extracted behavioral features tap", ha="center", va="center", color="#475569", 
            fontsize=9.5, fontstyle="italic", bbox=dict(facecolor="#FFFFFF", edgecolor="none", alpha=0.9, pad=0.3), zorder=6)
            
    # Models to Fusion
    draw_ortho_path(ax, [(4.75, 5.0), (4.75, 4.5)], label="prob.", label_pos=(4.75, 4.75))
    draw_ortho_path(ax, [(7.25, 5.0), (7.25, 4.5)], label="anom.", label_pos=(7.25, 4.75))
    
    # Fusion to Data Tier
    draw_ortho_path(ax, [(6.0, 3.5), (6.0, 2.0)], label="final scores", label_pos=(6.0, 2.75))
    
    # API to Session Store
    draw_ortho_path(ax, [(2.5, 7.0), (2.5, 2.0)], label="save events", label_pos=(2.5, 4.5))

    fig.tight_layout()
    out_png = os.path.join(OUTPUT_DIR, "fig01_system_architecture.png")
    out_pdf = os.path.join(OUTPUT_DIR, "fig01_system_architecture.pdf")
    fig.savefig(out_png, dpi=DPI, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Saved {out_png}")
    print(f"  ✓ Saved {out_pdf}")

def pol2cart(r, theta):
    return r * np.cos(theta), r * np.sin(theta)

def draw_radar():
    categories = ["Typing Dynamics", "Hesitation\nPatterns", "Paste & Editing", "Focus\nBehaviour"]
    N = 4
    honest = [0.10, 0.10, 0.00, 0.00]
    suspicious = [0.20, 0.10, 0.85, 0.50]
    angles = [np.pi/2 - i * (np.pi/2) for i in range(N)]

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.axis("off")
    ax.set_title("Multi-Dimensional Risk Analysis", fontsize=16, fontweight="bold", pad=30, color="#0F172A")
    ax.set_aspect("equal")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    
    # Polygon Grids
    thresholds = [0.2, 0.4, 0.6, 0.8, 1.0]
    for t in thresholds:
        poly_pts = [pol2cart(t, a) for a in angles]
        poly = plt.Polygon(poly_pts, closed=True, fill=False, edgecolor="#E2E8F0", lw=1.2, zorder=1)
        ax.add_patch(poly)
        
        lx, ly = pol2cart(t, np.pi/4)
        ax.text(lx, ly, f"{t}", ha="center", va="center", fontsize=8.5, color="#94A3B8", 
                fontweight="bold", bbox=dict(facecolor="white", edgecolor="none", pad=1.0), zorder=2)
                
    # Axes lines
    for a in angles:
        px, py = pol2cart(1.0, a)
        ax.plot([0, px], [0, py], color="#E2E8F0", lw=1.5, zorder=1)
        
    # Threshold Circle
    circle = plt.Circle((0, 0), 0.60, fill=False, edgecolor="#D97706", linestyle="--", lw=2.0, zorder=3)
    ax.add_patch(circle)
    tx, ty = pol2cart(0.60, np.pi/4 * 3)
    ax.text(tx, ty, r"Flag Threshold ($\tau=0.60$)", ha="center", va="center", color="#D97706",
            fontsize=9.5, fontweight="bold", rotation=45, bbox=dict(facecolor="white", edgecolor="none", pad=1.0), zorder=6)
            
    # Labels
    for i, (cat, a) in enumerate(zip(categories, angles)):
        px, py = pol2cart(1.15, a)
        ha, va = "center", "center"
        if abs(np.cos(a)) < 0.1:
            va = "bottom" if np.sin(a) > 0 else "top"
        else:
            ha = "left" if np.cos(a) > 0 else "right"
        ax.text(px, py, cat, ha=ha, va=va, fontsize=11.5, fontweight="bold", color="#1E293B", zorder=7)

    # Data
    honest_pts = [pol2cart(honest[i], angles[i]) for i in range(N)]
    honest_poly = plt.Polygon(honest_pts, closed=True, fill=True, facecolor="#3B82F6", alpha=0.15, zorder=4)
    ax.add_patch(honest_poly)
    ax.plot(*zip(*(honest_pts + [honest_pts[0]])), color="#2563EB", lw=2.5, marker="o", markersize=8, markeredgecolor="white", markeredgewidth=1.5, zorder=5)

    susp_pts = [pol2cart(suspicious[i], angles[i]) for i in range(N)]
    susp_poly = plt.Polygon(susp_pts, closed=True, fill=True, facecolor="#EF4444", alpha=0.12, zorder=4)
    ax.add_patch(susp_poly)
    ax.plot(*zip(*(susp_pts + [susp_pts[0]])), color="#DC2626", lw=2.5, marker="D", markersize=8, markeredgecolor="white", markeredgewidth=1.5, zorder=5)

    # Point Annotations
    ax.text(*pol2cart(0.20, np.pi/2), "0.10", color="#2563EB", fontsize=9, fontweight="bold", ha="center") 
    ax.text(*pol2cart(0.30, np.pi/2), "0.20", color="#DC2626", fontsize=9, fontweight="bold", ha="center") 

    ax.text(*pol2cart(0.20, 0), "0.10", color="#0F172A", fontsize=9, fontweight="bold", ha="center", va="center") 
    
    ax.text(*pol2cart(0.95, -np.pi/2), "0.85", color="#DC2626", fontsize=9, fontweight="bold", ha="center") 
    ax.text(*pol2cart(0.60, np.pi), "0.50", color="#DC2626", fontsize=9, fontweight="bold", ha="center", va="bottom") 

    ax.annotate("0.00 (Honest)", xy=(-0.02, -0.02), xytext=(-0.35, -0.35), 
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.2),
                color="#2563EB", fontsize=9, fontweight="bold", zorder=8)

    # Legend
    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color="#2563EB", lw=2.5, marker="o", markersize=8, markerfacecolor="#2563EB", markeredgecolor="white"),
        Line2D([0], [0], color="#DC2626", lw=2.5, marker="D", markersize=8, markerfacecolor="#DC2626", markeredgecolor="white"),
    ]
    ax.legend(custom_lines, ['Honest Session', 'Suspicious Session'],
              loc='lower center', bbox_to_anchor=(0.5, -0.15),
              ncol=2, frameon=True, edgecolor="#E2E8F0", facecolor="white", fontsize=10.5)

    fig.tight_layout()
    out_png = os.path.join(OUTPUT_DIR, "fig05_dimension_radar.png")
    out_pdf = os.path.join(OUTPUT_DIR, "fig05_dimension_radar.pdf")
    fig.savefig(out_png, dpi=DPI, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Saved {out_png}")
    print(f"  ✓ Saved {out_pdf}")

if __name__ == "__main__":
    configure_aesthetics()
    print("Generating IEEE-compliant ultra-premium figures …")
    draw_architecture()
    draw_radar()
    print("Done.")