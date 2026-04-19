#!/usr/bin/env python3
"""
Figure 1 — P gate decomposition (visual abstract).

The merkabit's signature operation P(φ) = Rz(+φ) ⊗ Rz(−φ) compiles to
zero-overhead native gates on both IBM and Google superconducting hardware.

    Top:         P gate definition
    Left branch: IBM Eagle r3 / Heron r2 — two virtual-Z frame changes,
                 transpiled depth 6 for any n-step Floquet cycle.
    Right branch: Google Willow — single PhXZ gate per qubit,
                  transpiled depth 2 independent of n.
    Bottom:      shared takeaway.

Output: fig1_p_gate_decomposition.png/.pdf
"""
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, Rectangle

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
})

# Colours
COLOR_IBM    = "#4477AA"   # blue
COLOR_GOOGLE = "#EE6677"   # red
COLOR_TOP    = "#222222"
COLOR_BOX_BG = "#F5F5F5"

fig, ax = plt.subplots(figsize=(11.5, 8.0))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# ─────────────────── TOP: The P gate definition ───────────────────
title_box = FancyBboxPatch((22, 88), 56, 11,
                            boxstyle="round,pad=0.5,rounding_size=1.2",
                            linewidth=1.5, edgecolor=COLOR_TOP,
                            facecolor=COLOR_BOX_BG)
ax.add_patch(title_box)
ax.text(50, 95.5, "The P gate (the merkabit's signature)",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color=COLOR_TOP)
ax.text(50, 91, r"$P(\varphi)\;=\;R_z(+\varphi)\;\otimes\;R_z(-\varphi)$"
                r"   on the dual-spinor pair $(q^+,\, q^-)$",
        ha="center", va="center", fontsize=11, color=COLOR_TOP)

# Two arrows down to the branches
ax.annotate("", xy=(20, 80), xytext=(38, 88),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4,
                            connectionstyle="arc3,rad=-0.15"))
ax.annotate("", xy=(80, 80), xytext=(62, 88),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4,
                            connectionstyle="arc3,rad=0.15"))

# Branch labels
ax.text(20, 84, "IBM Eagle r3 / Heron r2",
        ha="center", fontsize=10.5, color=COLOR_IBM, fontweight="bold")
ax.text(80, 84, "Google Willow / Sycamore family",
        ha="center", fontsize=10.5, color=COLOR_GOOGLE, fontweight="bold")

# ─────────────────── LEFT: IBM virtual-Z (depth 6) ───────────────────
left_box = FancyBboxPatch((4, 12), 42, 67,
                           boxstyle="round,pad=0.5,rounding_size=1.0",
                           linewidth=1.4, edgecolor=COLOR_IBM,
                           facecolor="white")
ax.add_patch(left_box)

ax.text(25, 75,
        "compiles to two virtual-Z frame changes",
        ha="center", va="center", fontsize=10.5, color=COLOR_IBM, style="italic")

# Circuit diagram — qubit lines split around each gate box
qubit_y_plus  = 65
qubit_y_minus = 55
LEFT_X, RIGHT_X = 10, 41
GATE_X_IBM = 25
GATE_HW = 5  # half-width of IBM gate box
# Left segments
ax.plot([LEFT_X, GATE_X_IBM - GATE_HW], [qubit_y_plus,  qubit_y_plus],  color="black", lw=1.2)
ax.plot([LEFT_X, GATE_X_IBM - GATE_HW], [qubit_y_minus, qubit_y_minus], color="black", lw=1.2)
# Right segments
ax.plot([GATE_X_IBM + GATE_HW, RIGHT_X], [qubit_y_plus,  qubit_y_plus],  color="black", lw=1.2)
ax.plot([GATE_X_IBM + GATE_HW, RIGHT_X], [qubit_y_minus, qubit_y_minus], color="black", lw=1.2)
ax.text(8, qubit_y_plus,  r"$q^+$", ha="right", va="center", fontsize=11)
ax.text(8, qubit_y_minus, r"$q^-$", ha="right", va="center", fontsize=11)

def vz_box(x, y, label):
    box = Rectangle((x - GATE_HW, y - 2.5), 2*GATE_HW, 5, linewidth=1.2,
                    edgecolor=COLOR_IBM, facecolor=COLOR_BOX_BG,
                    linestyle=(0, (3, 1.5)))
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=10, color=COLOR_IBM)

vz_box(GATE_X_IBM, qubit_y_plus,  r"$R_z(+\varphi)$")
vz_box(GATE_X_IBM, qubit_y_minus, r"$R_z(-\varphi)$")

# Below the circuit: descriptive text
ax.text(25, 45,
        "Each $R_z$ is a virtual-Z frame change\n"
        r"(relabelling of the rotating frame)" "\n"
        "— zero gate time, zero gate error —",
        ha="center", va="top", fontsize=9.5, color=COLOR_IBM)

# Depth tag
depth_box_ibm = Rectangle((6.5, 26), 37, 6, linewidth=1.5,
                           edgecolor=COLOR_IBM, facecolor="#EAF0F7")
ax.add_patch(depth_box_ibm)
ax.text(25, 29,
        r"Transpiled depth 6 for any $n$-step Floquet cycle",
        ha="center", va="center", fontsize=10.5, color=COLOR_IBM, fontweight="bold")

# Native basis
ax.text(25, 18.5,
        r"native single-qubit basis: $\{\sqrt{X},\, X,\, R_z\}$",
        ha="center", va="center", fontsize=9, color="#555", style="italic")

# ─────────────────── RIGHT: Cirq PhXZ (depth 2) ───────────────────
right_box = FancyBboxPatch((54, 12), 42, 67,
                            boxstyle="round,pad=0.5,rounding_size=1.0",
                            linewidth=1.4, edgecolor=COLOR_GOOGLE,
                            facecolor="white")
ax.add_patch(right_box)

ax.text(75, 75,
        "compiles to one PhXZ per qubit",
        ha="center", va="center", fontsize=10.5, color=COLOR_GOOGLE, style="italic")

# Circuit diagram — qubit lines split around each gate box
LEFT_X_R, RIGHT_X_R = 60, 91
GATE_X_GOOGLE = 75
GATE_HW_G = 8
ax.plot([LEFT_X_R, GATE_X_GOOGLE - GATE_HW_G], [qubit_y_plus,  qubit_y_plus],  color="black", lw=1.2)
ax.plot([LEFT_X_R, GATE_X_GOOGLE - GATE_HW_G], [qubit_y_minus, qubit_y_minus], color="black", lw=1.2)
ax.plot([GATE_X_GOOGLE + GATE_HW_G, RIGHT_X_R], [qubit_y_plus,  qubit_y_plus],  color="black", lw=1.2)
ax.plot([GATE_X_GOOGLE + GATE_HW_G, RIGHT_X_R], [qubit_y_minus, qubit_y_minus], color="black", lw=1.2)
ax.text(58, qubit_y_plus,  r"$q^+$", ha="right", va="center", fontsize=11)
ax.text(58, qubit_y_minus, r"$q^-$", ha="right", va="center", fontsize=11)

def phxz_box(x, y, label):
    box = Rectangle((x - GATE_HW_G, y - 2.5), 2*GATE_HW_G, 5, linewidth=1.4,
                    edgecolor=COLOR_GOOGLE, facecolor=COLOR_BOX_BG)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=10, color=COLOR_GOOGLE)

phxz_box(GATE_X_GOOGLE, qubit_y_plus,  r"$\mathrm{PhXZ}(a_+, x, z_+)$")
phxz_box(GATE_X_GOOGLE, qubit_y_minus, r"$\mathrm{PhXZ}(a_-, x, z_-)$")

ax.text(75, 45,
        "Cirq optimiser merges the entire\n"
        r"$n$-step Floquet cycle into a single" "\n"
        r"PhXZ gate per qubit (~20 ns each)",
        ha="center", va="top", fontsize=9.5, color=COLOR_GOOGLE)

depth_box_google = Rectangle((56.5, 26), 37, 6, linewidth=1.5,
                              edgecolor=COLOR_GOOGLE, facecolor="#FBECEC")
ax.add_patch(depth_box_google)
ax.text(75, 29,
        r"Transpiled depth 2 independent of $n$",
        ha="center", va="center", fontsize=10.5, color=COLOR_GOOGLE, fontweight="bold")

ax.text(75, 18.5,
        r"native single-qubit basis: $\{\mathrm{PhXZ},\, \mathrm{CZ}\}$",
        ha="center", va="center", fontsize=9, color="#555", style="italic")

# ─────────────────── BOTTOM: shared takeaway ───────────────────
takeaway_box = FancyBboxPatch((4, 1.5), 92, 8,
                               boxstyle="round,pad=0.5,rounding_size=0.8",
                               linewidth=1.0, edgecolor="#888",
                               facecolor="#FAFAFA")
ax.add_patch(takeaway_box)
ax.text(50, 7.0,
        "On both architectures the P gate is " r"$\bf{native}$"
        " — zero two-qubit gates, zero additional calibration, zero hardware modification.",
        ha="center", va="center", fontsize=10.5, color="#222")
ax.text(50, 3.6,
        r"Every superconducting quantum processor since the introduction of the virtual-$Z$ frame change implements the merkabit's defining operation.",
        ha="center", va="center", fontsize=9.5, color="#444", style="italic")

plt.tight_layout()
HERE = os.path.dirname(os.path.abspath(__file__))
out_png = os.path.join(HERE, "fig1_p_gate_decomposition.png")
out_pdf = os.path.join(HERE, "fig1_p_gate_decomposition.pdf")
plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.savefig(out_pdf, bbox_inches="tight")
print(f"Wrote {out_png}")
print(f"Wrote {out_pdf}")
