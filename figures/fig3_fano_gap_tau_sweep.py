#!/usr/bin/env python3
"""
Figure 3 — Directional Fano gap: paired vs control across τ = 1, 3, 5
on ibm_strasbourg (9 April 2026, 9-qubit triangle cell).

Two-panel figure:
  (a) Bar chart of paired vs control Fano factor at τ = 1, 3, 5.
      The depth-matched τ = 5 gap (-0.058 favouring paired) is the
      paper's central hardware result (§3.3). At τ = 1 and τ = 3 the
      paired Fano is higher than the control — the directional signal
      only develops after the Floquet cycle has completed multiple
      periods. The plot shows this honestly.
  (b) Per-round Fano at τ = 5 (paired): five points across rounds 1-5,
      mean 0.487 ± 0.005, demonstrating that the sub-Poissonian signal
      is per-round-stable and not an end-of-cycle artefact.

Data sources: HARDWARE-RESULTS.md Table 3 (lines 95-100) and per-round
Fano table (line 119). All measurements on ibm_strasbourg, 9 Apr 2026.

Output: fig3_fano_gap_tau_sweep.png/.pdf
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.3,
})

# ── Hardware data from HARDWARE-RESULTS.md Table 3 ──
TAU = [1, 3, 5]
F_PAIRED  = [0.654, 0.871, 0.506]
F_CONTROL = [0.613, 0.600, 0.564]
DEPTH     = [47, 156, 279]   # transpiled depth at each τ
CX_GATES  = [None, None, 108]  # only τ=5 reported in HARDWARE-RESULTS

# Per-round Fano at τ=5 (HARDWARE-RESULTS.md line 119)
ROUNDS = [1, 2, 3, 4, 5]
F_PER_ROUND = [0.494, 0.481, 0.483, 0.485, 0.492]
F_PER_ROUND_MEAN = np.mean(F_PER_ROUND)
F_PER_ROUND_STD  = np.std(F_PER_ROUND, ddof=1)

# Colours
COLOR_PAIRED  = "#4477AA"   # blue
COLOR_CONTROL = "#CCBB44"   # yellow
COLOR_GAP     = "#EE6677"   # red (the τ=5 gap)
COLOR_POISSON = "#999999"

# ── Figure: two-panel layout (left=bar chart, right=per-round inset) ──
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(11.0, 4.6),
                                  gridspec_kw={"width_ratios": [1.6, 1.0]})

# ─────────────────── Panel (a): paired vs control bars ───────────────────
ax = ax_a
x = np.arange(len(TAU))
width = 0.36

bars_p = ax.bar(x - width/2, F_PAIRED, width, color=COLOR_PAIRED,
                label="Paired (P gate present)",
                edgecolor="white", linewidth=0.8)
bars_c = ax.bar(x + width/2, F_CONTROL, width, color=COLOR_CONTROL,
                label="Control (P gate removed)",
                edgecolor="white", linewidth=0.8)

# Value labels above each bar
for i, (p, c) in enumerate(zip(F_PAIRED, F_CONTROL)):
    ax.text(i - width/2, p + 0.015, f"{p:.3f}", ha="center", fontsize=9)
    ax.text(i + width/2, c + 0.015, f"{c:.3f}", ha="center", fontsize=9)

# Highlight the τ=5 gap
gap = F_PAIRED[2] - F_CONTROL[2]   # negative = paired more sub-P
ax.annotate("", xy=(2 - width/2, F_PAIRED[2]), xytext=(2 + width/2, F_CONTROL[2]),
            arrowprops=dict(arrowstyle="<->", color=COLOR_GAP, lw=1.8))
ax.text(2, 0.40, f"ΔF = {gap:+.3f}\n(directional)",
        ha="center", fontsize=10, color=COLOR_GAP, fontweight="bold")

# Poisson reference
ax.axhline(1.0, color=COLOR_POISSON, linestyle="--", linewidth=1.0, label="Poisson (F = 1)")
ax.text(0.5, 1.02, "F < 1 = sub-Poissonian", color=COLOR_POISSON, fontsize=9)

# Depth annotations under x labels
ax.set_xticks(x)
ax.set_xticklabels([f"τ = {t}\n(depth {d}{', 108 CX/ECR' if t == 5 else ''})"
                    for t, d in zip(TAU, DEPTH)])
ax.set_ylabel(r"Fano factor $\hat F = s^2 / \bar w$")
ax.set_ylim(0, 1.15)
ax.set_title(r"(a) τ-sweep on 9-qubit triangle cell, ibm_strasbourg, 9 Apr 2026", loc="left")
ax.legend(loc="upper right", framealpha=0.95)

# Add a one-line annotation about the matched-depth argument
ax.text(0.5, -0.27,
        "At τ = 5 the paired and control circuits run on the same chip with matched depth (279) and\n"
        "matched two-qubit gate count (108 CX/ECR), batched within seconds. The −0.058 gap cannot\n"
        "be attributed to decoherence, calibration drift, or qubit-quality differences (see §3.3).",
        transform=ax.transAxes, ha="center", fontsize=8.5, color="#444",
        family="serif", style="italic")

# ─────────────────── Panel (b): per-round Fano at τ=5 ───────────────────
ax = ax_b
ax.plot(ROUNDS, F_PER_ROUND, "o-", color=COLOR_PAIRED, markersize=10,
        linewidth=1.8, markeredgecolor="white", markeredgewidth=0.8,
        label="Per-round F (paired, τ = 5)")

# Mean line + ±1σ band
mean_line = ax.axhline(F_PER_ROUND_MEAN, color=COLOR_PAIRED, linestyle="--",
                        linewidth=1.2, alpha=0.7,
                        label=f"Mean = {F_PER_ROUND_MEAN:.3f} ± {F_PER_ROUND_STD:.3f}")
ax.fill_between([0.5, 5.5],
                F_PER_ROUND_MEAN - F_PER_ROUND_STD,
                F_PER_ROUND_MEAN + F_PER_ROUND_STD,
                color=COLOR_PAIRED, alpha=0.12)

# Poisson reference
ax.axhline(1.0, color=COLOR_POISSON, linestyle="--", linewidth=1.0)
ax.text(3, 1.02, "Poisson (F = 1)", color=COLOR_POISSON, fontsize=9, ha="center")

# Annotate values
for r, f in zip(ROUNDS, F_PER_ROUND):
    ax.text(r, f - 0.04, f"{f:.3f}", ha="center", fontsize=8.5)

ax.set_xlabel("Floquet round")
ax.set_ylabel(r"Per-round Fano factor")
ax.set_xticks(ROUNDS)
ax.set_xlim(0.5, 5.5)
ax.set_ylim(0.30, 1.15)
ax.set_title(r"(b) Per-round Fano at τ = 5 (paired)", loc="left")
ax.legend(loc="upper right", framealpha=0.95)

plt.tight_layout()
out_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig3_fano_gap_tau_sweep.png")
out_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig3_fano_gap_tau_sweep.pdf")
plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.savefig(out_pdf, bbox_inches="tight")
print(f"Wrote {out_png}")
print(f"Wrote {out_pdf}")
