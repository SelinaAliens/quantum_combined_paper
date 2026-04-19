#!/usr/bin/env python3
"""
Seed-dispersion driver for sim_scaling_comparison.py
Runs the four headline Paper 26 cells across 30 PRNG seeds at tau=5, eps=0.10.

Reproduces ../data/seed_dispersion_30seeds.csv. ~5 minutes wall time.
Backs the F = 0.370 ± 0.026 number in §4.4 of the consolidation paper.

Usage:
    cd simulations/
    python seed_sweep_driver.py
"""
import os, sys, csv, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_scaling_comparison as sim
import numpy as np

CELLS = {
    "hex-r1-7n":   sim.build_hex_cell(1),
    "sq-3x3-9n":   sim.build_square_cell(3),
    "hex-r2-19n":  sim.build_hex_cell(2),
    "sq-4x4-16n":  sim.build_square_cell(4),
}

TAU = 5
EPS = 0.10
SHOTS = 20000
SEEDS = list(range(1, 31))  # seeds 1..30

OUT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "seed_dispersion_30seeds.csv"
)

print(f"Seed sweep: tau={TAU}, eps={EPS}, shots={SHOTS}, seeds={len(SEEDS)}")
print(f"Cells: {list(CELLS.keys())}")
print(f"Output: {os.path.normpath(OUT_CSV)}")
print()

rows = []
results = {name: {"paired": [], "control": []} for name in CELLS}
t0 = time.time()

for seed_i, seed in enumerate(SEEDS):
    for cell_name, cell in CELLS.items():
        r_p = sim.simulate(cell, TAU, EPS, SHOTS, seed=seed, paired=True)
        r_c = sim.simulate(cell, TAU, EPS, SHOTS, seed=seed, paired=False)
        results[cell_name]["paired"].append(r_p["fano"])
        results[cell_name]["control"].append(r_c["fano"])
        rows.append({
            "seed": seed,
            "cell": cell_name,
            "tau": TAU,
            "epsilon": EPS,
            "shots": SHOTS,
            "fano_paired": r_p["fano"],
            "fano_control": r_c["fano"],
            "detection_paired": r_p["detection"],
            "mean_weight_paired": r_p["mean_weight"],
        })
    elapsed = time.time() - t0
    eta = elapsed / (seed_i + 1) * (len(SEEDS) - seed_i - 1)
    print(f"  seed {seed:2d}/{SEEDS[-1]} done ({elapsed:.0f}s elapsed, {eta:.0f}s ETA)", flush=True)

# Write the CSV
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nWrote {len(rows)} rows to {os.path.normpath(OUT_CSV)}")

# Summary
print()
print("=" * 95)
print(f"RESULTS  ({len(SEEDS)} seeds, {SHOTS} shots/seed, tau={TAU}, eps={EPS})")
print("=" * 95)
print(f"{'Cell':>14} | {'F_paired (mean +/- std)':>28} | {'F_paired 95% CI':>22} | {'F_control (mean +/- std)':>28}")
print("-" * 105)

summary = {}
for cell_name in CELLS:
    p = np.array(results[cell_name]["paired"])
    c = np.array(results[cell_name]["control"])
    p_mean, p_std = p.mean(), p.std(ddof=1)
    c_mean, c_std = c.mean(), c.std(ddof=1)
    p_ci_lo, p_ci_hi = np.percentile(p, [2.5, 97.5])
    summary[cell_name] = {"p_mean": p_mean, "p_std": p_std}
    print(f"{cell_name:>14} | {p_mean:>10.4f} +/- {p_std:>7.4f}        | "
          f"[{p_ci_lo:.4f}, {p_ci_hi:.4f}]     | {c_mean:>10.4f} +/- {c_std:>7.4f}")

print()
print("Sub-Poissonian sigma test:")
for cell_name, s in summary.items():
    sigma_below = (1.0 - s["p_mean"]) / s["p_std"]
    print(f"  {cell_name:>14}: F_paired = {s['p_mean']:.4f} +/- {s['p_std']:.4f}  =>  {sigma_below:5.1f} sigma below F = 1")

print()
print("Single-seed reference (seed = 42, the value originally reported in Paper 26):")
for cell_name, cell in CELLS.items():
    r_p = sim.simulate(cell, TAU, EPS, SHOTS, seed=42, paired=True)
    delta_sigma = (r_p["fano"] - summary[cell_name]["p_mean"]) / summary[cell_name]["p_std"]
    print(f"  {cell_name:>14}: F (seed=42) = {r_p['fano']:.4f}  =>  delta from mean = {delta_sigma:+5.2f} sigma")

print()
print(f"Total wall time: {time.time()-t0:.0f}s")
