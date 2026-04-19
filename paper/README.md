# Manuscript

The consolidation paper *Native Asymmetric-Phase Gates Produce Cross-Architecture Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors* (Stenberg & Hetland, 2026) is **pending submission**. The manuscript itself is not yet posted in this repository.

## Where to find the paper after submission

- **arXiv:** the preprint will be posted to quant-ph and linked here once an arXiv ID is assigned.
- **Zenodo DOI:** a citable Zenodo snapshot of this repository (including the manuscript) will be minted at submission and linked here.
- **Journal version:** when accepted, the journal-formatted version will be linked here alongside the accepted-author-manuscript.

## What's in this repository now

The supporting artefacts for the paper are already public in this repository:

- **Backing data** (`data/`)
  - `seed_dispersion_30seeds.csv` — 30-seed Monte Carlo dispersion (§4.4 of the paper)
  - `angle_perturbation_1000.csv` — 3,000-trial angle-table perturbation control (§6.2)
- **Reproduction scripts** (`simulations/`)
  - `seed_sweep_driver.py` — reproduces the seed-dispersion CSV in ~5 minutes
  - `angle_perturbation_control.py` — reproduces the perturbation CSV in ~30 seconds; also reproduces every paper-quoted ideal observable
  - `sim_scaling_comparison.py` — frozen copy of the upstream Monte Carlo simulation
- **Figures** (`figures/`) — all six paper figures plus their generating Python scripts (regenerable from the CSVs in seconds)
- **Section-by-section file map** (`PAPER_GUIDE.md`) — describes which file/repo backs each paper section

## Hardware data

All IBM Eagle r3 and Heron r2 raw counts are in the [IBM hardware track repo](https://github.com/SelinaAliens/merkabit_hardware_test) (`HARDWARE-RESULTS.md` plus `outputs/` JSON files).

The pre-registered Cirq protocols for the Google Willow run are in the [Willow track repo](https://github.com/SelinaAliens/willow_hardware_merkabit), with `PREDICTION.md` carrying the timestamped commit history (SHAs `5bbfdb6f` on 2026-04-12 and `745f653f` on 2026-04-15) that establishes pre-registration before any Google hardware access.

## Citation (interim, until arXiv / DOI assigned)

> Stenberg, S. & Hetland, T. H. *Native Asymmetric-Phase Gates Produce Cross-Architecture Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors.* Manuscript pending submission, 2026. Code and supplementary data: `https://github.com/SelinaAliens/quantum_combined_hardware`.
