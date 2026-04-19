#!/usr/bin/env python3
"""
Figure 4 — Seed dispersion (§4.4) + hex-vs-square topology (§4).

Two-panel figure:
  (a) Box-and-strip plot of F_paired across 30 PRNG seeds for the four
      headline cells (hex-r1-7n, sq-3x3-9n, hex-r2-19n, sq-4x4-16n) at
      tau = 5, eps = 0.10. The 4x4 square shows the lowest mean AND
      lowest dispersion — the "stable optimum" claim of §4.4.
      The Paper 26 single-seed-42 value is marked with a red ✕ to show
      it was a low-tail draw on the 4x4 cell.
  (b) F vs epsilon for hex (7n, 19n) and square (9n, 16n) at tau = 5.
      Square consistently below hex at every epsilon — the "square wins
      deep" claim of §4.

Reads ../data/seed_dispersion_30seeds.csv for panel (a).
Panel (b) data is from Paper 26 Table 3 (committed as constants below).

Output: fig4_seed_dispersion_and_topology.png/.pdf
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ── Style ──
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

# ── Colours ──
COLOR_HEX = "#4477AA"     # blue
COLOR_SQ = "#EE6677"      # red
COLOR_PAPER26 = "#222222" # dark grey for the seed=42 mark
COLOR_POISSON = "#999999" # F=1 reference line

# ── Load seed-dispersion data ──
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "seed_dispersion_30seeds.csv")
df = pd.read_csv(CSV)
print(f"Loaded {len(df)} rows from {os.path.normpath(CSV)}")

# Order cells: hex-7n, sq-9n, hex-19n, sq-16n (small to large within hex/sq)
CELL_ORDER = ["hex-r1-7n", "sq-3x3-9n", "hex-r2-19n", "sq-4x4-16n"]
CELL_LABELS = {
    "hex-r1-7n":  "hex 7n\n(r = 1)",
    "sq-3x3-9n":  "sq 9n\n(3×3)",
    "hex-r2-19n": "hex 19n\n(r = 2)",
    "sq-4x4-16n": "sq 16n\n(4×4)",
}
CELL_COLORS = {
    "hex-r1-7n": COLOR_HEX, "sq-3x3-9n": COLOR_SQ,
    "hex-r2-19n": COLOR_HEX, "sq-4x4-16n": COLOR_SQ,
}

# Single-seed-42 reference values from Paper 26 (the original published numbers)
PAPER26_SEED42 = {
    "hex-r1-7n":  0.522,
    "sq-3x3-9n":  0.343,
    "hex-r2-19n": 0.397,
    "sq-4x4-16n": 0.285,
}

# ── Build figure: two side-by-side panels ──
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(11.0, 4.8))

# ─────────────────── Panel (a): seed dispersion ───────────────────
ax = ax_a
positions = np.arange(len(CELL_ORDER))
data = [df[df["cell"] == c]["fano_paired"].values for c in CELL_ORDER]

# Strip plot (jitter individual seeds)
rng = np.random.default_rng(42)
for i, (cell, vals) in enumerate(zip(CELL_ORDER, data)):
    jitter = rng.uniform(-0.08, 0.08, size=len(vals))
    ax.scatter(positions[i] + jitter, vals, s=18, alpha=0.55,
               color=CELL_COLORS[cell], edgecolor="white", linewidth=0.5, zorder=3)

# Box plot overlay
bp = ax.boxplot(data, positions=positions, widths=0.45, patch_artist=True,
                showcaps=True, showfliers=False,
                boxprops=dict(facecolor="none", edgecolor="black", linewidth=1.2),
                medianprops=dict(color="black", linewidth=1.5),
                whiskerprops=dict(color="black", linewidth=1.0),
                capprops=dict(color="black", linewidth=1.0))

# Mark the Paper 26 seed=42 values
for i, cell in enumerate(CELL_ORDER):
    val = PAPER26_SEED42[cell]
    ax.scatter([positions[i]], [val], marker="x", s=110, color=COLOR_PAPER26,
               linewidth=2.2, zorder=10, label="Paper 26 (seed = 42)" if i == 0 else None)

# Annotate the 4x4 sweet spot
mean_4x4 = df[df["cell"] == "sq-4x4-16n"]["fano_paired"].mean()
std_4x4 = df[df["cell"] == "sq-4x4-16n"]["fano_paired"].std(ddof=1)
ax.annotate(f"§4.4 headline:\nF = {mean_4x4:.3f} ± {std_4x4:.3f}\n(lowest mean AND\nlowest dispersion)",
            xy=(3, mean_4x4), xytext=(2.0, 0.85),
            fontsize=9, ha="center",
            arrowprops=dict(arrowstyle="->", color="black", lw=0.8))

# Poisson reference
ax.axhline(1.0, color=COLOR_POISSON, linestyle="--", linewidth=1.0, label="Poisson (F = 1)")

ax.set_xticks(positions)
ax.set_xticklabels([CELL_LABELS[c] for c in CELL_ORDER])
ax.set_ylabel(r"Fano factor $F_{\mathrm{paired}}$  ($\tau = 5$, $\varepsilon = 0.10$)")
ax.set_ylim(0.15, 1.05)
ax.set_title("(a) Seed dispersion across 30 PRNG seeds (20,000 shots each)", loc="left")
ax.legend(loc="upper left", framealpha=0.9)

# Add hex/sq groupings as text below the x-axis
ax.text(0.5, -0.15, "hex topology", transform=ax.get_xaxis_transform(),
        ha="center", color=COLOR_HEX, fontsize=10, fontweight="bold")
ax.text(2.5, -0.15, "square topology", transform=ax.get_xaxis_transform(),
        ha="center", color=COLOR_SQ, fontsize=10, fontweight="bold")
# (This is a cosmetic label that may or may not render perfectly; we leave it.)

# ─────────────────── Panel (b): F vs epsilon, hex vs square ───────────────────
ax = ax_b
# Data from Paper 26 Table 3 (seed=42, single-trial; quoted in v9 §4 prose)
EPS = np.array([0.01, 0.05, 0.10, 0.20, 0.30])
HEX_7N  = np.array([0.067, 0.305, 0.557, 0.846, 0.940])  # 7-node hex
HEX_19N = np.array([0.048, 0.223, 0.397, 0.652, 0.775])  # 19-node hex (r=2)
SQ_9N   = np.array([0.042, 0.189, 0.344, 0.569, 0.697])  # 3x3 square
SQ_16N  = np.array([0.033, 0.157, 0.285, 0.489, 0.604])  # 4x4 square (sweet spot)

ax.plot(EPS, HEX_7N,  "o-", color=COLOR_HEX, label="hex 7n (r = 1)",
        linewidth=1.5, markersize=7, alpha=0.55)
ax.plot(EPS, HEX_19N, "s-", color=COLOR_HEX, label="hex 19n (r = 2)",
        linewidth=1.8, markersize=7)
ax.plot(EPS, SQ_9N,   "o-", color=COLOR_SQ, label="sq 9n (3×3)",
        linewidth=1.5, markersize=7, alpha=0.55)
ax.plot(EPS, SQ_16N,  "s-", color=COLOR_SQ, label="sq 16n (4×4) ← sweet spot",
        linewidth=1.8, markersize=7)

ax.axhline(1.0, color=COLOR_POISSON, linestyle="--", linewidth=1.0)

ax.set_xlabel(r"Per-node, per-step error rate  $\varepsilon$")
ax.set_ylabel(r"Fano factor $F_{\mathrm{paired}}$  ($\tau = 5$)")
ax.set_xlim(-0.005, 0.32)
ax.set_ylim(0, 1.05)
ax.set_title("(b) Square topology beats hex at every error rate", loc="left")
ax.legend(loc="upper left", framealpha=0.9)

plt.tight_layout()
out_png = os.path.join(HERE, "fig4_seed_dispersion_and_topology.png")
out_pdf = os.path.join(HERE, "fig4_seed_dispersion_and_topology.pdf")
plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.savefig(out_pdf, bbox_inches="tight")
print(f"Wrote {out_png}")
print(f"Wrote {out_pdf}")
