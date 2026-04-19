#!/usr/bin/env python3
"""
F-vs-τ at multiple ε values, 3-node hex triangle, paired vs control.
Tests whether ANY ε in the MC reproduces the hardware τ-dependent pattern.

Hardware at the 9-qubit triangle on ibm_strasbourg:
  τ=1: paired 0.654, control 0.613   (paired slightly higher)
  τ=3: paired 0.871, control 0.600   (paired MUCH higher)
  τ=5: paired 0.506, control 0.564   (paired finally lower — directional signal)
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_scaling_comparison as sim
import numpy as np

cell = sim.build_hex_triangle()
SHOTS = 20000
SEEDS = list(range(1, 21))   # 20 seeds for speed
TAU_VALUES = [1, 2, 3, 4, 5, 6, 7]
EPS_VALUES = [0.01, 0.05, 0.10, 0.20, 0.30]

HARDWARE = {1: 0.041, 3: 0.271, 5: -0.058}

print(f"3-node hex triangle, paired vs control, ε scan, {SHOTS:,} shots × {len(SEEDS)} seeds")
print(f"Hardware: ΔF(τ=1) = {HARDWARE[1]:+.3f}, ΔF(τ=3) = {HARDWARE[3]:+.3f}, ΔF(τ=5) = {HARDWARE[5]:+.3f}")
print()

t0 = time.time()
print(f"{'ε':>6} | " + " | ".join(f"τ={t:>2}" for t in TAU_VALUES))
print("-" * (8 + len(TAU_VALUES) * 13))

for eps in EPS_VALUES:
    deltas = []
    for tau in TAU_VALUES:
        p_vals = []
        c_vals = []
        for seed in SEEDS:
            p_vals.append(sim.simulate(cell, tau, eps, SHOTS, seed=seed, paired=True)["fano"])
            c_vals.append(sim.simulate(cell, tau, eps, SHOTS, seed=seed, paired=False)["fano"])
        delta = np.mean(p_vals) - np.mean(c_vals)
        deltas.append(delta)
    row = f"{eps:>6.2f} | " + " | ".join(f"{d:+7.3f}" for d in deltas)
    print(row)

print()
print("=" * 80)
print("Reading: each cell shows ΔF = F_paired − F_control at the given (ε, τ).")
print("Hardware τ=1 = +0.041, τ=3 = +0.271, τ=5 = −0.058 — find the closest match.")
print(f"Total time: {time.time() - t0:.0f}s")
