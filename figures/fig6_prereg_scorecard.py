#!/usr/bin/env python3
"""
Figure 6 — Pre-registration scorecard.

Two-column visual table:
  Left  — IBM Appendix N (Base Paper [16] v4, 2026-03-09):
          5 predictions, all retired on hardware April 6-12, 2026.
  Right — Google Willow PREDICTION.md (committed before any access):
          8 predictions, all pending hardware execution.

Status indicators are drawn as Circle patches (green = retired,
amber = pending) to avoid emoji-font dependencies. Mathematical
symbols use mathtext.

Output: fig6_prereg_scorecard.png/.pdf
"""
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
})

COLOR_RETIRED = "#228833"   # green
COLOR_PENDING = "#CCBB44"   # amber
COLOR_IBM     = "#4477AA"
COLOR_GOOGLE  = "#EE6677"
COLOR_BG_IBM  = "#EAF0F7"
COLOR_BG_GOOG = "#FBECEC"
COLOR_BG_PEND = "#FAF7E8"

# ── IBM predictions (Appendix N, retired) ──
IBM_PREDS = [
    ("P3", r"$\mathbb{Z}_2$ chirality symmetry",
        r"mean error 0.016 vs predicted < 5%",
        "Strasbourg, 7 Apr 2026"),
    ("P4", r"Centre-node detection rate",
        r"99.3% vs predicted 91% $\pm$ 5%",
        "Strasbourg (Eisenstein cell), 7 Apr"),
    ("P1", r"Berry-phase Ramsey signature",
        r"sign flip n=6$\rightarrow$8 confirmed; 96% peak fidelity",
        "Strasbourg + Kingston, 9 + 12 Apr"),
    ("P2", r"Stroboscopic quasi-period",
        r"n=37, 39 peaks at 99.99% / 99.6% (Kingston)",
        "Strasbourg + Kingston, 9 + 12 Apr"),
    ("P5", r"DTC subharmonic survival",
        r"paired/control 3.20$-$3.92$\times$ across 3 backends",
        "Brussels + Strasbourg + Kingston, 12 Apr"),
]

# ── Willow predictions (Table 7, pending) ──
WILLOW_PREDS = [
    ("1", r"2-qubit Fano factor at $\tau = 5$",
        r"$F \approx 0.3-0.7$",                          r"$F > 0.9$"),
    ("2", r"DTC paired/control 2T-power ratio",
        r"$> 3\times$",                                  r"ratio $< 2\times$"),
    ("3", r"P1b Ramsey sign flip",
        r"negative $\rightarrow$ positive at $n = 6 \rightarrow 8$",
        r"no sign change"),
    ("4", r"P2 stroboscopic local min $n = 13$",
        r"$P(|00\rangle) \approx 0.696 \pm 5\%$",        r"outside $\pm 5\%$"),
    ("5", r"P2 quasi-period peak $n$",
        r"$n = 39 \pm 2$",                               r"peak outside range"),
    ("6", r"4$\times$4 square-grid Fano ($\tau = 5$)",
        r"$F \approx 0.37 \pm 0.05$",                    r"$F > 0.6$"),
    ("7", r"P4 scaling: $F$ vs $N$ qubits",
        r"$F_{paired} \approx 0.19$ across $N \in \{2,4,6,8\}$",
        r"$F > 0.5$ at any $N$"),
    ("8", r"$P(|00\rangle)$ height at $n = 39$ (peak)",
        r"$\geq 0.85$ (Cirq ideal 0.9090; 94th pct)",    r"$P < 0.7$"),
]

fig, ax = plt.subplots(figsize=(13.5, 9.0))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Title
ax.text(50, 96, "Pre-registered prediction scorecard",
        ha="center", fontsize=14, fontweight="bold", color="#222")
ax.text(50, 92.5,
        "All predictions deposited at timestamped public commits before any hardware access.",
        ha="center", fontsize=10.5, color="#444", style="italic")

# Helper: status circle
def status_circle(x, y, color, radius=1.3):
    c = Circle((x, y), radius, facecolor=color, edgecolor="#222",
               linewidth=0.8, zorder=5)
    ax.add_patch(c)

# ─────────────────── LEFT column: IBM Appendix N ───────────────────
LEFT_X, LEFT_W = 2, 47
left_header = FancyBboxPatch((LEFT_X, 82), LEFT_W, 7,
                              boxstyle="round,pad=0.5,rounding_size=0.8",
                              linewidth=1.5, edgecolor=COLOR_IBM,
                              facecolor=COLOR_BG_IBM)
ax.add_patch(left_header)
ax.text(LEFT_X + LEFT_W / 2, 86.5,
        "IBM Appendix N — RETIRED",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color=COLOR_IBM)
ax.text(LEFT_X + LEFT_W / 2, 83.5,
        "Base Paper [16] v4, deposited Zenodo 2026-03-09; retired 6$-$12 Apr 2026",
        ha="center", va="center", fontsize=9, color="#444", style="italic")

ROW_H = 13
for i, (tag, name, result, where) in enumerate(IBM_PREDS):
    y_top = 79 - i * ROW_H
    row_box = Rectangle((LEFT_X, y_top - ROW_H + 1), LEFT_W, ROW_H - 1.5,
                         linewidth=0.8, edgecolor="#888", facecolor="white")
    ax.add_patch(row_box)
    # Status circle (green = retired)
    status_circle(LEFT_X + 2.5, y_top - 3.0, COLOR_RETIRED)
    # Tag
    ax.text(LEFT_X + 5.5, y_top - 3, tag,
            fontsize=11, color=COLOR_IBM, fontweight="bold", va="center")
    # Name
    ax.text(LEFT_X + 9, y_top - 3, name,
            fontsize=10.5, color="#222", va="center")
    # Result
    ax.text(LEFT_X + 1.5, y_top - 7.0, "result: " + result,
            fontsize=9, color="#333")
    # Provenance
    ax.text(LEFT_X + 1.5, y_top - 10, where,
            fontsize=8.5, color="#666", style="italic")

# Footer summary (left)
status_circle(LEFT_X + LEFT_W / 2 - 9, 12, COLOR_RETIRED, radius=1.5)
ax.text(LEFT_X + LEFT_W / 2 - 6.5, 12,
        "5 of 5 retired",
        va="center", fontsize=14, fontweight="bold", color=COLOR_RETIRED)
ax.text(LEFT_X + LEFT_W / 2, 8.5,
        "across three IBM backends and two architectures",
        ha="center", fontsize=9.5, color="#444", style="italic")

# ─────────────────── RIGHT column: Willow predictions ───────────────────
RIGHT_X, RIGHT_W = 51, 47
right_header = FancyBboxPatch((RIGHT_X, 82), RIGHT_W, 7,
                               boxstyle="round,pad=0.5,rounding_size=0.8",
                               linewidth=1.5, edgecolor=COLOR_GOOGLE,
                               facecolor=COLOR_BG_GOOG)
ax.add_patch(right_header)
ax.text(RIGHT_X + RIGHT_W / 2, 86.5,
        "Google Willow — PENDING HARDWARE",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color=COLOR_GOOGLE)
ax.text(RIGHT_X + RIGHT_W / 2, 83.5,
        "PREDICTION.md SHA 5bbfdb6f (12 Apr) and 745f653f (15 Apr); both before any access",
        ha="center", va="center", fontsize=9, color="#444", style="italic")

W_ROW_H = 8.5
for i, (num, name, pred, falsif) in enumerate(WILLOW_PREDS):
    y_top = 79 - i * W_ROW_H
    is_loadbearing = (num == "8")
    row_box = Rectangle((RIGHT_X, y_top - W_ROW_H + 0.5), RIGHT_W, W_ROW_H - 1,
                         linewidth=1.4 if is_loadbearing else 0.8,
                         edgecolor="#a44" if is_loadbearing else "#888",
                         facecolor=COLOR_BG_PEND if is_loadbearing else "white")
    ax.add_patch(row_box)
    # Status circle (amber = pending)
    status_circle(RIGHT_X + 2.5, y_top - 3, COLOR_PENDING)
    # Number
    ax.text(RIGHT_X + 5.5, y_top - 3, num,
            fontsize=11, color=COLOR_GOOGLE, fontweight="bold", va="center")
    # Name
    ax.text(RIGHT_X + 8, y_top - 3, name,
            fontsize=9.5, color="#222", va="center")
    # Predicted value
    ax.text(RIGHT_X + 8, y_top - 5.3, "predict: " + pred,
            fontsize=8.5, color="#333")
    # Falsification
    ax.text(RIGHT_X + 8, y_top - 7.1, "falsify by: " + falsif,
            fontsize=8.5, color="#a44")

# Highlight obs 8 as load-bearing (annotation outside the row)
ax.text(RIGHT_X + RIGHT_W - 1, 79 - 7 * W_ROW_H + 4.0,
        "load-bearing\n(94th pct vs\nrandom tables;\n§6.2)",
        fontsize=8, color="#a44", style="italic", ha="right", va="center",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=COLOR_BG_PEND, edgecolor="#a44", linewidth=0.7))

# Footer summary (right)
status_circle(RIGHT_X + RIGHT_W / 2 - 9, 12, COLOR_PENDING, radius=1.5)
ax.text(RIGHT_X + RIGHT_W / 2 - 6.5, 12,
        "8 of 8 pending",
        va="center", fontsize=14, fontweight="bold", color="#998811")
ax.text(RIGHT_X + RIGHT_W / 2, 8.5,
        "Cirq protocols + scoring scripts pinned at submission-time SHA",
        ha="center", fontsize=9.5, color="#444", style="italic")

# ─────────────────── Bottom takeaway band ───────────────────
takeaway = FancyBboxPatch((4, 1.5), 92, 4.5,
                           boxstyle="round,pad=0.5,rounding_size=0.6",
                           linewidth=1.0, edgecolor="#888",
                           facecolor="#FAFAFA")
ax.add_patch(takeaway)
ax.text(50, 3.7,
        "Both registrations follow the same standard: timestamped public commits before data, "
        "no error mitigation, raw counts added within 48 h of receipt, no post-hoc threshold adjustment.",
        ha="center", va="center", fontsize=9.5, color="#222", style="italic")

plt.tight_layout()
HERE = os.path.dirname(os.path.abspath(__file__))
out_png = os.path.join(HERE, "fig6_prereg_scorecard.png")
out_pdf = os.path.join(HERE, "fig6_prereg_scorecard.pdf")
plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.savefig(out_pdf, bbox_inches="tight")
print(f"Wrote {out_png}")
print(f"Wrote {out_pdf}")
