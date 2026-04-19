#!/usr/bin/env python3
"""
Angle-table perturbation control for the consolidation paper.

Tests whether the merkabit's predicted observables (P(|00>) at n=13 ~ 0.696,
pi-lock <ZZ> ~ 0.447, etc.) are SPECIFIC to the merkabit angle table or whether
"any 12-step Floquet protocol with similar magnitudes" would also produce them.

This is the angle-specialness defense for Quantum referees who suspect the
geometric origin (Appendix C) is just a post-hoc fit.

What we do
----------
1. Compute the merkabit's predicted observables on the dual-spinor pair (q+, q-)
   from Table 1a multipliers + the base formulas in section 2.4.

2. Generate N random perturbations of the 15 multipliers (5 absent gates x 3
   angle types) with two strategies:
   (a) "Shuffle": permute the 15 numbers randomly.
   (b) "Random": draw 15 iid Uniform(0.4, 1.8) values matching the original range.

3. For each perturbation, compute the same observables.

4. Report where the merkabit observables sit in the perturbed distribution.
   If the merkabit values are at extreme percentiles, that supports the
   "angles are special" claim. If they are typical, the framework defense
   weakens (but the empirical claims still hold via §3-§5 hardware data).

Mathematical setup
------------------
Single-qubit gates:
    R_z(theta) = diag(exp(-i theta/2), exp(+i theta/2))
    R_x(theta) = [[cos(theta/2), -i sin(theta/2)], [-i sin(theta/2), cos(theta/2)]]
    P(phi)    = R_z(+phi) (q+) tensor R_z(-phi) (q-)   <-- the merkabit signature

One Floquet step:
    U_step(k) = (R_x(rx_k) R_z(rz_k) (q+) tensor R_x(rx_k) R_z(rz_k) (q-)) * P(p_k)

Twelve steps make one cycle. Initial state |00>; observables are P(|00>) at
each step and <ZZ> = <psi| Z tensor Z |psi>.

Run with:
    python angle_perturbation_control.py
Wall time: ~30 seconds for 1000 perturbations on a laptop.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Single-qubit gate primitives
# ---------------------------------------------------------------------------
def Rz(theta):
    return np.array([[np.exp(-1j*theta/2), 0],
                     [0, np.exp(+1j*theta/2)]], dtype=complex)

def Rx(theta):
    c, s = np.cos(theta/2), np.sin(theta/2)
    return np.array([[c, -1j*s], [-1j*s, c]], dtype=complex)

# 4x4 building blocks
I2 = np.eye(2, dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
ZZ = np.kron(Z, Z)

def kron(A, B):
    return np.kron(A, B)

# ---------------------------------------------------------------------------
# Floquet protocol on the dual-spinor pair (q+, q-)
# ---------------------------------------------------------------------------
T_CYCLE = 12

def base_angles(k):
    """Return (p_base, rz_base, rx_base) at step k from the v5 paper formulas."""
    sym = 2*np.pi/36                                  # = pi/18  (corrected formula)
    p_base  = 2*np.pi/12
    omega_k = 2*np.pi*k/T_CYCLE
    rx_base = sym*(1 + 0.5*np.cos(omega_k))
    rz_base = sym*(1 + 0.5*np.cos(omega_k + 2*np.pi/3))
    return p_base, rz_base, rx_base

# Merkabit Table 1a multipliers (paper v5; also code ouroboros_circuit.py)
# Row order matches paper Table 1a: S, R, T, P, F (P = strong, F = baseline)
MERKABIT_MULTIPLIERS = {
    # absent-gate -> (p_mult, rz_mult, rx_mult)
    'S': (1.0, 0.4, 1.3),
    'R': (1.0, 1.3, 0.4),
    'T': (1.0, 0.7, 0.7),
    'P': (0.6, 1.5, 1.8),
    'F': (1.0, 1.0, 1.0),
}
ABSENT_ORDER = ['S', 'R', 'T', 'P', 'F']

def step_unitary(k, absent_gate, multipliers):
    """4x4 Floquet step on the dual-spinor pair (q+ tensor q-)."""
    p_b, rz_b, rx_b = base_angles(k)
    p_m, rz_m, rx_m = multipliers[absent_gate]
    p, rz, rx = p_b*p_m, rz_b*rz_m, rx_b*rx_m
    # P gate: R_z(+p) on q+, R_z(-p) on q-
    U_P  = kron(Rz(+p), Rz(-p))
    # Symmetric R_z and R_x on both qubits
    U_Rz = kron(Rz(rz), Rz(rz))
    U_Rx = kron(Rx(rx), Rx(rx))
    return U_Rx @ U_Rz @ U_P

def floquet_evolution(absent_gate_seq, multipliers, n_steps):
    """Apply n_steps of the Floquet protocol to |00>, return state vector."""
    psi = np.array([1, 0, 0, 0], dtype=complex)
    for k in range(n_steps):
        U = step_unitary(k % T_CYCLE, absent_gate_seq[k % len(absent_gate_seq)], multipliers)
        psi = U @ psi
    return psi

def observables(psi):
    """Return (P(|00>), <ZZ>) for state psi."""
    p00 = abs(psi[0])**2
    zz  = float(np.real(np.conj(psi) @ ZZ @ psi))
    return p00, zz

# ---------------------------------------------------------------------------
# Pick the canonical 2-qubit Cirq absent-gate sequence
# ---------------------------------------------------------------------------
# The canonical 2-qubit prediction (cited in Table 7 obs 4 and the §5 protocol)
# uses chirality = +1, base = 0. Then absent_gate(0, +1, k) = k mod 5, i.e.
# the absent-gate cycles through all five values:
#   k = 0,1,2,3,4,5,6,7,8,9,10,11 -> S,R,T,P,F,S,R,T,P,F,S,R
# This is what willow_hardware_merkabit/experiments/run_p2_stroboscopic_cirq.py
# computes; the merkabit predicted observables (P(n=13) ~ 0.696, etc.) are
# defined for THIS trajectory.

# IMPORTANT: This is the cyclic ORDER in which absent-gate labels appear at
# successive Floquet steps (k mod 5). It matches the GATES list ordering used
# in willow_hardware_merkabit/experiments/run_p2_stroboscopic_cirq.py:
#   GATES = ['S', 'R', 'T', 'F', 'P']  (Willow Cirq convention)
# Note: this differs from the GATES list in merkabit_hardware_test/ouroboros_circuit.py
# which uses ['S', 'R', 'T', 'P', 'F']. Both code-bases assign the same
# multipliers to the same letter ('P' = strong, 'F' = baseline); only the
# cyclic position of P/F in the absent-gate trajectory differs.
# For the canonical 2-qubit Cirq prediction (paper Table 7 obs 4 = P at n=13),
# we use the Cirq ordering.
ABSENT_ORDER_CYCLIC = ['S', 'R', 'T', 'F', 'P']
ABSENT_SEQ_FIXED = [ABSENT_ORDER_CYCLIC[k % 5] for k in range(T_CYCLE)]
# = ['S', 'R', 'T', 'F', 'P', 'S', 'R', 'T', 'F', 'P', 'S', 'R']

# ---------------------------------------------------------------------------
# Compute merkabit predicted observables
# ---------------------------------------------------------------------------
def predicted_observables(multipliers, n_max=60):
    """Return arrays P_n and ZZ_n for n = 1..n_max steps.

    NOTE on dual periodicity: the angle base is periodic with period T_CYCLE = 12
    (cos(omega_k) terms), but the absent-gate index is periodic with period 5
    (= NUM_GATES). gcd(5, 12) = 1, so the combined Floquet trajectory has
    period 60. Use k % T_CYCLE for angle base, and k % 5 for absent-gate index.
    """
    P_n  = np.zeros(n_max + 1)
    ZZ_n = np.zeros(n_max + 1)
    P_n[0], ZZ_n[0] = 1.0, 1.0
    psi = np.array([1, 0, 0, 0], dtype=complex)
    for k in range(n_max):
        absent = ABSENT_ORDER_CYCLIC[k % 5]
        U = step_unitary(k % T_CYCLE, absent, multipliers)
        psi = U @ psi
        P_n[k+1], ZZ_n[k+1] = observables(psi)
    return P_n, ZZ_n

# ---------------------------------------------------------------------------
# Perturbation generators
# ---------------------------------------------------------------------------
def merkabit_param_vector():
    """Flatten the merkabit multipliers into a 15-vector in Table 1a row order."""
    return np.array([m for g in ABSENT_ORDER for m in MERKABIT_MULTIPLIERS[g]])

def vector_to_multipliers(v):
    """Inverse of merkabit_param_vector: 15-vector -> dict of triplets."""
    return {g: tuple(v[3*i : 3*i+3]) for i, g in enumerate(ABSENT_ORDER)}

def perturb_shuffle(rng):
    """Shuffle the 15 merkabit multipliers (preserves multiset, breaks structure)."""
    v = merkabit_param_vector().copy()
    rng.shuffle(v)
    return vector_to_multipliers(v)

def perturb_random(rng, lo=0.4, hi=1.8):
    """Replace each multiplier with iid Uniform(lo, hi)."""
    v = rng.uniform(lo, hi, size=15)
    return vector_to_multipliers(v)

def perturb_small(rng, sigma=0.1):
    """Add Gaussian noise (std sigma) to each multiplier."""
    v = merkabit_param_vector() + rng.normal(0, sigma, size=15)
    v = np.clip(v, 0.05, None)            # multipliers must stay positive
    return vector_to_multipliers(v)

# ---------------------------------------------------------------------------
# Main: compute merkabit observables, then perturbation sweep
# ---------------------------------------------------------------------------
def main():
    import csv, os
    OUT_CSV = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "data", "angle_perturbation_1000.csv"
    )

    print("=" * 78)
    print("ANGLE-TABLE PERTURBATION CONTROL")
    print("Tests whether merkabit's specific Table 1a multipliers are special,")
    print("or whether any similar 15-parameter angle table gives the same observables.")
    print("=" * 78)

    # ---- Merkabit baseline observables ----
    P_n, ZZ_n = predicted_observables(MERKABIT_MULTIPLIERS, n_max=60)
    merk_observables = {
        'P_at_n12':   P_n[12],
        'P_at_n13':   P_n[13],
        'P_at_n39':   P_n[39],
        'ZZ_at_n12':  ZZ_n[12],
        'P_at_n27':   P_n[27],
        'P_at_n37':   P_n[37],
    }
    print("\nMerkabit predicted observables (chirality=0 single-pair, base='S'):")
    for k, v in merk_observables.items():
        print(f"  {k:>14s} = {v:+.4f}")

    # ---- Perturbation sweeps ----
    rng = np.random.default_rng(42)
    N_PERTURB = 1000

    results = {
        'shuffle': {k: [] for k in merk_observables},
        'random':  {k: [] for k in merk_observables},
        'small':   {k: [] for k in merk_observables},
    }

    print(f"\nRunning {N_PERTURB} perturbations of each type...")
    rows = []
    for i in range(N_PERTURB):
        for tag, gen in [('shuffle', perturb_shuffle),
                         ('random',  perturb_random),
                         ('small',   perturb_small)]:
            mults = gen(rng)
            P_n, ZZ_n = predicted_observables(mults, n_max=60)
            results[tag]['P_at_n12']  .append(P_n[12])
            results[tag]['P_at_n13']  .append(P_n[13])
            results[tag]['P_at_n39']  .append(P_n[39])
            results[tag]['ZZ_at_n12'] .append(ZZ_n[12])
            results[tag]['P_at_n27']  .append(P_n[27])
            results[tag]['P_at_n37']  .append(P_n[37])
            rows.append({
                "trial": i + 1, "perturbation": tag,
                "P_at_n12": P_n[12], "P_at_n13": P_n[13], "P_at_n27": P_n[27],
                "P_at_n37": P_n[37], "P_at_n39": P_n[39], "ZZ_at_n12": ZZ_n[12],
            })
        if (i + 1) % 200 == 0:
            print(f"  ... {i+1}/{N_PERTURB}", flush=True)

    # Write CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {os.path.normpath(OUT_CSV)}")

    # ---- Report ----
    print()
    print("=" * 78)
    print("RESULTS")
    print("=" * 78)
    print()
    print(f"{'Observable':<14} {'Merkabit':>10}  | {'Perturbation':<10} {'Mean':>8} {'Std':>8} {'CI(2.5%)':>9} {'CI(97.5%)':>9} {'pct(merk)':>10}")
    print("-" * 100)

    for obs_name, merk_val in merk_observables.items():
        for tag in ['shuffle', 'random', 'small']:
            arr = np.array(results[tag][obs_name])
            mean = arr.mean()
            std  = arr.std(ddof=1)
            ci_lo, ci_hi = np.percentile(arr, [2.5, 97.5])
            # Where does merkabit value sit in the perturbed distribution?
            pct_below = (arr <= merk_val).mean() * 100   # percentile of merkabit
            print(f"{obs_name:<14} {merk_val:>+10.4f}  | {tag:<10} {mean:>+8.4f} {std:>8.4f} {ci_lo:>+9.4f} {ci_hi:>+9.4f} {pct_below:>9.1f}%")

    print()
    print("INTERPRETATION:")
    print("  - 'pct(merk)' is the percentile of the merkabit value within the perturbed distribution.")
    print("  - If merkabit observables sit at extreme percentiles (< 5% or > 95%) for the perturbed")
    print("    distributions, the merkabit angle table is genuinely special — random/shuffled tables")
    print("    cannot reproduce the predicted values.")
    print("  - If merkabit observables sit near the median (40-60%), the predictions are 'typical' for")
    print("    similar-magnitude tables, weakening the angle-specialness claim. The empirical hardware")
    print("    results in sec 3-5 still stand regardless.")

if __name__ == '__main__':
    main()
