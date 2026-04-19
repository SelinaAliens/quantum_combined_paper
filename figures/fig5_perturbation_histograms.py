#!/usr/bin/env python3
"""
Figure 5 — Angle-table perturbation control histograms.

Two-panel figure visualising the §6.2 finding that the merkabit angle table
is strongly discriminative for the high-recurrence peak (P at n = 39, 94th
percentile vs random tables) but typical for the low-recurrence local minimum
(P at n = 13, 33rd percentile).

Reads ../data/angle_perturbation_1000.csv (3,000 trials × 6 observables).

Output: fig5_perturbation_histograms.png (and .pdf for print).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
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
    "grid.linestyle": "-",
    "grid.linewidth": 0.5,
})

# Colours (colour-blind friendly)
COLOR_RANDOM = "#4477AA"   # blue
COLOR_SHUFFLE = "#CCBB44"  # yellow
COLOR_SMALL = "#AA3377"    # purple
COLOR_MERK = "#EE6677"     # red (merkabit ideal value, vertical line)

# Merkabit ideal values (from the v9 paper §6.2 Table 8)
MERKABIT = {
    "P_at_n13": 0.6964,
    "P_at_n27": 0.6832,
    "P_at_n37": 0.9156,
    "P_at_n39": 0.9090,
    "ZZ_at_n12": 0.4474,
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "angle_perturbation_1000.csv")
df = pd.read_csv(CSV)
print(f"Loaded {len(df)} rows from {os.path.normpath(CSV)}")

# ---------------------------------------------------------------------------
# Build figure: 2 panels stacked vertically
# ---------------------------------------------------------------------------
fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7.0, 6.0), sharex=False)

# ── Top panel: P(n=39), the discriminating observable ──
ax = ax_top
obs = "P_at_n39"
merk = MERKABIT["P_at_n39"]
bins = np.linspace(0.1, 1.0, 50)

for tag, color, label in [("random", COLOR_RANDOM, "Random (Uniform 0.4–1.8)"),
                          ("shuffle", COLOR_SHUFFLE, "Shuffle (permute multipliers)"),
                          ("small",  COLOR_SMALL, "Small noise (σ = 0.1)")]:
    arr = df[df["perturbation"] == tag][obs].values
    ax.hist(arr, bins=bins, alpha=0.55, color=color, label=label, edgecolor="white", linewidth=0.4)

ax.axvline(merk, color=COLOR_MERK, linewidth=2.5, label=f"Merkabit ideal = {merk:.4f}", zorder=10)
# Pct at 94th — annotate
random_arr = df[df["perturbation"] == "random"][obs].values
pct_random = (random_arr <= merk).mean() * 100
ax.annotate(f"merkabit at\n{pct_random:.0f}th percentile\nof random tables",
            xy=(merk, 60), xytext=(0.55, 95),
            fontsize=9, color=COLOR_MERK,
            arrowprops=dict(arrowstyle="->", color=COLOR_MERK, lw=1.0))

ax.set_xlabel(r"$P(|00\rangle)$ at $n = 39$ (quasi-period peak)")
ax.set_ylabel("Trials (out of 1,000 per perturbation type)")
ax.set_title(r"(a) High-recurrence peak: discriminating ($\geq$ 0.85 $\Rightarrow$ angle-table specialness)", loc="left")
ax.set_xlim(0.1, 1.0)
ax.legend(loc="upper left", framealpha=0.9)

# ── Bottom panel: P(n=13), the typical observable ──
ax = ax_bot
obs = "P_at_n13"
merk = MERKABIT["P_at_n13"]
bins = np.linspace(0.1, 1.0, 50)

for tag, color, label in [("random", COLOR_RANDOM, "Random (Uniform 0.4–1.8)"),
                          ("shuffle", COLOR_SHUFFLE, "Shuffle (permute multipliers)"),
                          ("small",  COLOR_SMALL, "Small noise (σ = 0.1)")]:
    arr = df[df["perturbation"] == tag][obs].values
    ax.hist(arr, bins=bins, alpha=0.55, color=color, label=label, edgecolor="white", linewidth=0.4)

ax.axvline(merk, color=COLOR_MERK, linewidth=2.5, label=f"Merkabit ideal = {merk:.4f}", zorder=10)
random_arr = df[df["perturbation"] == "random"][obs].values
pct_random = (random_arr <= merk).mean() * 100
ax.annotate(f"merkabit at\n{pct_random:.0f}rd percentile\n(typical)",
            xy=(merk, 60), xytext=(0.05, 95),
            fontsize=9, color=COLOR_MERK,
            arrowprops=dict(arrowstyle="->", color=COLOR_MERK, lw=1.0))

ax.set_xlabel(r"$P(|00\rangle)$ at $n = 13$ (local minimum)")
ax.set_ylabel("Trials (out of 1,000 per perturbation type)")
ax.set_title(r"(b) Low-recurrence local minimum: typical (random tables give similar values)", loc="left")
ax.set_xlim(0.1, 1.0)
ax.legend(loc="upper left", framealpha=0.9)

plt.tight_layout()
out_png = os.path.join(HERE, "fig5_perturbation_histograms.png")
out_pdf = os.path.join(HERE, "fig5_perturbation_histograms.pdf")
plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.savefig(out_pdf, bbox_inches="tight")
print(f"Wrote {out_png}")
print(f"Wrote {out_pdf}")
