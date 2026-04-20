#!/usr/bin/env python3
"""
F-vs-tau on the 3-node triangle, quantum-trajectory MC with hand-built
IBM-realistic noise.

Path B counterpart to tau_sweep_noisy_qiskit.py. Adapts the 7-node
hexagonal cell trajectory simulator from
  https://github.com/SelinaAliens/The_Merkabit/multi_merkabit_cell_noise.py
to the 3-node triangle and runs the same paired vs P-removed contrast
the hardware uses.

Why a third simulation?
-----------------------
The noisy Qiskit run (FakeSherbrooke noise model) failed to reproduce
the hardware tau direction-flip. Two possible reasons:
  (a) the Qiskit calibrated noise model is INCOHERENT-only - it captures
      depolarising, T1/T2, readout, but not coherent ZZ crosstalk between
      forward and inverse spinors of the same merkabit, and not
      inter-merkabit ZZ between neighbouring nodes;
  (b) the signature is genuinely a hardware-only artifact (drift,
      readout asymmetry).

This script tests (a) directly. The trajectory MC carries two extra
physics channels the Qiskit run does not:
  - INTRA-merkabit ZZ: 30 kHz coherent coupling between forward and
    inverse spinors of the same merkabit (the "merkabit signature"
    that the P gate is supposed to interact with);
  - INTER-merkabit ZZ: 8 kHz coherent coupling between adjacent
    merkabits' forward spinors;
  - Burst (correlated) errors: P(neighbour error | this errored) = 5%.

Calibration: IBM Brisbane defaults from The_Merkabit repo:
  T1_centre = 220 us, T2_centre = 170 us, gate = 35 ns,
  gate_err_centre = 2.5e-4, gate_err_periph = 4e-4.

If THIS reproduces the tau direction-flip, the signature is coherent
ZZ-mediated. If it does not, the signature is most likely a hardware
artifact (drift between sessions, readout asymmetry on the specific
9 qubits used).

Output
------
- ../data/tau_sweep_lindblad_triangle.csv : (tau, paired, seed,
    fano, mean_weight, n_traj, det_rate)
- printed table comparing DeltaF vs hardware at tau in {1, 3, 5}
"""
import os, sys, csv, time
from pathlib import Path
from collections import defaultdict

import numpy as np

# Re-use the noise model + apply_* functions from The_Merkabit
TM_REPO = r"C:\Users\selin\The_Merkabit"
sys.path.insert(0, TM_REPO)
from multi_merkabit_cell_noise import (
    MultiMerkabitNoiseModel,
    apply_intra_noise,
    apply_inter_crosstalk,
    apply_burst_errors,
    PSI_PLUS,
    coherence,
    PAULIS, I2, X, Y, Z,
    T as FLOQUET_T,        # 12
    STEP_PHASE,            # 2*pi/12
    GATES, NUM_GATES,
)

# ---------------------------------------------------------------------------
# 3-node triangle (matches TriangleCell in run_rotation_gap_hardware.py)
# ---------------------------------------------------------------------------
class TriangleCell:
    """3-merkabit triangle, chirality {0, +1, -1}, 3 mutual edges."""
    def __init__(self):
        self.num_nodes = 3
        self.chirality = [0, +1, -1]
        self.edges = [(0, 1), (0, 2), (1, 2)]
        self.num_edges = 3
        self.neighbours = defaultdict(list)
        for i, j in self.edges:
            self.neighbours[i].append(j)
            self.neighbours[j].append(i)
        # MultiMerkabitNoiseModel needs is_interior + centre + nodes
        self.is_interior = [True, False, False]   # treat node 0 as centre
        self.centre = 0
        self.nodes = [(0, 0), (1, 0), (0, 1)]
        self.sublattice = [0, 1, 2]

# ---------------------------------------------------------------------------
# Per-node, paired/control-aware Floquet step unitary
# ---------------------------------------------------------------------------
def get_gate_angles_node(t_step, absent_idx):
    """
    Same gate-angle formula as run_rotation_gap_hardware.py:
      p   = 2pi/12
      sym = 2pi/36
      rx  = sym * (1 + 0.5 cos(omega))
      rz  = sym * (1 + 0.5 cos(omega + 2pi/3))
      multipliers per absent-gate label.
    """
    p   = STEP_PHASE
    sym = STEP_PHASE / 3
    omega = 2 * np.pi * t_step / FLOQUET_T
    rx = sym * (1.0 + 0.5 * np.cos(omega))
    rz = sym * (1.0 + 0.5 * np.cos(omega + 2 * np.pi / 3))
    label = GATES[absent_idx]
    if   label == 'S': rz *= 0.4;  rx *= 1.3
    elif label == 'R': rx *= 0.4;  rz *= 1.3
    elif label == 'T': rx *= 0.7;  rz *= 0.7
    elif label == 'P': p  *= 0.6;  rx *= 1.8;  rz *= 1.5
    return p, rz, rx


def step_unitary_node(t_step, base, chirality, paired, noise_angle=0.0, rng=None):
    """
    Build the 4x4 unitary acting on one merkabit's (forward, inverse)
    pair at Floquet sub-step t_step, given its (base, chirality).
    paired=True : asymmetric P, the merkabit signature
    paired=False: P removed (matches hardware control)
    """
    absent_idx = (base + chirality * t_step) % NUM_GATES
    p_a, rz_a, rx_a = get_gate_angles_node(t_step, absent_idx)
    if noise_angle > 0 and rng is not None:
        p_a  += noise_angle * rng.standard_normal()
        rz_a += noise_angle * rng.standard_normal()
        rx_a += noise_angle * rng.standard_normal()

    # P gate
    if paired:
        Pf = np.diag([np.exp( 1j*p_a/2), np.exp(-1j*p_a/2)])
        Pi = np.diag([np.exp(-1j*p_a/2), np.exp( 1j*p_a/2)])
        U_P = np.kron(Pf, Pi)
    else:
        U_P = np.eye(4, dtype=complex)

    # Symmetric Rz on both spinors
    Rz = np.diag([np.exp(-1j*rz_a/2), np.exp(1j*rz_a/2)])
    U_Rz = np.kron(Rz, Rz)

    # Symmetric Rx on both spinors
    c, s = np.cos(rx_a/2), -1j*np.sin(rx_a/2)
    Rx = np.array([[c, s], [s, c]], dtype=complex)
    U_Rx = np.kron(Rx, Rx)

    return U_Rx @ U_Rz @ U_P


# ---------------------------------------------------------------------------
# Per-edge per-round syndrome sampling
# ---------------------------------------------------------------------------
def measure_qu_marginal(psi):
    """P(forward spinor = |1>) given a 4-component state |psi> = sum c_uv |u,v>."""
    # |psi> ordered as [|00>, |01>, |10>, |11>] (kron(forward, inverse))
    p1 = abs(psi[2])**2 + abs(psi[3])**2
    return float(np.real(p1))


def sample_syndrome(states, cell, rng):
    """One round of syndrome extraction.
    For each edge (i,j), sample qu_i, qu_j ~ Bernoulli(p1) independently
    and return the parity bit qu_i XOR qu_j. This is the trajectory-MC
    analogue of CX(qu_i, anc); CX(qu_j, anc); measure(anc).
    Returns a list of bits (one per edge)."""
    p1 = [measure_qu_marginal(states[i]) for i in range(cell.num_nodes)]
    bits = []
    for (i, j) in cell.edges:
        qi = 1 if rng.random() < p1[i] else 0
        qj = 1 if rng.random() < p1[j] else 0
        bits.append(qi ^ qj)
    return bits


# ---------------------------------------------------------------------------
# One trajectory: tau Floquet periods with syndrome sampling each period
# ---------------------------------------------------------------------------
def evolve_one_trajectory(cell, nm, base_assignment, tau, paired,
                           coherent_noise, rng):
    """
    Run a single quantum trajectory for tau Floquet periods on the
    triangle. Each period:
      - 12 sub-steps of (gate unitary + intra-noise + burst + ZZ inter)
      - At end of period: sample syndrome bits per edge
    Returns syndrome bitstring of length tau * num_edges.
    """
    # Initialise: forward spinors in |+>, inverse spinors in |0>
    # (matches build_triangle_circuit which puts H on qu, leaves qv in |0>)
    psi0 = np.kron(np.array([1, 1], dtype=complex)/np.sqrt(2),
                   np.array([1, 0], dtype=complex))
    states = [psi0.copy() for _ in range(cell.num_nodes)]

    syndrome_bits = []
    for t_period in range(tau):
        for k in range(FLOQUET_T):
            errored_this_step = set()
            for i in range(cell.num_nodes):
                base = base_assignment[i]
                chi = cell.chirality[i]
                U_k = step_unitary_node(k, base, chi, paired,
                                         noise_angle=coherent_noise, rng=rng)
                states[i] = U_k @ states[i]
                states[i] /= np.linalg.norm(states[i])
                # 3 sub-gate noise applications per step (matches existing code)
                for _ in range(3):
                    states[i], errored = apply_intra_noise(states[i], i, nm, rng)
                    if errored:
                        errored_this_step.add(i)
            if errored_this_step:
                states = apply_burst_errors(states, errored_this_step, cell, nm, rng)
            states = apply_inter_crosstalk(states, cell, nm, rng)
            for i in range(cell.num_nodes):
                states[i] /= np.linalg.norm(states[i])
        # End of period: sample syndrome
        round_bits = sample_syndrome(states, cell, rng)
        syndrome_bits.extend(round_bits)

    return syndrome_bits


# ---------------------------------------------------------------------------
# Aggregate Fano over N_traj trajectories
# ---------------------------------------------------------------------------
def run_config(cell, nm, base_assignment, tau, paired,
                n_traj, base_seed, coherent_noise=0.0):
    weights = np.zeros(n_traj, dtype=float)
    detected = 0
    for k in range(n_traj):
        rng = np.random.default_rng(base_seed * 1_000_003 + k)
        bits = evolve_one_trajectory(cell, nm, base_assignment, tau, paired,
                                       coherent_noise, rng)
        w = sum(bits)
        weights[k] = w
        if w > 0:
            detected += 1
    mean_w = float(np.mean(weights))
    var_w  = float(np.var(weights, ddof=1))
    fano = var_w / mean_w if mean_w > 1e-10 else float('nan')
    return {
        "fano": fano,
        "mean_weight": mean_w,
        "var_weight": var_w,
        "detection_rate": detected / n_traj,
        "n_traj": n_traj,
    }


# ---------------------------------------------------------------------------
# Main sweep (guarded so the module can be imported by other scripts without
# kicking off the full 25-minute sweep)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    SHOTS_PER_CONFIG = 1500     # quantum trajectories per (tau, paired, seed)
    SEEDS            = list(range(1, 6))    # 5 outer seeds for trajectory variance
    TAU_VALUES       = [1, 2, 3, 4, 5, 6, 7]
    COHERENT_NOISE   = 0.05 * STEP_PHASE   # coherent control noise (matches T1 test)

    HARDWARE = {
        1: {"paired": 0.654, "control": 0.613},
        3: {"paired": 0.871, "control": 0.600},
        5: {"paired": 0.506, "control": 0.564},
    }

    OUT_CSV = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "data", "tau_sweep_lindblad_triangle.csv"
    )

    # Build cell + noise model
    cell = TriangleCell()
    nm = MultiMerkabitNoiseModel(
        cell, name="IBM Brisbane (triangle adaptation)"
    )

    # Pick a fixed base assignment (must satisfy adjacent-different constraint).
    # Triangle has 3 nodes all pairwise adjacent, so all 3 bases must differ.
    base_assignment = [0, 1, 2]   # S, R, T at nodes 0, 1, 2
    # Verify
    for i, j in cell.edges:
        assert base_assignment[i] != base_assignment[j], "invalid base assignment"

    print("=" * 78)
    print("Quantum-trajectory MC tau-sweep on the 3-node triangle")
    print(f"Noise model    : {nm.name}")
    print(f"  T1/T2 centre : {nm.node_params[0]['T1_us']:.0f}us / {nm.node_params[0]['T2_us']:.0f}us")
    print(f"  T1/T2 periph : {nm.node_params[1]['T1_us']:.0f}us / {nm.node_params[1]['T2_us']:.0f}us")
    print(f"  ZZ intra     : {nm.zz_intra_phase:.4f} rad/gate (30 kHz)")
    print(f"  ZZ inter     : {nm.zz_inter_phase:.4f} rad/gate (8 kHz)")
    print(f"  Burst prob   : {nm.burst_prob}")
    print(f"Trajectories   : {SHOTS_PER_CONFIG} per (tau, paired, seed)")
    print(f"Outer seeds    : {len(SEEDS)}")
    print(f"Tau sweep      : {TAU_VALUES}")
    print(f"Base assignment: {[GATES[a] for a in base_assignment]}  "
          f"chirality={cell.chirality}")
    print("=" * 78)

    t0 = time.time()
    rows = []
    print(f"\n{'tau':>3} | {'paired':>6} | {'seed':>4} | {'F':>8} | "
          f"{'<w>':>6} | {'det':>6} | {'sec':>5}")
    print("-" * 56)

    for tau in TAU_VALUES:
        for paired in [True, False]:
            for seed in SEEDS:
                t1 = time.time()
                r = run_config(cell, nm, base_assignment, tau, paired,
                               n_traj=SHOTS_PER_CONFIG, base_seed=seed,
                               coherent_noise=COHERENT_NOISE)
                dt = time.time() - t1
                rows.append({
                    "tau": tau, "paired": int(paired), "seed": seed,
                    "fano": r["fano"], "mean_weight": r["mean_weight"],
                    "detection": r["detection_rate"], "n_traj": r["n_traj"],
                })
                print(f"{tau:>3} | {str(paired):>6} | {seed:>4} | "
                      f"{r['fano']:>8.4f} | {r['mean_weight']:>6.3f} | "
                      f"{r['detection_rate']:>6.3f} | {dt:>5.1f}")
        elapsed = time.time() - t0
        print(f"  --- tau={tau} done ({elapsed:.0f}s elapsed) ---")

    # Write CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {os.path.normpath(OUT_CSV)}")

    # Summary table vs hardware
    print()
    print("=" * 92)
    print("LINDBLAD TRIANGLE MC vs HARDWARE")
    print("=" * 92)
    print(f"{'tau':>3} | {'F_paired (mu+/-sigma)':>22} | {'F_control (mu+/-sigma)':>22} | "
          f"{'DeltaF (sim)':>14} | {'DeltaF (HW)':>11} | sign match")
    print("-" * 92)

    for tau in TAU_VALUES:
        p_vals = [row["fano"] for row in rows if row["tau"] == tau and row["paired"] == 1]
        c_vals = [row["fano"] for row in rows if row["tau"] == tau and row["paired"] == 0]
        p_mean, p_std = float(np.mean(p_vals)), float(np.std(p_vals, ddof=1))
        c_mean, c_std = float(np.mean(c_vals)), float(np.std(c_vals, ddof=1))
        delta = p_mean - c_mean
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
    print(f"Total time: {time.time() - t0:.0f}s")
