# Merkabit Quantum Paper 2026 — Companion Repository

**Paper:** *Native Asymmetric-Phase Gates Produce Cross-Architecture Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors*
**Authors:** Selina Stenberg and Thor Henning Hetland
**Target venue:** Quantum
**Status:** Pre-submission, April 2026

This repository is the **paper-companion artifact** for the consolidation of Papers 24, 25, and 26 of the Merkabit Research Series. It contains the manuscript, the supplementary data table that backs §4.4, and the simulation script that produced that data.

It does **not** duplicate code or data that already lives in the two source repositories. Instead, it points at them. See `PAPER_GUIDE.md` for a complete section-by-section file map.

---

## Contents

```
quantum_combined_paper/
├── README.md                                    (this file — wayfinding)
├── LICENSE                                      (MIT)
├── PAPER_GUIDE.md                               (paper section → source-repo file map)
├── paper/
│   ├── README.md                                    (manuscript pending submission; arXiv / DOI link will be added on posting)
│   └── 3.3_revised.md                               (revised §3.3 framing — per-round Fano forensics)
├── data/
│   ├── README.md                                    (CSV schemas and provenance)
│   ├── seed_dispersion_30seeds.csv                  (30-seed Monte Carlo dispersion, §4.4)
│   ├── angle_perturbation_1000.csv                  (3,000-trial angle-table perturbation control, §6.2)
│   ├── per_round_fano_summary.csv                   (per-round Fano across 5 hardware sessions, §3.3)
│   ├── tau_sweep_3node_triangle.csv                 (classical pentachoric MC, 3-node triangle τ-sweep)
│   ├── tau_sweep_noisy_qiskit.csv                   (Qiskit Aer + FakeSherbrooke noise model, τ-sweep)
│   └── tau_sweep_lindblad_triangle.csv              (quantum-trajectory MC + IBM Brisbane noise, τ-sweep)
├── figures/
│   └── figS_per_round_fano.{png,pdf}                (per-round vs aggregate Fano forensics, §3.3)
├── simulations/
│   ├── README.md                                    (how to reproduce §4.4, §6.2, §3.3 from scratch)
│   ├── sim_scaling_comparison.py                    (frozen copy of willow_hardware_merkabit/simulations/sim_scaling_comparison.py)
│   ├── seed_sweep_driver.py                         (driver that produced seed_dispersion_30seeds.csv)
│   ├── angle_perturbation_control.py                (dual-spinor unitary + angle-table perturbation sweep, §6.2)
│   ├── tau_sweep_3node_triangle.py                  (classical pentachoric MC on the triangle)
│   ├── tau_sweep_eps_scan.py                        (ε-scan version of the triangle MC)
│   ├── tau_sweep_noisy_qiskit.py                    (Qiskit Aer + FakeSherbrooke noise τ-sweep)
│   ├── tau_sweep_lindblad_triangle.py               (quantum-trajectory + Brisbane noise τ-sweep)
│   └── per_round_fano_extractor.py                  (extracts per-round Fano from 5 hardware JSONs)
└── .gitignore
```

The manuscript itself is **pending submission** — see `paper/README.md`. The §3.3 revision in `paper/3.3_revised.md` reflects the per-round Fano forensics described below.

---

## Source repositories (where the live code and data live)

This paper draws on artifacts from two pre-existing repositories. Both should be read alongside this companion.

### 1. IBM hardware track — [`SelinaAliens/merkabit_hardware_test`](https://github.com/SelinaAliens/merkabit_hardware_test)

All IBM Eagle r3 and Heron r2 hardware results: raw IBM Runtime JSON counts, the `HARDWARE-RESULTS.md` per-session log with job IDs, the `ouroboros_circuit.py` Floquet-circuit builder, the `qubit_mapper.py` Eisenstein-cell embedding, and the `experiments/` scripts that submitted the IBM jobs. Public mirror of `selinaserephina-star/merkabit_hardware_test`.

The paper §3 (cross-architecture hardware confirmation) and §7.1 (data provenance) point here.

### 2. Willow pre-registration track — [`SelinaAliens/willow_hardware_merkabit`](https://github.com/SelinaAliens/willow_hardware_merkabit)

The pre-registered Willow predictions, Cirq implementations of the four protocols (P1b, P2, P4, P5), the topology-scaling Monte Carlo simulations, and the historical Willow F = 2.42 reanalysis. **`PREDICTION.md` carries the timestamped commit history that backs §5.3 of the paper** (initial SHA `5bbfdb6f` on 2026-04-12; updated SHA `745f653f` on 2026-04-15, both prior to any Google hardware access). Public mirror of `selinaserephina-star/willow_hardware_merkabit`.

The paper §4 (topology Monte Carlo), §5 (pre-registered test), and §3.1's pointer to the historical Willow analysis all point here.

---

## What this repo adds that the source repos don't

1. **A pointer to the manuscript** (`paper/README.md`) — the consolidation paper itself is **pending submission**; the arXiv ID and Zenodo DOI will be added to `paper/README.md` once assigned. The manuscript is not yet posted in this repository.

2. **The seed-dispersion table** (`data/seed_dispersion_30seeds.csv`) — 30 PRNG seeds × 4 cells × {paired, control} = 120 rows showing that the headline §4.4 result (4×4 square cell at τ = 5, ε = 0.10) gives F = 0.370 ± 0.026 across seeds, not the single-seed F = 0.286 originally reported in Paper 26 [15]. This data table is generated specifically for §4.4 of the consolidation paper and does not exist in either source repo.

3. **The driver that produced the table** (`simulations/seed_sweep_driver.py`) — wraps `sim_scaling_comparison.py` and runs it across seeds 1..30. Reproducible, ~5 minutes wall time on a laptop.

4. **A frozen copy of `sim_scaling_comparison.py`** — the simulation script that produced the seed-dispersion data. Frozen here at submission-time SHA so the paper's numerical claims remain reproducible even if the live source repo evolves. The live version is in `willow_hardware_merkabit/simulations/`.

5. **The angle-table perturbation control** (`simulations/angle_perturbation_control.py` and `data/angle_perturbation_1000.csv`) — a self-contained dual-spinor Floquet unitary in numpy that reproduces every paper-quoted ideal observable (§3.2 π-lock, §3.4 P2 stroboscopic, Table 5) to four-digit agreement, then perturbs the 15-parameter Table 1a multipliers across 3,000 trials to test whether the merkabit angle table is required to produce the predicted observables. Generated specifically for §6.2 of the consolidation paper. **Headline finding**: the high-recurrence peaks (P at n = 37 ≈ 0.92 and n = 39 ≈ 0.91) are strongly discriminative (merkabit at 86th–94th percentile of perturbed distributions); the low-recurrence observables (P at n = 13, π-lock) are typical for similar-magnitude tables. The Willow run's discrimination weight concentrates on Table 7 observable 5.

6. **Per-round Fano forensics for §3.3** (`simulations/per_round_fano_extractor.py`, `data/per_round_fano_summary.csv`, `figures/figS_per_round_fano.{png,pdf}`, `paper/3.3_revised.md`) — extracts per-round Fano values from all four `rotation_gap_*` JSONs in `merkabit_hardware_test/outputs/rotation_gap/` plus the 7-node `pentachoric_error_injection_*` JSON. **Headline finding**: per-round Fano sits in [0.48, 0.65] across every session, every τ, paired and control. The aggregate Fano spread quoted in earlier drafts of §3.3 (0.51 to 5.64) is dominated by *session-dependent round-to-round correlation* (ρ from ~0.00 to ~0.89), not by the protocol. The merkabit signature is reproducible at the per-round level; the τ-dependent aggregate-Fano "direction-flip" is a calibration-drift artefact, not a protocol observable. The 7-node pentachoric injection corroborates: F = 0.055 ± 0.010 at the centre node (chi=0), F = 0.204 ± 0.029 at the periphery, detection rate 0.987 across 28 single-error injections.

7. **Three independent τ-sweep simulations** (`simulations/tau_sweep_3node_triangle.py`, `tau_sweep_noisy_qiskit.py`, `tau_sweep_lindblad_triangle.py`) — classical pentachoric MC, Qiskit Aer + FakeSherbrooke noise model, and quantum-trajectory MC + IBM Brisbane noise budget. The trajectory MC reproduces hardware per-round F = 0.49–0.55 across τ ∈ [1, 7] and the τ = 5 paired vs control sign; the Qiskit incoherent-noise model alone reverses the sign, demonstrating that the merkabit signature *requires* coherent ZZ to manifest. CSVs in `data/tau_sweep_*.csv`.

---

## Reproducing the paper's headline numbers

### IBM hardware results (§3)
Not reproducible without IBM Quantum Runtime access. Raw counts and job IDs are in [`merkabit_hardware_test/outputs/`](https://github.com/SelinaAliens/merkabit_hardware_test/tree/main/outputs); analysis scripts in `merkabit_hardware_test/experiments/`.

### Topology Monte Carlo (§4) and seed-dispersion (§4.4)
```bash
git clone https://github.com/SelinaAliens/quantum_combined_paper
cd quantum_combined_paper/simulations
python seed_sweep_driver.py    # ~5 min, reproduces data/seed_dispersion_30seeds.csv
```

### Angle-table perturbation control (§6.2)
```bash
cd quantum_combined_paper/simulations
python angle_perturbation_control.py    # ~30 sec, reproduces data/angle_perturbation_1000.csv
```
The script first prints the merkabit ideal observables (sanity-check against paper §3.2 π-lock and §3.4 P2 stroboscopic), then runs 3,000 multiplier-perturbation trials. See `simulations/README.md` and `data/README.md` for details.

### Per-round Fano forensics (§3.3)
```bash
# Requires a local clone of merkabit_hardware_test (default path: C:/Users/selin/merkabit_hardware_test)
cd quantum_combined_paper/simulations
python per_round_fano_extractor.py --hw-repo /path/to/merkabit_hardware_test
# ~3 sec, reproduces data/per_round_fano_summary.csv and figures/figS_per_round_fano.{png,pdf}
```

### τ-sweep simulations (§3.3 supporting)
```bash
cd quantum_combined_paper/simulations
python tau_sweep_3node_triangle.py      # ~60 sec, classical pentachoric MC
python tau_sweep_noisy_qiskit.py        # ~3 min, Qiskit Aer + FakeSherbrooke (Eagle r3) noise
python tau_sweep_lindblad_triangle.py   # ~25 min, quantum-trajectory MC + IBM Brisbane noise
```

### Willow Cirq predictions (§5)
Not reproducible against hardware (early-access pending). Cirq scripts that *will* run on Willow are at [`willow_hardware_merkabit/experiments/`](https://github.com/SelinaAliens/willow_hardware_merkabit/tree/main/experiments) (P1b, P2, P4, P5).

---

## Citation

**Zenodo DOI:** [10.5281/zenodo.19663025](https://doi.org/10.5281/zenodo.19663025) (companion repo snapshot, tag `v1.0-submission`).

Citation:

> Stenberg, S. & Hetland, T. H. *Native Asymmetric-Phase Gates Produce Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors: Cross-Architecture IBM Evidence and a Pre-Registered Willow Test.* GitHub: `SelinaAliens/quantum_combined_paper` (April 2026).

**Zenodo DOI:** [10.5281/zenodo.19663025](https://doi.org/10.5281/zenodo.19663025) — companion repo snapshot at SHA `9c56153` (tag `v1.0-submission`). Use this DOI as the canonical citation for the supplementary code and data.

---

## License

MIT. See `LICENSE`.

## Contact

Selina Stenberg — corresponding author.
