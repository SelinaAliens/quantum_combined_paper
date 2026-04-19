#!/usr/bin/env python3
"""
F-vs-tau on the 3-node triangle, noisy Qiskit simulation.

Re-uses the exact circuit builder from the hardware experiment
(merkabit_hardware_test/experiments/run_rotation_gap_hardware.py)
and runs it through AerSimulator with the FakeSherbrooke noise model
(Eagle r3, 127 qubits, same family/revision as ibm_strasbourg).

Why this exists
---------------
The classical Monte Carlo in `sim_scaling_comparison.py` uses
chirality=0 as its control, while the hardware experiment uses
"P gate removed" as its control. Those are *different* controls,
so the classical MC's failure to reproduce the hardware tau direction
flip (paired > control at tau=1, 3; paired < control at tau=5) is
not a falsification of the merkabit signature - it is a scope
mismatch.

This script closes the gap: same circuit, same paired/control
contrast as the hardware, with a calibrated Eagle r3 noise model
in place of the chip itself.

Output
------
- ../data/tau_sweep_noisy_qiskit.csv : one row per (tau, paired, seed)
- printed comparison table vs hardware DeltaF at tau in {1, 3, 5}
"""
import os, sys, csv, time
from pathlib import Path
from collections import defaultdict

import numpy as np

# Pull in the hardware circuit builder + analyzer
HW_REPO = r"C:\Users\selin\merkabit_hardware_test"
sys.path.insert(0, os.path.join(HW_REPO, "experiments"))
from run_rotation_gap_hardware import (
    TriangleCell,
    find_valid_assignment,
    build_triangle_circuit,
    analyze_syndrome,
    GATES,
)

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

# --- Configuration ----------------------------------------------------------
SHOTS      = 8192
SEEDS      = list(range(1, 11))   # 10 seeds: each seed re-randomises noise
TAU_VALUES = [1, 2, 3, 4, 5, 6, 7]
OPT_LEVEL  = 1                    # match hardware transpiler setting

# Hardware reference (HARDWARE-RESULTS.md Table 5, ibm_strasbourg)
HARDWARE = {
    1: {"paired": 0.654, "control": 0.613},
    3: {"paired": 0.871, "control": 0.600},
    5: {"paired": 0.506, "control": 0.564},
}

OUT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "tau_sweep_noisy_qiskit.csv"
)

# --- Backend / noise model --------------------------------------------------
# Strategy: extract the Eagle r3 noise (T1/T2, gate errors, readout) from
# FakeSherbrooke, but apply it to a generic AerSimulator with a virtual
# 9-qubit register. This isolates the question "does the merkabit signature
# survive realistic Eagle r3 noise?" from the unrelated question "does this
# specific physical layout on this specific chip support a 9-qubit triangle
# without SWAPs?". The hardware run on ibm_strasbourg used a hand-picked
# layout (qubits 58-81); FakeSherbrooke's heavy-hex offset differs and that
# specific layout would force ~30+ SWAPs which would dominate the noise.
fake = FakeSherbrooke()
noise_model = NoiseModel.from_backend(fake)
sim_backend = AerSimulator(noise_model=noise_model)

print("=" * 78)
print("Noisy Qiskit tau-sweep on the 3-node triangle")
print(f"Noise source: FakeSherbrooke (Eagle r3, calibrated T1/T2, gate, readout)")
print(f"Backend     : generic AerSimulator with FakeSherbrooke noise model")
print(f"Stand-in for: ibm_strasbourg (Eagle r3, 127 qubits)")
print(f"Shots/seed  : {SHOTS:,}")
print(f"Seeds       : {len(SEEDS)} (re-randomises noise per run)")
print(f"Tau sweep   : {TAU_VALUES}")
print("=" * 78)

# --- Cell + assignment + layout ---------------------------------------------
cell = TriangleCell()
assignment = find_valid_assignment(cell, seed=42)
print(f"Cell        : {cell.num_nodes} nodes, {cell.num_edges} edges, "
      f"chirality={cell.chirality}")
print(f"Assignment  : {[GATES[a] for a in assignment]}")

# Compact virtual layout: 6 data (0-5) + 3 ancilla (6-8). The transpiler
# will route on the noise model's basis gates; with no coupling map
# constraint, no SWAPs are inserted, so depth reflects only the protocol
# itself plus single-qubit decompositions.
layout = {
    "node_qu":  {0: 0, 1: 2, 2: 4},
    "node_qv":  {0: 1, 1: 3, 2: 5},
    "edge_anc": {(0, 1): 6, (0, 2): 7, (1, 2): 8},
}
print(f"Layout      : virtual 9-qubit register (no SWAP overhead)")

# No coupling-map constraint: pass native_cx_dirs=None so the builder
# uses the standard CX(data->anc) Z-parity strategy on every edge.
native_dirs = None
print()

# --- Sweep ------------------------------------------------------------------
t0 = time.time()
rows = []
print(f"{'tau':>3} | {'paired':>6} | {'seed':>4} | {'F':>8} | "
      f"{'det':>6} | {'<w>':>6} | {'depth':>5}")
print("-" * 60)

for tau in TAU_VALUES:
    for paired in [True, False]:
        for seed in SEEDS:
            qc, _ = build_triangle_circuit(
                cell, assignment, layout, tau,
                paired=paired,
                native_cx_dirs=native_dirs,
            )
            qc_t = transpile(qc, sim_backend, optimization_level=OPT_LEVEL,
                             seed_transpiler=seed)
            depth = qc_t.depth()
            job = sim_backend.run(qc_t, shots=SHOTS, seed_simulator=seed)
            counts = job.result().get_counts()
            r = analyze_syndrome(counts, cell, tau)
            row = {
                "tau": tau, "paired": int(paired), "seed": seed,
                "fano": r["fano_factor"],
                "detection": r["detection_rate"],
                "mean_weight": r["mean_syndrome_weight"],
                "depth": depth,
            }
            rows.append(row)
            print(f"{tau:>3} | {str(paired):>6} | {seed:>4} | "
                  f"{r['fano_factor']:>8.4f} | "
                  f"{r['detection_rate']:>6.3f} | "
                  f"{r['mean_syndrome_weight']:>6.3f} | {depth:>5}")
    elapsed = time.time() - t0
    print(f"  --- tau={tau} done ({elapsed:.0f}s elapsed) ---")

# --- Write CSV --------------------------------------------------------------
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nWrote {len(rows)} rows to {os.path.normpath(OUT_CSV)}")

# --- Aggregate + compare to hardware ----------------------------------------
print()
print("=" * 90)
print(f"NOISY QISKIT vs HARDWARE: 3-node triangle, FakeSherbrooke "
      f"(Eagle r3 stand-in for ibm_strasbourg)")
print("=" * 90)
print(f"{'tau':>3} | {'F_paired (mu+/-sigma)':>22} | "
      f"{'F_control (mu+/-sigma)':>22} | "
      f"{'DeltaF (sim)':>14} | {'DeltaF (HW)':>11} | sign match")
print("-" * 100)

summary = {}
for tau in TAU_VALUES:
    p_vals = [row["fano"] for row in rows if row["tau"] == tau and row["paired"] == 1]
    c_vals = [row["fano"] for row in rows if row["tau"] == tau and row["paired"] == 0]
    p_mean, p_std = float(np.mean(p_vals)), float(np.std(p_vals, ddof=1))
    c_mean, c_std = float(np.mean(c_vals)), float(np.std(c_vals, ddof=1))
    delta = p_mean - c_mean
    delta_se = float(np.sqrt(p_std**2 / len(p_vals) + c_std**2 / len(c_vals)))
    summary[tau] = dict(p_mean=p_mean, p_std=p_std, c_mean=c_mean, c_std=c_std,
                        delta=delta, delta_se=delta_se)
    hw = HARDWARE.get(tau)
    if hw:
        hw_delta = hw["paired"] - hw["control"]
        sim_sign = "+" if delta > 0 else "-"
        hw_sign  = "+" if hw_delta > 0 else "-"
        match = "yes" if sim_sign == hw_sign else "NO"
        print(f"{tau:>3} | {p_mean:>10.4f} +/- {p_std:>6.4f}    | "
              f"{c_mean:>10.4f} +/- {c_std:>6.4f}    | "
              f"{delta:>+8.4f}      | {hw_delta:>+8.3f}   | {match:>10}")
    else:
        print(f"{tau:>3} | {p_mean:>10.4f} +/- {p_std:>6.4f}    | "
              f"{c_mean:>10.4f} +/- {c_std:>6.4f}    | "
              f"{delta:>+8.4f}      | {'(no HW)':>11}   | {'-':>10}")

print()
print("=" * 90)
print("Reading the table")
print("-" * 90)
print("DeltaF = F_paired - F_control. Hardware shows + at tau=1, + at tau=3,")
print("- at tau=5 (the direction flip). If the noisy Qiskit reproduces that")
print("sign pattern, the merkabit signature is structural under the canonical")
print("hardware control. If not, either the noise model is missing something")
print("(crosstalk, drift) or the signature was a hardware-only quirk.")
print(f"\nTotal time: {time.time() - t0:.0f}s")
