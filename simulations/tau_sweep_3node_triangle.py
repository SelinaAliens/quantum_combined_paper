#!/usr/bin/env python3
"""
F-vs-τ sweep on the 3-node hex triangle cell.

Tests whether the τ direction-flip in §3.3 (paired > control at τ = 1, 3;
paired < control at τ = 5) is structural (predicted by the classical Monte
Carlo) or a hardware-only quirk that happened to land at τ = 5.

Sweep:  τ ∈ {1, 2, 3, 4, 5, 6, 7}, paired ∈ {True, False}, 30 PRNG seeds.
Cell:   3-node hex triangle (matches the §3.3 hardware experiment).
Noise:  ε = 0.10 (canonical paper value).
Shots:  20 000 per (τ, paired, seed) configuration.

Output: ../data/tau_sweep_3node_triangle.csv with one row per
(τ, paired, seed) configuration plus a printed summary table comparing
the MC predictions to the §3.3 hardware values.

Run from this directory:
    python tau_sweep_3node_triangle.py
"""
import os, sys, csv, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_scaling_comparison as sim
import numpy as np

# Hardware values from §3.3 (HARDWARE-RESULTS.md Table 5)
HARDWARE = {
    1: {"paired": 0.654, "control": 0.613},
    3: {"paired": 0.871, "control": 0.600},
    5: {"paired": 0.506, "control": 0.564},
}

EPS = 0.10
SHOTS = 20000
SEEDS = list(range(1, 31))
TAU_VALUES = [1, 2, 3, 4, 5, 6, 7]

OUT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "tau_sweep_3node_triangle.csv"
)

cell = sim.build_hex_triangle()
print(f"Cell: {cell['name']}  ({cell['num_nodes']} nodes, {cell['num_edges']} edges, "
      f"chirality={cell['chirality']})")
print(f"Sweep: \u03c4 \u2208 {TAU_VALUES}, \u03b5 = {EPS}, shots = {SHOTS:,}, seeds = {len(SEEDS)}")
print(f"Total runs: {len(TAU_VALUES) * 2 * len(SEEDS)}")
print()

t0 = time.time()
rows = []
for tau in TAU_VALUES:
    for seed in SEEDS:
        for paired in [True, False]:
            r = sim.simulate(cell, tau, EPS, SHOTS, seed=seed, paired=paired)
            rows.append({
                "tau": tau, "paired": int(paired), "seed": seed,
                "fano": r["fano"], "detection": r["detection"],
                "mean_weight": r["mean_weight"],
            })
    elapsed = time.time() - t0
    print(f"  \u03c4 = {tau} done ({elapsed:.0f}s elapsed)")

# Write CSV
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nWrote {len(rows)} rows to {os.path.normpath(OUT_CSV)}")

# Aggregate
print()
print("=" * 90)
print(f"RESULTS: 3-node hex triangle, \u03b5 = 0.10, {SHOTS:,} shots/seed, {len(SEEDS)} seeds")
print("=" * 90)
print(f"{'\u03c4':>2} | {'F_paired (mean \u00b1 std)':>22} | {'F_control (mean \u00b1 std)':>22} | "
      f"{'\u0394F = paired \u2212 control':>22} | {'HW \u0394F':>10}")
print("-" * 95)

summary = {}
for tau in TAU_VALUES:
    p_vals = [row["fano"] for row in rows if row["tau"] == tau and row["paired"] == 1]
    c_vals = [row["fano"] for row in rows if row["tau"] == tau and row["paired"] == 0]
    p_mean, p_std = np.mean(p_vals), np.std(p_vals, ddof=1)
    c_mean, c_std = np.mean(c_vals), np.std(c_vals, ddof=1)
    delta_mean = p_mean - c_mean
    delta_std = np.sqrt(p_std**2 + c_std**2)  # standard error on the difference
    hw_delta = HARDWARE.get(tau, {})
    hw_str = f"{hw_delta['paired'] - hw_delta['control']:+.3f}" if hw_delta else "(no hw)"
    summary[tau] = {"p_mean": p_mean, "p_std": p_std, "c_mean": c_mean, "c_std": c_std,
                    "delta_mean": delta_mean, "delta_std": delta_std}
    print(f"{tau:>2} | {p_mean:>10.4f} \u00b1 {p_std:>8.4f}    | {c_mean:>10.4f} \u00b1 {c_std:>8.4f}    | "
          f"{delta_mean:+8.4f} \u00b1 {delta_std:>7.4f}    | {hw_str:>10}")

# Find the reversal point in the MC
print()
print("=" * 90)
print("REVERSAL ANALYSIS")
print("=" * 90)
prev_sign = None
for tau in TAU_VALUES:
    sign = "+" if summary[tau]["delta_mean"] > 0 else "\u2212"
    print(f"  \u03c4 = {tau}: \u0394F = {summary[tau]['delta_mean']:+.4f}  ({sign})")
    if prev_sign and prev_sign != sign:
        print(f"    \u2192 reversal between \u03c4 = {tau - 1} and \u03c4 = {tau}")
    prev_sign = sign

# Hardware comparison
print()
print("Hardware vs MC \u0394F sign:")
for tau in [1, 3, 5]:
    hw = HARDWARE[tau]
    hw_delta = hw["paired"] - hw["control"]
    mc_delta = summary[tau]["delta_mean"]
    hw_sign = "+" if hw_delta > 0 else "\u2212"
    mc_sign = "+" if mc_delta > 0 else "\u2212"
    match = "\u2713" if hw_sign == mc_sign else "\u2717"
    print(f"  \u03c4 = {tau}: HW \u0394F = {hw_delta:+.3f} ({hw_sign})  vs  "
          f"MC \u0394F = {mc_delta:+.3f} ({mc_sign})  {match}")

print(f"\nTotal time: {time.time() - t0:.0f}s")
