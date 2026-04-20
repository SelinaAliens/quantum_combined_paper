#!/usr/bin/env python3
"""
ZZ-on vs ZZ-off comparison for the Lindblad-style trajectory MC on the
3-merkabit triangle.

Tests whether the paired-below-control sign (ΔF < 0) survives when the
coherent ZZ channels are removed from the noise model. If the sign
survives, the merkabit signature is produced by the depolarising/
amplitude-damping channels alone and the "coherent ZZ is the mechanism"
claim weakens. If the sign reverses to paired > control (matching the
incoherent Qiskit-Aer result), the ZZ-on vs ZZ-off contrast within a
single simulator framework cleanly identifies coherent ZZ as the
mechanism.

Same setup as tau_sweep_lindblad_triangle.py but runs each (tau, paired)
configuration TWICE with paired RNG seeds — once with the IBM Brisbane
ZZ budget (intra 30 kHz, inter 8 kHz) and once with ZZ disabled
(intra=0, inter=0). All other noise channels (T1/T2, depolarising,
burst-error correlation, readout) are unchanged. Paired RNG seeds make
the on/off comparison directly within-trajectory comparable.

Reduced grid for speed: tau ∈ {1, 3, 5, 7}, 5 seeds, 1500 trajectories
per (tau, paired, seed, zz_state) — ~60 000 trajectories total,
estimated ~10 minutes wall time.

Output:
    ../data/tau_sweep_lindblad_zz_onoff.csv  : tidy long-form table
    printed table with ΔF (ZZ on) vs ΔF (ZZ off) at each tau
"""
import os, sys, csv, time
from pathlib import Path
import numpy as np

TM_REPO = r"C:\Users\selin\The_Merkabit"
sys.path.insert(0, TM_REPO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_merkabit_cell_noise import (
    MultiMerkabitNoiseModel, GATES, NUM_GATES,
    STEP_PHASE, T as FLOQUET_T,
)
# Re-use the Triangle-cell + per-node-aware step unitary + syndrome
# sampler from tau_sweep_lindblad_triangle.py
from tau_sweep_lindblad_triangle import (
    TriangleCell, step_unitary_node, sample_syndrome, evolve_one_trajectory,
)

# --- Config ---
SHOTS_PER_CONFIG = 1500
SEEDS            = list(range(1, 6))    # 5 outer seeds
TAU_VALUES       = [1, 3, 5, 7]
COHERENT_NOISE   = 0.05 * STEP_PHASE

OUT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "tau_sweep_lindblad_zz_onoff.csv"
)

cell = TriangleCell()
base_assignment = [0, 1, 2]    # S, R, T at nodes 0, 1, 2

# Two noise models, identical except for ZZ:
nm_zz_on = MultiMerkabitNoiseModel(
    cell, name="IBM Brisbane (ZZ on, full Lindblad)",
    zz_intra_kHz=30, zz_inter_kHz=8,
)
nm_zz_off = MultiMerkabitNoiseModel(
    cell, name="IBM Brisbane (ZZ off, depol + T1/T2 + readout only)",
    zz_intra_kHz=0, zz_inter_kHz=0,
)

print("=" * 80)
print("ZZ-ON vs ZZ-OFF Lindblad comparison on the 3-merkabit triangle")
print("=" * 80)
print(f"Cell        : {cell.num_nodes} nodes, chirality={cell.chirality}")
print(f"Trajectories: {SHOTS_PER_CONFIG} per (tau, paired, seed, zz_state)")
print(f"Outer seeds : {len(SEEDS)}")
print(f"Tau sweep   : {TAU_VALUES}")
print(f"Total runs  : {len(TAU_VALUES) * 2 * len(SEEDS) * 2 * SHOTS_PER_CONFIG:,} trajectories")
print()
print("ZZ-on noise model:")
for line in nm_zz_on.summary().split('\n'):
    print('  ', line)
print()
print("ZZ-off noise model (intra=0, inter=0, all other channels unchanged):")
for line in nm_zz_off.summary().split('\n'):
    print('  ', line)
print()

def run_config(nm, base_seed, tau, paired, n_traj):
    weights = np.zeros(n_traj, dtype=float)
    for k in range(n_traj):
        rng = np.random.default_rng(base_seed * 1_000_003 + k)
        bits = evolve_one_trajectory(cell, nm, base_assignment, tau, paired,
                                       COHERENT_NOISE, rng)
        weights[k] = sum(bits)
    m = float(np.mean(weights))
    v = float(np.var(weights, ddof=1))
    fano = v / m if m > 1e-10 else float('nan')
    return {"fano": fano, "mean_weight": m, "var_weight": v}

t0 = time.time()
rows = []
print(f"\n{'tau':>3} | {'paired':>6} | {'seed':>4} | {'ZZ on F':>8} | {'ZZ off F':>9} | {'ΔF(on-off)':>10} | {'sec':>5}")
print("-" * 70)

for tau in TAU_VALUES:
    for paired in [True, False]:
        for seed in SEEDS:
            t1 = time.time()
            r_on  = run_config(nm_zz_on,  seed, tau, paired, SHOTS_PER_CONFIG)
            r_off = run_config(nm_zz_off, seed, tau, paired, SHOTS_PER_CONFIG)
            dt = time.time() - t1
            rows.append({
                "tau": tau, "paired": int(paired), "seed": seed,
                "zz_on_fano":  r_on["fano"],  "zz_on_mean":  r_on["mean_weight"],
                "zz_off_fano": r_off["fano"], "zz_off_mean": r_off["mean_weight"],
            })
            print(f"{tau:>3} | {str(paired):>6} | {seed:>4} | "
                  f"{r_on['fano']:>8.4f} | {r_off['fano']:>9.4f} | "
                  f"{r_on['fano'] - r_off['fano']:>+10.4f} | {dt:>5.1f}")
    print(f"  --- tau={tau} done ({time.time() - t0:.0f}s elapsed) ---")

# Write CSV
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nWrote {len(rows)} rows to {os.path.normpath(OUT_CSV)}")

# --- Summary: ΔF (paired - control) under ZZ-on vs ZZ-off ---
print()
print("=" * 88)
print("HEADLINE: ΔF = F_paired − F_control, ZZ-on vs ZZ-off")
print("=" * 88)
print(f"{'tau':>3} | {'F_paired (on)':>14} | {'F_ctrl (on)':>12} | {'ΔF(on)':>9} | "
      f"{'F_paired (off)':>15} | {'F_ctrl (off)':>13} | {'ΔF(off)':>9} | sign")
print("-" * 110)

for tau in TAU_VALUES:
    p_on  = [r["zz_on_fano"]  for r in rows if r["tau"] == tau and r["paired"] == 1]
    c_on  = [r["zz_on_fano"]  for r in rows if r["tau"] == tau and r["paired"] == 0]
    p_off = [r["zz_off_fano"] for r in rows if r["tau"] == tau and r["paired"] == 1]
    c_off = [r["zz_off_fano"] for r in rows if r["tau"] == tau and r["paired"] == 0]
    p_on_m,  c_on_m  = float(np.mean(p_on)),  float(np.mean(c_on))
    p_off_m, c_off_m = float(np.mean(p_off)), float(np.mean(c_off))
    d_on  = p_on_m  - c_on_m
    d_off = p_off_m - c_off_m
    sign_on  = "+" if d_on  > 0 else "−"
    sign_off = "+" if d_off > 0 else "−"
    flips = "FLIPS" if sign_on != sign_off else "same"
    print(f"{tau:>3} | {p_on_m:>14.4f} | {c_on_m:>12.4f} | {d_on:>+9.4f} | "
          f"{p_off_m:>15.4f} | {c_off_m:>13.4f} | {d_off:>+9.4f} | {flips}")

print()
print("Reading the table")
print("-" * 88)
print("If ΔF(off) flips sign relative to ΔF(on), the coherent ZZ channel is responsible")
print("for the paired-below-control gap. If ΔF(off) keeps the sign, depolarising +")
print("amplitude-damping noise alone produces the gap and the ZZ mechanism claim weakens.")
print(f"\nTotal time: {time.time() - t0:.0f}s")
