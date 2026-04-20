# Manuscript

The consolidation paper *Native Asymmetric-Phase Gates Produce Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors: Cross-Architecture IBM Evidence and a Pre-Registered Willow Test* (Stenberg & Hetland, 2026) — **submission candidate v19** — is feature-complete and undergoing final author review prior to journal submission. The manuscript is held privately on the authors' workstations during this phase; the public copy of this repository (`SelinaAliens/quantum_combined_paper`) hosts all supporting code, data, and figures.

## Submission status

- **Submission candidate:** `Paper_Quantum_Draft_v19.docx` (held privately; not posted to either repository until journal acceptance)
- **Target venue:** Quantum
- **Pre-registration anchors (commit-verifiable, public):**
  - IBM-side: Base Paper Zenodo deposit `10.5281/zenodo.18925475 v4` (deposited 2026-03-09, predates IBM hardware sessions of 6–12 April 2026)
  - Willow-side: `willow_hardware_merkabit/PREDICTION.md` SHAs `5bbfdb6f` (2026-04-12) and `745f653f` (2026-04-15) — both prior to any Google hardware access
- **Eight pre-registered Willow observables:** Table 9 of the manuscript, with obs 8 (P(n=39) ≥ 0.85) as the load-bearing falsifier of angle-table specialness identified by §6.2

## Where to find the paper after submission

- **arXiv:** the preprint will be posted to quant-ph and linked here once an arXiv ID is assigned.
- **Zenodo DOI:** a citable Zenodo snapshot of this repository (including the manuscript) will be minted at submission and linked here.
- **Journal version:** when accepted, the journal-formatted version will be linked here alongside the accepted-author-manuscript.

## Iteration history (private repo only — not in public mirror)

The manuscript went through nine major revision cycles between v11 and v19:

- **v11** — author baseline at 2026-04-19. Included §3.3 "directional Fano gap at τ=5" framed as the central hardware result (ΔF = −0.058, no error bar).
- **v12** — added §3.3 per-round Fano forensics paragraph + new §8 bullets (per-round CSV, three τ-sweep simulators). Reframed the τ direction-flip as session-dependent ρ inflation rather than a protocol observable.
- **v13** — Tier-2 author-checklist edits: title softening (option 2), §3.3 + abstract bootstrap CI on ΔF, §4.4 24σ disambiguation, §5.3 interpretation matrix paragraph, §6.1 classical MC caveat.
- **v14** — promoted the 7-node pentachoric error-injection result (F = 0.055 ± 0.010 centre, 0.204 ± 0.029 periphery, det 0.987) to its own §3.6 subsection + a new §1 (v) bullet ("five complementary ways" instead of four).
- **v15** — ZZ-on/off comparison sim (`tau_sweep_lindblad_zz_onoff.py`, 40 configurations × 1500 trajectories, 46 min runtime) replaces the over-strong "coherent ZZ is the mechanism" claim with the corrected "ZZ amplifies but is not necessary" framing. Restored the τ=3 explanation sentence accidentally trimmed in v14.
- **v16** — split the dense §3.3 forensics paragraph into three (¶A session forensics, ¶B three simulator configurations, ¶C what the simulators show) with a bolded run-in header on ¶A.
- **v17** — inlined Figure S1 (`figS_per_round_fano.png`) into the §3.3 prose right after ¶C (size 4.5 × 4.5 inches, centered); added §8 bullet listing submission-time commit SHAs (`6b2ca4d`, `9c6eb5a`, `235f423`, `0c71d64`).
- **v18** — fixed stale `Figure S1` body cross-reference in Figure 3's caption to read `Figure 2` after the manual figure renumber (S1 became Figure 2; subsequent figures shifted +1).
- **v19** — updated GitHub URLs in §8 to point at the new public mirror `SelinaAliens/quantum_combined_paper` (replaces the earlier `quantum_combined_hardware` placeholder).

The intermediate `v11_BACKUP_before_3.3_revision.docx` through `v18.docx` files are held privately. Only v19 is the submission candidate; the earlier versions are kept for revision history and audit trail.

## What's in this repository

The supporting artefacts for the paper are public:

- **Backing data** (`data/`)
  - `seed_dispersion_30seeds.csv` — 30-seed Monte Carlo dispersion (§4.4 of the paper)
  - `angle_perturbation_1000.csv` — 3,000-trial angle-table perturbation control (§6.2)
  - `per_round_fano_summary.csv` — per-round Fano across 5 hardware sessions (§3.3)
  - `tau_sweep_3node_triangle.csv` — classical pentachoric MC, 3-node triangle τ-sweep
  - `tau_sweep_noisy_qiskit.csv` — Qiskit Aer + FakeSherbrooke noise model τ-sweep
  - `tau_sweep_lindblad_triangle.csv` — quantum-trajectory MC + IBM Brisbane noise τ-sweep
  - `tau_sweep_lindblad_zz_onoff.csv` — ZZ-on vs ZZ-off A/B comparison
  - `bootstrap_run3_deltaF.csv` — parametric bootstrap CI on Run 3 ΔF
- **Reproduction scripts** (`simulations/`) — all standalone, all reproducible from a clean checkout; see `simulations/README.md` for the runtime budget per script
- **Figures** (`figures/`) — the per-round Fano forensics figure that became Figure S1 in v17 plus the six other paper figures
- **Section-by-section file map** (`PAPER_GUIDE.md`)
- **§3.3 standalone prose** (`paper/3.3_revised.md`) — the per-round Fano forensics narrative, also embedded directly in the v17 manuscript

## Hardware data

All IBM Eagle r3 and Heron r2 raw counts are in the [IBM hardware track repo](https://github.com/SelinaAliens/merkabit_hardware_test) (`HARDWARE-RESULTS.md` plus `outputs/` JSON files).

The pre-registered Cirq protocols for the Google Willow run are in the [Willow track repo](https://github.com/SelinaAliens/willow_hardware_merkabit), with `PREDICTION.md` carrying the timestamped commit history (SHAs `5bbfdb6f` on 2026-04-12 and `745f653f` on 2026-04-15) that establishes pre-registration before any Google hardware access.

## Citation (interim, until arXiv / DOI assigned)

> Stenberg, S. & Hetland, T. H. *Native Asymmetric-Phase Gates Produce Sub-Poissonian Syndrome Statistics on Superconducting Quantum Processors: Cross-Architecture IBM Evidence and a Pre-Registered Willow Test.* Submission candidate v19, 2026. Code and supplementary data: `https://github.com/SelinaAliens/quantum_combined_paper`.
