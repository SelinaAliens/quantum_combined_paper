# Simulations — reproducing §4.4

Two scripts:

| File | Role |
|---|---|
| `sim_scaling_comparison.py` | Frozen copy of `willow_hardware_merkabit/simulations/sim_scaling_comparison.py`. Provides the `simulate(cell, tau, epsilon, shots, seed, paired)` entry point and the `build_hex_cell(r)` / `build_square_cell(side)` cell builders. |
| `seed_sweep_driver.py` | Wrapper that imports `simulate()` and runs it across seeds 1..30 on the four headline cells, writing `../data/seed_dispersion_30seeds.csv`. |

## Why a frozen copy?

`sim_scaling_comparison.py` lives upstream in `willow_hardware_merkabit`. The live version may evolve; the version here is pinned to the form that produced the seed-dispersion CSV cited in the paper. The two are byte-identical at submission time.

## Reproducing §4.4 from scratch

```bash
# Clone this repo
git clone https://github.com/SelinaAliens/quantum_combined_hardware
cd quantum_combined_hardware/simulations

# Run the seed sweep (numpy required)
python seed_sweep_driver.py
# Produces ../data/seed_dispersion_30seeds.csv after ~5 minutes
```

Expected output: 30 lines of progress (`seed N/30 done (...s elapsed, ...s ETA)`) followed by a results table. The 4×4 square-cell row should report `F_paired = 0.3703 ± 0.0258` to within shot noise.

## Reproducing the original Paper 26 [15] single-seed numbers

```bash
# Inside Python REPL after `import sim_scaling_comparison as sim`:
cell = sim.build_square_cell(4)              # 4×4 = 16 nodes
result = sim.simulate(cell, tau=5, epsilon=0.10, shots=20000, seed=42, paired=True)
print(result["fano"])                        # expect 0.286 ± shot noise
```

The seed=42 result reproduces the published Paper 26 [15] value `F = 0.285` to within shot noise (Monte Carlo dispersion at 20 000 shots is ≈ 0.005). The seed-averaged value across 30 seeds is `F = 0.370 ± 0.026` (see `../data/seed_dispersion_30seeds.csv` and §4.4 of the manuscript).

## Dependencies

- Python ≥ 3.10
- numpy ≥ 1.20

That's it. No qiskit, no cirq, no scipy. The Monte Carlo is pure numpy.

## Wall-time notes

- Single seed, single cell, 20 000 shots: ~1 s (4×4) to ~0.5 s (3-node hex)
- Full seed sweep (30 seeds × 4 cells × 2 configs): ~5 minutes serial, ~30 s if you multiprocess across seeds
- The `seed_sweep_driver.py` is intentionally serial for reproducibility; if you want parallel, wrap the inner loop with `multiprocessing.Pool`.
