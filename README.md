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
merkabit_quantum_paper_2026/
├── README.md                       (this file — wayfinding)
├── LICENSE                         (MIT)
├── PAPER_GUIDE.md                  (paper section → source-repo file map)
├── paper/
│   └── Paper_Quantum_Draft_v6.docx (the manuscript)
├── data/
│   ├── README.md                       (CSV schemas and provenance)
│   ├── seed_dispersion_30seeds.csv     (30-seed Monte Carlo dispersion, §4.4)
│   └── angle_perturbation_1000.csv     (3,000-trial angle-table perturbation control, §6.1)
├── simulations/
│   ├── README.md                           (how to reproduce §4.4 and §6.1 from scratch)
│   ├── sim_scaling_comparison.py           (frozen copy of willow_hardware_merkabit/simulations/sim_scaling_comparison.py)
│   ├── seed_sweep_driver.py                (driver that produced seed_dispersion_30seeds.csv)
│   └── angle_perturbation_control.py       (dual-spinor unitary + angle-table perturbation sweep)
└── .gitignore
```

Total size: < 600 kB. Three scripts, two CSVs, one docx, three READMEs, one license.

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

1. **The manuscript** (`paper/Paper_Quantum_Draft_v6.docx`) — the consolidation paper itself, in submission-ready form.

2. **The seed-dispersion table** (`data/seed_dispersion_30seeds.csv`) — 30 PRNG seeds × 4 cells × {paired, control} = 120 rows showing that the headline §4.4 result (4×4 square cell at τ = 5, ε = 0.10) gives F = 0.370 ± 0.026 across seeds, not the single-seed F = 0.286 originally reported in Paper 26 [15]. This data table is generated specifically for §4.4 of the consolidation paper and does not exist in either source repo.

3. **The driver that produced the table** (`simulations/seed_sweep_driver.py`) — wraps `sim_scaling_comparison.py` and runs it across seeds 1..30. Reproducible, ~5 minutes wall time on a laptop.

4. **A frozen copy of `sim_scaling_comparison.py`** — the simulation script that produced the seed-dispersion data. Frozen here at submission-time SHA so the paper's numerical claims remain reproducible even if the live source repo evolves. The live version is in `willow_hardware_merkabit/simulations/`.

5. **The angle-table perturbation control** (`simulations/angle_perturbation_control.py` and `data/angle_perturbation_1000.csv`) — a self-contained dual-spinor Floquet unitary in numpy that reproduces every paper-quoted ideal observable (§3.2 π-lock, §3.4 P2 stroboscopic, Table 5) to four-digit agreement, then perturbs the 15-parameter Table 1a multipliers across 3,000 trials to test whether the merkabit angle table is required to produce the predicted observables. Generated specifically for §6.1 of the consolidation paper. **Headline finding**: the high-recurrence peaks (P at n = 37 ≈ 0.92 and n = 39 ≈ 0.91) are strongly discriminative (merkabit at 86th–94th percentile of perturbed distributions); the low-recurrence observables (P at n = 13, π-lock) are typical for similar-magnitude tables. The Willow run's discrimination weight concentrates on Table 7 observable 5.

---

## Reproducing the paper's headline numbers

### IBM hardware results (§3)
Not reproducible without IBM Quantum Runtime access. Raw counts and job IDs are in [`merkabit_hardware_test/outputs/`](https://github.com/SelinaAliens/merkabit_hardware_test/tree/main/outputs); analysis scripts in `merkabit_hardware_test/experiments/`.

### Topology Monte Carlo (§4) and seed-dispersion (§4.4)
```bash
git clone https://github.com/selinaserephina-star/merkabit_quantum_paper_2026
cd merkabit_quantum_paper_2026/simulations
python seed_sweep_driver.py    # ~5 min, reproduces data/seed_dispersion_30seeds.csv
```

### Angle-table perturbation control (§6.1)
```bash
cd merkabit_quantum_paper_2026/simulations
python angle_perturbation_control.py    # ~30 sec, reproduces data/angle_perturbation_1000.csv
```
The script first prints the merkabit ideal observables (sanity-check against paper §3.2 π-lock and §3.4 P2 stroboscopic), then runs 3,000 multiplier-perturbation trials. See `simulations/README.md` and `data/README.md` for details.

### Willow Cirq predictions (§5)
Not reproducible against hardware (early-access pending). Cirq scripts that *will* run on Willow are at [`willow_hardware_merkabit/experiments/`](https://github.com/SelinaAliens/willow_hardware_merkabit/tree/main/experiments) (P1b, P2, P4, P5).

---

## Citation

Until a Zenodo DOI is minted at submission, cite as:

> Stenberg, S. & Hetland, T. H. *Native Asymmetric-Phase Gates Produce Cross-Architecture Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors.* GitHub: `selinaserephina-star/merkabit_quantum_paper_2026` (April 2026).

A Zenodo DOI snapshot of this repo (and the two source repos at submission-time SHAs) will be minted when the paper is submitted to Quantum.

---

## License

MIT. See `LICENSE`.

## Contact

Selina Stenberg — corresponding author.
