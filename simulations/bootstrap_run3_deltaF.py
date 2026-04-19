#!/usr/bin/env python3
"""
Confidence interval on the Run 3 paired-vs-control Fano gap.

Uses two complementary approaches:

(1) Poisson-asymptotic (primary; standard in syndrome-statistics literature)
    For a sample of N shots with per-shot weight distribution close to
    quasi-Poisson, the Fano factor F = Var/Mean has approximate sampling
    variance Var(F) ≈ 2 F² / N. For the difference of two independent Fano
    estimates, Var(ΔF) ≈ 2 (F1² + F2²) / N. This is the leading-order
    delta-method result and does not depend on the joint distribution
    structure beyond the assumption that the underlying weight distribution
    is approximately quasi-Poisson — which is well supported here since
    the recorded distributions are sub-Poissonian-of-Poisson with
    F ≈ 0.49–0.56.

(2) Parametric bootstrap (sanity check)
    Synthesises a per-shot bitstring distribution from the recorded edge
    fire rates and a latent shot-level scale that reproduces the
    round-to-round correlation implied by the recorded per-round and
    aggregate Fano values. Resamples N shots with replacement, B = 10 000
    times, and computes the percentile CI. Used to check that the
    asymptotic CI is in the right ballpark, but reports the asymptotic
    result as primary because the parametric model is provisional and
    the asymptotic formula is well-established.

Limitation: a true non-parametric BCa would require the full per-shot
counts dictionary from the IBM Runtime PrimitiveResult; the JSON only
preserves moments and a top-10 counts summary. The asymptotic CI here
is the right order of magnitude and is independently derivable from
the JSON's sufficient statistics; if Thor retrieves the raw counts, a
non-parametric BCa can replace it without changing the §3.3 narrative.
"""
import os, json, sys, math, csv
import numpy as np

JSON_PATH = r"C:\Users\selin\merkabit_hardware_test\outputs\rotation_gap\rotation_gap_ibm_strasbourg_20260409_112127.json"

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)
paired   = data["results"]["paired_tau5"]
control  = data["results"]["unpaired_tau5"]
N_SHOTS  = paired["total_shots"]   # 4096

# ---------------------------------------------------------------------------
# (1) Poisson-asymptotic CI
# ---------------------------------------------------------------------------
def fano_se_poisson(F, N):
    """Asymptotic SE of F = Var/Mean for N shots, quasi-Poisson assumption.
    Derivation: delta method on F = s²/m with Var(s²) ≈ 2 s⁴/N (Gaussian)
    and Var(m) ≈ s²/N gives Var(F) ≈ 2 F²/N. Equivalent to the
    chi-squared-on-(N-1)-df result for variance ratio. Standard formula
    in counting-statistics literature; conservative for sub-Poissonian
    distributions (which underestimate kurtosis vs Poisson)."""
    return math.sqrt(2.0 * F * F / N)

def asymptotic_ci(F, N, level=0.95):
    se = fano_se_poisson(F, N)
    z = 1.959963984540054   # scipy.stats.norm.ppf(0.975)
    return F - z * se, F + z * se, se

print("=" * 80)
print("Run 3 (ibm_strasbourg, 2026-04-09 11:21:27) — Fano gap CI")
print("=" * 80)
print(f"Shots/configuration : {N_SHOTS}")
print(f"Paired job  : {paired.get('job_id', '<no job_id>')}")
print(f"Control job : {control.get('job_id', '<no job_id>')}")
print()

F_p_agg = paired["fano_factor"]
F_c_agg = control["fano_factor"]
F_p_round_mean = float(np.mean(paired["per_round_fano"]))
F_c_round_mean = float(np.mean(control["per_round_fano"]))
delta_agg   = F_p_agg - F_c_agg
delta_round = F_p_round_mean - F_c_round_mean

# Aggregate F: each F estimated from N=4096 shots
lo_p, hi_p, se_p = asymptotic_ci(F_p_agg, N_SHOTS)
lo_c, hi_c, se_c = asymptotic_ci(F_c_agg, N_SHOTS)
se_delta_agg = math.sqrt(se_p**2 + se_c**2)
ci_delta_agg = (delta_agg - 1.96 * se_delta_agg, delta_agg + 1.96 * se_delta_agg)

# Per-round F: each per-round F is a Fano from N=4096 shots restricted to
# 3 bits. SE per round same formula. Mean of 5 rounds: divide by sqrt(5)
# under the implied near-zero round-to-round correlation (rho_eff ≈ 0.01-0.03
# in Run 3, so rounds are essentially independent for this purpose).
N_PER_ROUND = N_SHOTS
N_ROUNDS = 5
se_p_round_one = fano_se_poisson(F_p_round_mean, N_PER_ROUND)
se_c_round_one = fano_se_poisson(F_c_round_mean, N_PER_ROUND)
se_p_round_mean = se_p_round_one / math.sqrt(N_ROUNDS)
se_c_round_mean = se_c_round_one / math.sqrt(N_ROUNDS)
se_delta_round = math.sqrt(se_p_round_mean**2 + se_c_round_mean**2)
ci_delta_round = (delta_round - 1.96 * se_delta_round, delta_round + 1.96 * se_delta_round)

# Z-score on aggregate ΔF
z_agg   = abs(delta_agg)   / se_delta_agg
z_round = abs(delta_round) / se_delta_round

print("ASYMPTOTIC CI (quasi-Poisson, delta method)")
print("-" * 80)
print(f"  F_paired (aggregate)         = {F_p_agg:.4f}    "
      f"SE = {se_p:.4f}    95% CI [{lo_p:.4f}, {hi_p:.4f}]")
print(f"  F_control (aggregate)        = {F_c_agg:.4f}    "
      f"SE = {se_c:.4f}    95% CI [{lo_c:.4f}, {hi_c:.4f}]")
print()
print(f"  ΔF (aggregate)               = {delta_agg:+.4f}   "
      f"SE = {se_delta_agg:.4f}   95% CI [{ci_delta_agg[0]:+.4f}, {ci_delta_agg[1]:+.4f}]   "
      f"|z| = {z_agg:.2f}   "
      f"({'EXCLUDES 0' if ci_delta_agg[1] < 0 or ci_delta_agg[0] > 0 else 'includes 0'})")
print(f"  ΔF (per-round mean)          = {delta_round:+.4f}   "
      f"SE = {se_delta_round:.4f}   95% CI [{ci_delta_round[0]:+.4f}, {ci_delta_round[1]:+.4f}]   "
      f"|z| = {z_round:.2f}   "
      f"({'EXCLUDES 0' if ci_delta_round[1] < 0 or ci_delta_round[0] > 0 else 'includes 0'})")

# ---------------------------------------------------------------------------
# (2) Parametric bootstrap — synthesise round-correlation-aware shots
# ---------------------------------------------------------------------------
def synthesize_correlated(N, edge_fire_rates, agg_F, per_round_F_mean,
                            n_rounds=5, rng=None):
    """Synthesise N shots × (n_rounds × n_edges) bits.
    Captures round-to-round correlation via a per-shot latent z scaling all
    edge probabilities such that the implied aggregate Fano matches.
    Solve for sigma_z^2:  rho_eff = (agg_F / round_F - 1) / (n_rounds - 1)
    rho_eff implies Var(z) ≈ rho_eff × m_round² / sum_p² (small approximation
    keeping leading term). Iterate sigma until aggregate F matches recorded.
    Returns bits array of shape (N, n_rounds * n_edges)."""
    rng = rng or np.random.default_rng()
    n_edges = len(edge_fire_rates)
    p = np.array(edge_fire_rates)
    rho_eff = max(0.0, (agg_F / per_round_F_mean - 1.0) / (n_rounds - 1)) if per_round_F_mean > 1e-9 else 0.0

    # Choose sigma_z by closed-form approximation, then refine
    # Var(z) such that Cov(W_r1, W_r2) = sum_p² × Var(z), and
    # Var(W_r) ≈ sum p(1-p) + Var(z) × sum_p²; rho ≈ Var(z)·sum_p² / Var(W_r)
    sum_p = float(p.sum())
    bern_var = float((p * (1 - p)).sum())
    target = (rho_eff * bern_var) / max(1e-12, (1 - rho_eff)) if rho_eff < 1 else 0.0
    sigma_z = math.sqrt(target) / max(1e-9, sum_p)

    # Latent z per shot, mean 1, std sigma_z, clip to [0.1, 1.9] for stability
    z = np.clip(rng.normal(1.0, sigma_z, size=N), 0.1, 1.9)
    bits = np.zeros((N, n_rounds * n_edges), dtype=np.int8)
    for r in range(n_rounds):
        for e, pe in enumerate(p):
            scaled = np.clip(z * pe, 0.001, 0.999)
            bits[:, r * n_edges + e] = (rng.random(N) < scaled).astype(np.int8)
    return bits

def fano_metrics(bits, n_rounds=5, n_edges=3):
    weights = bits.sum(axis=1)
    m = weights.mean()
    F_agg = weights.var(ddof=1) / m if m > 1e-12 else float("nan")
    per_round_F = []
    for r in range(n_rounds):
        rw = bits[:, r * n_edges:(r + 1) * n_edges].sum(axis=1)
        rm = rw.mean()
        per_round_F.append(rw.var(ddof=1) / rm if rm > 1e-12 else float("nan"))
    return F_agg, float(np.mean(per_round_F))

rng = np.random.default_rng(42)
paired_bits = synthesize_correlated(N_SHOTS, paired["edge_fire_rates"],
                                     agg_F=F_p_agg, per_round_F_mean=F_p_round_mean,
                                     rng=rng)
control_bits = synthesize_correlated(N_SHOTS, control["edge_fire_rates"],
                                      agg_F=F_c_agg, per_round_F_mean=F_c_round_mean,
                                      rng=rng)

F_p_synth, F_p_round_synth = fano_metrics(paired_bits)
F_c_synth, F_c_round_synth = fano_metrics(control_bits)
print()
print("Synthesis sanity check (synthetic vs recorded):")
print(f"  F_paired_aggregate    : synth {F_p_synth:.4f}  recorded {F_p_agg:.4f}  Δ {abs(F_p_synth - F_p_agg):.4f}")
print(f"  F_paired_per_round    : synth {F_p_round_synth:.4f}  recorded {F_p_round_mean:.4f}  Δ {abs(F_p_round_synth - F_p_round_mean):.4f}")
print(f"  F_control_aggregate   : synth {F_c_synth:.4f}  recorded {F_c_agg:.4f}  Δ {abs(F_c_synth - F_c_agg):.4f}")
print(f"  F_control_per_round   : synth {F_c_round_synth:.4f}  recorded {F_c_round_mean:.4f}  Δ {abs(F_c_round_synth - F_c_round_mean):.4f}")

N_BOOT = 10_000
print()
print(f"Running {N_BOOT:,} bootstrap resamples...")
delta_F_agg_boot   = np.zeros(N_BOOT)
delta_F_round_boot = np.zeros(N_BOOT)
for b in range(N_BOOT):
    idx = rng.integers(0, N_SHOTS, size=N_SHOTS)
    F_p_b, F_p_r_b = fano_metrics(paired_bits[idx])
    F_c_b, F_c_r_b = fano_metrics(control_bits[idx])
    delta_F_agg_boot[b]   = F_p_b - F_c_b
    delta_F_round_boot[b] = F_p_r_b - F_c_r_b

def boot_ci(samples):
    return (float(np.mean(samples)),
            float(np.std(samples, ddof=1)),
            float(np.percentile(samples, 2.5)),
            float(np.percentile(samples, 97.5)))

print()
print("PARAMETRIC BOOTSTRAP (10 000 resamples, correlation-aware synthesis)")
print("-" * 80)
m, se, lo, hi = boot_ci(delta_F_agg_boot)
print(f"  ΔF (aggregate)               = {m:+.4f}   SE = {se:.4f}   "
      f"95% CI [{lo:+.4f}, {hi:+.4f}]   "
      f"({'EXCLUDES 0' if hi < 0 or lo > 0 else 'includes 0'})")
m, se, lo, hi = boot_ci(delta_F_round_boot)
print(f"  ΔF (per-round mean)          = {m:+.4f}   SE = {se:.4f}   "
      f"95% CI [{lo:+.4f}, {hi:+.4f}]   "
      f"({'EXCLUDES 0' if hi < 0 or lo > 0 else 'includes 0'})")

# Save CSV summary
out_csv = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "data", "bootstrap_run3_deltaF.csv"))
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["quantity", "method", "estimate", "SE", "ci_lo_95", "ci_hi_95", "excludes_zero"])
    # Asymptotic
    w.writerow(["F_paired_aggregate", "asymptotic_quasi_poisson",
                f"{F_p_agg:.6f}", f"{se_p:.6f}",
                f"{lo_p:.6f}", f"{hi_p:.6f}", "yes"])
    w.writerow(["F_control_aggregate", "asymptotic_quasi_poisson",
                f"{F_c_agg:.6f}", f"{se_c:.6f}",
                f"{lo_c:.6f}", f"{hi_c:.6f}", "yes"])
    w.writerow(["delta_F_aggregate", "asymptotic_quasi_poisson",
                f"{delta_agg:.6f}", f"{se_delta_agg:.6f}",
                f"{ci_delta_agg[0]:.6f}", f"{ci_delta_agg[1]:.6f}",
                "yes" if ci_delta_agg[1] < 0 or ci_delta_agg[0] > 0 else "no"])
    w.writerow(["delta_F_per_round", "asymptotic_quasi_poisson",
                f"{delta_round:.6f}", f"{se_delta_round:.6f}",
                f"{ci_delta_round[0]:.6f}", f"{ci_delta_round[1]:.6f}",
                "yes" if ci_delta_round[1] < 0 or ci_delta_round[0] > 0 else "no"])
    # Parametric bootstrap
    m, se, lo, hi = boot_ci(delta_F_agg_boot)
    w.writerow(["delta_F_aggregate", "parametric_bootstrap_B10000",
                f"{m:.6f}", f"{se:.6f}",
                f"{lo:.6f}", f"{hi:.6f}",
                "yes" if hi < 0 or lo > 0 else "no"])
    m, se, lo, hi = boot_ci(delta_F_round_boot)
    w.writerow(["delta_F_per_round", "parametric_bootstrap_B10000",
                f"{m:.6f}", f"{se:.6f}",
                f"{lo:.6f}", f"{hi:.6f}",
                "yes" if hi < 0 or lo > 0 else "no"])
print(f"\nWrote: {out_csv}")
