#!/usr/bin/env python3
"""
Per-round Fano extractor for the §3.3 rotation-gap forensics.

Reads all four rotation_gap JSON files from
  https://github.com/SelinaAliens/merkabit_hardware_test/tree/main/outputs/rotation_gap

plus the 7-node pentachoric error-injection JSON from
  outputs/pentachoric/pentachoric_error_injection_ibm_strasbourg_20260407.json

and writes:
  - ../data/per_round_fano_summary.csv : tidy long-form table of every
        per-round Fano value across every session, every (paired/control) run.
  - ../figures/figS_per_round_fano.png/.pdf : the headline plot.

Headline finding (motivating the §3.3 rewrite):
  Per-round Fano lives in [0.48, 0.55] across every session, every tau,
  paired or control. Aggregate Fano varies from 0.51 to 5.64 owing to
  session-dependent round-to-round correlation (rho ranging from ~0 to
  ~0.86). The merkabit signature is reproducible at the per-round level;
  the aggregate Fano dependence on tau is not a protocol observable but
  a calibration-drift observable.

Run from this directory:
    python per_round_fano_extractor.py

Defaults assume the IBM hardware test repo is cloned at
    C:\\Users\\selin\\merkabit_hardware_test
which matches the local workstation. Override with --hw-repo if needed.
"""
import os, sys, json, csv, argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_HW_REPO = r"C:\Users\selin\merkabit_hardware_test"
HERE = Path(__file__).resolve().parent
OUT_DATA = HERE.parent / "data"
OUT_FIGS = HERE.parent / "figures"

# -------------------------------------------------------------------------
# Per-source extractors
# -------------------------------------------------------------------------
def load_run1_partial(path):
    """Run 1, 2026-04-07 13:33: tau=1, 3 paired+control; tau=5 failed."""
    with open(path) as f:
        d = json.load(f)
    rows = []
    for entry in d["results"]:
        tau = entry["tau"]
        if entry.get("status") == "failed":
            continue
        for cfg_name, cfg in [("paired", entry.get("paired", {})),
                              ("control", entry.get("control", {}))]:
            if not cfg:
                continue
            per_round = cfg.get("per_round_fano")
            agg_F = cfg.get("fano_factor")
            det = cfg.get("detection_rate")
            if per_round is None and agg_F is not None:
                per_round = [agg_F]      # tau=1 paired stored only as scalar
            if per_round is None:
                continue
            for r_idx, F in enumerate(per_round, start=1):
                rows.append({
                    "session": "Run1_20260407_partial",
                    "backend": "ibm_strasbourg",
                    "tau": tau, "config": cfg_name, "round": r_idx,
                    "fano_per_round": float(F),
                    "fano_aggregate": float(agg_F) if agg_F is not None else float("nan"),
                    "detection_rate": float(det) if det is not None else float("nan"),
                    "shots": d.get("shots", 8192),
                    "job_id": cfg.get("job_id", ""),
                })
    return rows


def load_run2_tau5only(path):
    """Run 2, 2026-04-09 11:17: tau=5 paired only (no control)."""
    with open(path) as f:
        d = json.load(f)
    cfg = d["results"]["paired_tau5"]
    pr_dict = cfg["per_round_fano"]
    if isinstance(pr_dict, dict):
        per_round = [pr_dict[k] for k in sorted(pr_dict, key=int)]
    else:
        per_round = list(pr_dict)
    rows = []
    for r_idx, F in enumerate(per_round, start=1):
        rows.append({
            "session": "Run2_20260409_tau5_paired_only",
            "backend": "ibm_strasbourg",
            "tau": 5, "config": "paired", "round": r_idx,
            "fano_per_round": float(F),
            "fano_aggregate": float(cfg["fano_factor"]),
            "detection_rate": float(cfg["detection_rate"]),
            "shots": d.get("shots", 4096),
            "job_id": cfg.get("job_id", ""),
        })
    return rows


def load_run3_full(path):
    """Run 3, 2026-04-09 11:21: tau=5 paired + control (the §3.3 quote)."""
    with open(path) as f:
        d = json.load(f)
    rows = []
    for cfg_name, key in [("paired", "paired_tau5"), ("control", "unpaired_tau5")]:
        cfg = d["results"].get(key)
        if not cfg:
            continue
        for r_idx, F in enumerate(cfg["per_round_fano"], start=1):
            rows.append({
                "session": "Run3_20260409_full",
                "backend": "ibm_strasbourg",
                "tau": 5, "config": cfg_name, "round": r_idx,
                "fano_per_round": float(F),
                "fano_aggregate": float(cfg["fano_factor"]),
                "detection_rate": float(cfg["detection_rate"]),
                "shots": d.get("shots", 4096),
                "job_id": cfg.get("job_id", ""),
            })
    return rows


def load_earlier_sweep(path):
    """Earlier 'pasted from conversation' sweep, 2026-04-07/08: tau=1, 5, 12 paired only."""
    with open(path) as f:
        d = json.load(f)
    rows = []
    for key in ("tau_1", "tau_5", "tau_12"):
        if key not in d:
            continue
        cfg = d[key]
        for r_idx, F in enumerate(cfg["per_round_fano"], start=1):
            rows.append({
                "session": "Earlier_sweep_20260407",
                "backend": "ibm_strasbourg",
                "tau": cfg["tau"], "config": "paired", "round": r_idx,
                "fano_per_round": float(F),
                "fano_aggregate": float(cfg["fano_factor"]),
                "detection_rate": float(cfg["detection_rate"]),
                "shots": cfg.get("total_shots", 4096),
                "job_id": "",
            })
    return rows


def load_pentachoric(path):
    """7-node Eisenstein cell, tau=1, 28 single-error injections + baseline."""
    with open(path) as f:
        d = json.load(f)
    rows = []
    for entry in d["runs"]:
        # All entries are single-round (tau=1), no per_round_fano list; aggregate F is per-round
        F = entry["fano_factor"]
        det = entry["detection_rate"]
        label = entry["label"]
        is_baseline = (label == "baseline")
        rows.append({
            "session": "Pentachoric_7node_20260407",
            "backend": "ibm_strasbourg",
            "tau": 1,
            "config": "baseline" if is_baseline else "error_injected",
            "round": 1,
            "fano_per_round": float(F),
            "fano_aggregate": float(F),
            "detection_rate": float(det),
            "shots": entry.get("total_shots", 4096),
            "job_id": "",
            "label": label,
            "node": entry.get("node", -1),
            "chirality": entry.get("chirality", 99),
        })
    return rows


# -------------------------------------------------------------------------
# Round-to-round correlation rho: solve aggregate F vs per-round F
# -------------------------------------------------------------------------
def estimate_correlation(per_round_F, aggregate_F, tau):
    """
    Var(sum_t W_t) = sum_t Var(W_t) + 2 sum_{s<t} Cov(W_s, W_t)
    Assume per-round Fano F_r ~ const → Var(W_t) ≈ F_r * <W_t>
    Aggregate F = Var(sum)/<sum> = (sum Var + 2 sum Cov) / sum <W_t>

    With tau equal rounds and F_r the per-round Fano:
        F_agg = F_r * (1 + (tau-1) * rho_eff)
    where rho_eff is the average pairwise correlation coefficient.

    Returns rho_eff. tau=1 returns 0 by definition.
    """
    if tau <= 1:
        return 0.0
    F_per = float(np.mean(per_round_F))
    if F_per <= 1e-9:
        return float("nan")
    return (aggregate_F / F_per - 1.0) / (tau - 1.0)


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hw-repo", default=DEFAULT_HW_REPO,
                    help=f"Path to merkabit_hardware_test clone (default: {DEFAULT_HW_REPO})")
    args = ap.parse_args()

    rg = Path(args.hw_repo) / "outputs" / "rotation_gap"
    pent = Path(args.hw_repo) / "outputs" / "pentachoric"
    sources = [
        ("Run1_partial",  rg / "rotation_gap_partial_ibm_strasbourg_20260407_133351.json", load_run1_partial),
        ("Run2_tau5only", rg / "rotation_gap_tau5_ibm_strasbourg_20260409_111704.json",   load_run2_tau5only),
        ("Run3_full",     rg / "rotation_gap_ibm_strasbourg_20260409_112127.json",        load_run3_full),
        ("EarlierSweep",  rg / "rotation_gap_tau_sweep_ibm_strasbourg_20260407.json",     load_earlier_sweep),
        ("Pentachoric",   pent / "pentachoric_error_injection_ibm_strasbourg_20260407.json", load_pentachoric),
    ]

    all_rows = []
    print("Loading hardware sources:")
    for name, path, loader in sources:
        if not path.exists():
            print(f"  MISSING : {name} -> {path}")
            continue
        rows = loader(path)
        print(f"  ok      : {name:20s} -> {len(rows):3d} rows  ({path.name})")
        all_rows.extend(rows)

    if not all_rows:
        print("No data loaded; aborting.")
        return 1

    # Write CSV
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DATA / "per_round_fano_summary.csv"
    fieldnames = sorted({k for r in all_rows for k in r.keys()})
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print(f"\nWrote {len(all_rows)} rows -> {csv_path}")

    # ---- Summary table: per session, per (tau, config), per-round mean and aggregate ----
    print()
    print("=" * 100)
    print("PER-ROUND vs AGGREGATE FANO across all rotation_gap sessions")
    print("=" * 100)
    header = f"{'Session':>28} | {'tau':>3} | {'config':>8} | {'per-round (mean)':>17} | {'aggregate':>9} | {'rho_eff':>7} | shots"
    print(header)
    print("-" * len(header))

    by_session_tau_cfg = {}
    for r in all_rows:
        if r["session"] == "Pentachoric_7node_20260407":
            continue   # show separately
        key = (r["session"], r["tau"], r["config"])
        by_session_tau_cfg.setdefault(key, []).append(r)

    for key in sorted(by_session_tau_cfg.keys(),
                       key=lambda k: (k[0], k[1], k[2])):
        rows = by_session_tau_cfg[key]
        per_round = [r["fano_per_round"] for r in rows]
        agg = rows[0]["fano_aggregate"]
        tau = rows[0]["tau"]
        rho = estimate_correlation(per_round, agg, tau)
        print(f"{key[0]:>28} | {tau:>3} | {key[2]:>8} | "
              f"{np.mean(per_round):.4f} +/- {np.std(per_round, ddof=1) if len(per_round)>1 else 0.0:.4f} | "
              f"{agg:>9.4f} | {rho:>+7.3f} | {rows[0]['shots']}")

    # ---- Pentachoric breakdown ----
    print()
    print("=" * 100)
    print("PENTACHORIC ERROR INJECTION (7-node Eisenstein cell, tau=1)")
    print("=" * 100)
    pent_rows = [r for r in all_rows if r["session"] == "Pentachoric_7node_20260407"]
    print(f"{'config':>16} | {'chi':>3} | F (mean +/- std) | det rate (mean +/- std) | n")
    print("-" * 80)
    for cfg in ["baseline", "error_injected"]:
        sub = [r for r in pent_rows if r["config"] == cfg]
        if not sub:
            continue
        Fs = [r["fano_per_round"] for r in sub]
        ds = [r["detection_rate"] for r in sub]
        print(f"{cfg:>16} |   - | {np.mean(Fs):.4f} +/- {np.std(Fs, ddof=1) if len(Fs)>1 else 0.0:.4f}  | "
              f"{np.mean(ds):.4f} +/- {np.std(ds, ddof=1) if len(ds)>1 else 0.0:.4f}     | {len(sub)}")
    # Centre vs periphery (chi=0 vs chi!=0) on injected
    inj = [r for r in pent_rows if r["config"] == "error_injected"]
    centre = [r for r in inj if r["chirality"] == 0]
    periph = [r for r in inj if r["chirality"] != 0]
    if centre:
        Fs = [r["fano_per_round"] for r in centre]
        print(f"{'  (chi=0 centre)':>16} |   0 | {np.mean(Fs):.4f} +/- {np.std(Fs, ddof=1):.4f}  | "
              f"{np.mean([r['detection_rate'] for r in centre]):.4f}                  | {len(centre)}")
    if periph:
        Fs = [r["fano_per_round"] for r in periph]
        print(f"{'  (chi=+/-1 periph)':>16} | +/-1| {np.mean(Fs):.4f} +/- {np.std(Fs, ddof=1):.4f}  | "
              f"{np.mean([r['detection_rate'] for r in periph]):.4f}                  | {len(periph)}")

    # ---- Plot: per-round Fano vs aggregate Fano ----
    OUT_FIGS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(2, 1, figsize=(8.5, 8.5),
                            gridspec_kw={"height_ratios": [3, 2]})

    # Top panel: per-round F by session/tau/config (rotation_gap only)
    SESSION_COLOR = {
        "Run1_20260407_partial":            "#1f77b4",
        "Run2_20260409_tau5_paired_only":   "#ff7f0e",
        "Run3_20260409_full":               "#2ca02c",
        "Earlier_sweep_20260407":           "#9467bd",
    }
    SESSION_LABEL = {
        "Run1_20260407_partial":            "Run 1 (Apr 7, $\\tau$=1,3)",
        "Run2_20260409_tau5_paired_only":   "Run 2 (Apr 9 11:17, $\\tau$=5 paired)",
        "Run3_20260409_full":               "Run 3 (Apr 9 11:21, $\\tau$=5 full) [§3.3]",
        "Earlier_sweep_20260407":           "Earlier sweep (Apr 7/8, $\\tau$=1,5,12)",
    }
    CONFIG_MARKER = {"paired": "o", "control": "s"}

    rg_rows = [r for r in all_rows if r["session"] != "Pentachoric_7node_20260407"]
    plotted_labels = set()
    for r in rg_rows:
        col = SESSION_COLOR.get(r["session"], "gray")
        mk = CONFIG_MARKER.get(r["config"], "x")
        # x-position: tau plus a small per-(session, config) jitter
        offset = {"Run1_20260407_partial": -0.18,
                  "Run2_20260409_tau5_paired_only": -0.06,
                  "Run3_20260409_full": +0.06,
                  "Earlier_sweep_20260407": +0.18}.get(r["session"], 0.0)
        if r["config"] == "control":
            offset += 0.02
        x = r["tau"] + offset
        lab_key = (r["session"], r["config"])
        lab = None
        if lab_key not in plotted_labels:
            lab = f"{SESSION_LABEL.get(r['session'], r['session'])} — {r['config']}"
            plotted_labels.add(lab_key)
        ax[0].scatter(x, r["fano_per_round"], c=col, marker=mk, s=42,
                      edgecolor="black", linewidth=0.4, alpha=0.85, label=lab)

    ax[0].axhline(1.0, color="black", linestyle=":", linewidth=0.7,
                  label="Poisson reference F=1")
    ax[0].axhspan(0.48, 0.55, color="grey", alpha=0.12,
                  label="per-round F observed band [0.48, 0.55]")
    ax[0].set_xlabel(r"$\tau$ (rounds)")
    ax[0].set_ylabel("per-round Fano factor")
    ax[0].set_title("Per-round Fano on the 3-merkabit triangle (ibm_strasbourg, 4 sessions)\n"
                    "All sessions, all $\\tau$, paired and control collapse to F$_{\\mathrm{round}}$ "
                    "$\\in [0.48, 0.55]$")
    ax[0].set_xticks([1, 2, 3, 5, 12])
    ax[0].set_ylim(0.40, 1.15)
    ax[0].grid(True, alpha=0.3)
    ax[0].legend(fontsize=7, loc="upper left", framealpha=0.92, ncol=1)

    # Bottom panel: per-round vs aggregate F
    sess_for_agg = []
    for key, rows in by_session_tau_cfg.items():
        per_round = [r["fano_per_round"] for r in rows]
        agg = rows[0]["fano_aggregate"]
        rho = estimate_correlation(per_round, agg, rows[0]["tau"])
        sess_for_agg.append({
            "session": key[0], "tau": key[1], "config": key[2],
            "per_round_mean": np.mean(per_round),
            "aggregate": agg,
            "rho": rho,
        })

    for s in sess_for_agg:
        col = SESSION_COLOR.get(s["session"], "gray")
        mk = CONFIG_MARKER.get(s["config"], "x")
        ax[1].scatter(s["per_round_mean"], s["aggregate"],
                      c=col, marker=mk, s=72, edgecolor="black", linewidth=0.5)
        ax[1].annotate(f"$\\tau$={s['tau']}\n$\\rho$={s['rho']:+.2f}",
                       xy=(s["per_round_mean"], s["aggregate"]),
                       xytext=(6, 4), textcoords="offset points",
                       fontsize=7, alpha=0.82)

    xs = np.linspace(0.45, 0.65, 50)
    for tau, ls in [(1, ":"), (3, "-."), (5, "--"), (12, "-")]:
        # If rounds were uncorrelated, F_agg = F_per_round (rho=0)
        ax[1].plot(xs, xs, color="black", linewidth=0.5, alpha=0.4)
        # rho=0.86 line at given tau (from earlier sweep): F_agg = F_per * (1 + (tau-1)*0.86)
        for rho, lab in [(0.86, "$\\rho$=0.86 (drift)"),]:
            if tau == 5:
                ax[1].plot(xs, xs * (1 + (tau-1)*rho), color="red", linestyle=ls,
                            alpha=0.5,
                            label=f"$\\tau$={tau} at {lab}" if tau == 5 else None)
    ax[1].plot(xs, xs, color="black", linewidth=1.0, alpha=0.6,
                label="$\\rho$=0 (no round-to-round correlation)")

    ax[1].set_xlabel("per-round Fano (mean across rounds)")
    ax[1].set_ylabel("aggregate Fano (full syndrome string)")
    ax[1].set_title("Aggregate F is the same per-round signature plus session-dependent "
                    "round correlation $\\rho$")
    ax[1].set_xlim(0.45, 0.65)
    ax[1].set_yscale("log")
    ax[1].set_ylim(0.4, 8)
    ax[1].grid(True, which="both", alpha=0.3)
    ax[1].legend(fontsize=8, loc="upper left", framealpha=0.92)

    fig.tight_layout()
    png_path = OUT_FIGS / "figS_per_round_fano.png"
    pdf_path = OUT_FIGS / "figS_per_round_fano.pdf"
    fig.savefig(png_path, dpi=150)
    fig.savefig(pdf_path)
    print(f"\nWrote figure -> {png_path}")
    print(f"            -> {pdf_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
