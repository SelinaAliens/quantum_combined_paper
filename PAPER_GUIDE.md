# Paper Guide — Section-by-Section File Map

Maps every section of `paper/Paper_Quantum_Draft_v5.docx` to the source files that produced its claims, across all three repositories:

- **[this]** = this companion repo (`merkabit_quantum_paper_2026`)
- **[ibm]** = [`SelinaAliens/merkabit_hardware_test`](https://github.com/SelinaAliens/merkabit_hardware_test) (IBM hardware track)
- **[wlw]** = [`SelinaAliens/willow_hardware_merkabit`](https://github.com/SelinaAliens/willow_hardware_merkabit) (Willow pre-registration track)

---

## §2 — The P gate: native decomposition

| Claim | Source |
|---|---|
| P gate definition `Rz(+φ) ⊗ Rz(−φ)` | derivation in [16] (Base Paper); illustrated in `[ibm] ouroboros_circuit.py` |
| IBM virtual-Z compilation, depth 6 | `[ibm] ouroboros_circuit.py` + Qiskit transpiler |
| Cirq PhXZ compilation, depth 2 | `[wlw] experiments/run_p1b_ramsey_cirq.py` etc. |
| Twelve-step Floquet cycle | `[ibm] ouroboros_circuit.py` (`get_gate_angles()`, `build_ouroboros_step()`) |
| Table 1a/1b absent-gate multipliers | `[ibm] ouroboros_circuit.py:55-72` |

---

## §3 — Cross-architecture hardware confirmation

| Section | Source | Notes |
|---|---|---|
| §3.1 hardware sessions table | `[ibm] HARDWARE-RESULTS.md` (canonical session log) | Job IDs and CRNs |
| §3.1 historical Willow F = 2.42 pointer | `[wlw] analysis/willow_fano_analysis.py` | 420 surface-code circuits, symmetric-phase, distinct protocol from §5 |
| §3.2 ZPMB benchmarks (ZP-ORF, π-lock, parity) | `[ibm] experiments/run_p3_z2.py` + `[ibm] outputs/p3_z2/p3_z2_ibm_strasbourg_20260407_*.json` | 8 192 shots |
| §3.3 τ-sweep rotation gap (paired vs control Fano) | `[ibm] experiments/run_rotation_gap_hardware.py` + `[ibm] outputs/rotation_gap/rotation_gap_*.json` | Tables 3, 4 |
| §3.4 P2 stroboscopic cross-architecture | `[ibm] experiments/run_p2_stroboscopic.py` + `[ibm] outputs/p2_stroboscopic/p2_strobo_ibm_{strasbourg,kingston}_*.json` | Table 5 |
| §3.4 P5 DTC cross-architecture | `[ibm] experiments/run_p5_dtc.py` + `[ibm] outputs/p5_dtc/p5_dtc_ibm_{brussels,strasbourg,kingston}_*.json` | Table 6 |
| §3.5 P1b Ramsey Berry phase | `[ibm] experiments/run_p1_ramsey.py` + `[ibm] outputs/p1_ramsey/p1_ramsey_ibm_{strasbourg,kingston}_*.json` | Both backends |
| §3.5 P2 quasi-period peak n = 39 | same as §3.4 P2 stroboscopic | |

---

## §4 — Topology Monte Carlo

| Section | Source | Notes |
|---|---|---|
| §4.2 method (cells, chirality, error injection) | `[wlw] simulations/sim_scaling_comparison.py` | Same script as §4.4 |
| §4.3 hex vs square (τ, ε) grid (referenced as Paper 26 [15] Table 2) | `[wlw] simulations/sim_square_vs_hex_noisy.py` | 4 cells, 5 ε values |
| §4.4 scaling sweep + 4×4 sweet spot (referenced as Paper 26 [15] Table 3) | `[wlw] simulations/sim_scaling_comparison.py` | 7 cells, single-seed values |
| **§4.4 seed-dispersion stats (F = 0.370 ± 0.026)** | **`[this] data/seed_dispersion_30seeds.csv`** + **`[this] simulations/seed_sweep_driver.py`** | **30 seeds × 4 cells × {paired, control}** |

Section §4.4 in the v4 paper refers to "the supplementary CSV" — that CSV is `data/seed_dispersion_30seeds.csv` in *this* repo. The script that produced it is `simulations/seed_sweep_driver.py` (also in this repo); it wraps the frozen `simulations/sim_scaling_comparison.py` (also in this repo, identical to the live version in `[wlw]`).

---

## §5 — Pre-registered test for Google Willow

| Section | Source | Notes |
|---|---|---|
| §5.1 Table 7 predictions (observables 1–7) | `[wlw] PREDICTION.md` | SHAs `5bbfdb6f` (2026-04-12) and `745f653f` (2026-04-15) |
| §5.2 Cirq P1b (Ramsey Berry phase) | `[wlw] experiments/run_p1b_ramsey_cirq.py` | depth 2 after PhXZ merge |
| §5.2 Cirq P2 (stroboscopic quasi-period) | `[wlw] experiments/run_p2_stroboscopic_cirq.py` | depth 2 |
| §5.2 Cirq P4 (scaling, F vs N) | `[wlw] experiments/run_p4_scaling_cirq.py` | observable 7 |
| §5.2 Cirq P5 (DTC ε sweep) | `[wlw] experiments/run_p5_dtc_cirq.py` | depth 2 |
| §5.3 PREDICTION.md SHAs and timestamps | `[wlw] PREDICTION.md` (verifiable on GitHub) | DO NOT modify the willow repo's commit history |
| §5.3 IBM Appendix N pre-registration anchor | Base Paper [16] Zenodo `10.5281/zenodo.18925475 v4`, deposited 2026-03-09 | Predates IBM hardware sessions of 6–12 April 2026 |

---

## §6 — Discussion

Pure prose; no source files beyond those above. §6.2 (geometric origin of the angle table) cites refs [16, 19, 20, 21, 22, 13, 14, 15] — the Merkabit Research Series base paper plus Papers 20–26.

---

## §7 — Methods

| Section | Source |
|---|---|
| §7.1 hardware setup, qubit assignments, CRNs, job IDs | `[ibm] HARDWARE-RESULTS.md` (canonical) |
| §7.2 IBM circuit compilation (Qiskit 2.3.1, optimisation level 3) | `[ibm] experiments/*.py` |
| §7.2 Cirq compilation (PhXZ merge) | `[wlw] experiments/run_*.py` |
| §7.3 Fano factor / DTC ratio / cross-architecture fidelity estimators | `[ibm] experiments/*.py` (Fano, DTC); `[ibm] HARDWARE-RESULTS.md` (cross-arch fidelity formula) |
| §7.4 Monte Carlo protocol (PRNG seed 42, 20 000 shots) | `[wlw] simulations/sim_scaling_comparison.py` (frozen copy in `[this] simulations/`) |

---

## §8 — Data and code availability

The §8 listing in the paper:

| Resource | Location |
|---|---|
| IBM Runtime raw counts + experiment scripts | [ibm] |
| Cirq implementations + topology scaling sims + `PREDICTION.md` | [wlw] |
| Per-seed dispersion CSV + driver script | [this] `data/` and `simulations/` |
| Paper 24 / 25 / 26 Zenodo preprints | DOIs cited inline in §8 |
| Base Paper Zenodo deposit | DOI `10.5281/zenodo.18925475 v4` |
| Paper 3 Zenodo preprint | DOI `10.5281/zenodo.19438935` |
| DAQEC source dataset | DOI `10.5281/zenodo.17881116` (Ashuraliyev 2025) |

---

## Why three repositories?

- **`[ibm]`** is the IBM hardware track. It existed before the consolidation paper; Papers 24, 25, 26 cite it directly. Its `HARDWARE-RESULTS.md` and raw JSON outputs are the canonical hardware record.
- **`[wlw]`** is the Willow pre-registration track. It was created on 2026-04-12 specifically to hold the timestamped pre-registered prediction (`PREDICTION.md`). The credibility of §5.3 depends on that timestamp being independently verifiable, so the repo's commit history must remain untouched.
- **`[this]`** is the consolidation paper companion. It carries the manuscript, the seed-dispersion CSV (which exists only because of the consolidation paper's response to a pre-submission methodological audit), and the script that produced that CSV. It links to the other two; it does not duplicate them.
