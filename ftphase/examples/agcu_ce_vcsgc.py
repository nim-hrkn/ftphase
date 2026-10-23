"""Ag-Cu CE + MC, second pass: VCSGC instead of SGC, and a cutoff scan for the cluster expansion.

Why: the SGC isotherms of agcu_ce_mc.py (out_agcu_ce/sgc_ce_isotherms.tsv) show almost no hysteresis on the lattice CE
(nucleation is cheap without strain), so the branch ends at the coexistence dmu and its last point is a two-phase state of
the 2048-site cell; the tangent construction then picks that point.  The variance-constrained SGC ensemble (Sadigh &
Erhart 2012; mchammer VCSGCEnsemble) gives one <x> per phi also inside the gap and dF/dx directly, so F(x) is integrated
across the gap and the solvus is the common tangent (widest segment of the lower convex hull of F).

Steps
  1. re-enumerate the 631 orderings (1-8 atoms) and take their relaxed EAM energies from out_agcu_ce/training.tsv
  2. fit CEs for several cutoff sets (ARDR, 10-fold CV), keep the one with the smallest validation rmse
  3. VCSGC on the 8x8x8 conventional cell (2048 sites) at 800/900/1000 K, phi = -2.1 .. 0.1 (step 0.005 near the pure
     elements, 0.05 in the middle; 173 independent points per T, run in parallel); inside the gap the finite cell is
     two-phase and dF/dx follows the common-tangent slope (a tilted baseline in a finite cell), the solvus is where the
     ideal dilute branch fitted to the points nearest each pure element reaches the two-phase level just inside the
     gap (ftphase.ce.solvus_from_vcsgc); an ideal dilute-solution estimate from the CE impurity energies and the
     gap-wide dmu* is given as a check
  4. re-analyse the saved SGC isotherms with the repaired jump detection, and tabulate CE+VCSGC / CE+SGC /
     direct SGC / RK

    python agcu_ce_vcsgc.py [--procs N] [--T 800 900 1000]      -> out_agcu_ce/vcsgc.tsv, gap_vs_T_vcsgc.tsv, F_vcsgc.png, REPORT.md
"""

import argparse
import os
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_agcu_ce")
# x_B ~ -phi/2; the solvus on both sides lies within 0.03 of the pure elements at 800 K, so the ends are sampled in
# steps of 0.005 (x step 0.0025) and the middle in steps of 0.05
PHIS = np.unique(np.round(np.concatenate([np.arange(-2.1, -1.7999, 0.005), np.arange(-1.8, -0.2999, 0.05), np.arange(-0.3, 0.1001, 0.005)]), 3))
CUTOFF_SETS = {"p7t5": [7.0, 5.0], "p9t6": [9.0, 6.0], "p9t6q4": [9.0, 6.0, 4.0], "p11t7q5": [11.0, 7.0, 5.0], "p13t7": [13.0, 7.0]}


def log(m):
    print(time.strftime("%H:%M:%S"), m, flush=True)


def _vcsgc_point(args):
    T, phi, ce_file, seed = args
    from ase.build import bulk
    from icet import ClusterExpansion

    from ftphase.ce import vcsgc_scan

    ce = ClusterExpansion.read(ce_file)
    sc = bulk("Ag", "fcc", a=3.85, cubic=True).repeat((8, 8, 8))
    return vcsgc_scan(ce, sc, T, [phi], ("Ag", "Cu"), kappa=200.0, n_sweeps_eq=20, n_sweeps_av=20, seed=seed)[0]


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    from ase.build import bulk

    from ftphase.ce import dilute_solvus, enumerate_training_structures, fit_cluster_expansion, integrate_isotherm, solvus_from_vcsgc

    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=max(1, os.cpu_count() // 2))
    ap.add_argument("--T", type=float, nargs="+", default=[800.0, 900.0, 1000.0])
    ap.add_argument("--skip-mc", action="store_true")
    a = ap.parse_args()
    prim = bulk("Ag", "fcc", a=3.85)
    syms = [["Ag", "Cu"]]
    structures = enumerate_training_structures(prim, syms, range(1, 9))
    tr = pd.read_csv(os.path.join(OUT, "training.tsv"), sep="\t")
    assert len(tr) == len(structures)
    x = np.array([np.mean(np.array(s.get_chemical_symbols()) == "Cu") for s in structures])
    assert np.allclose(x, tr.x_Cu) and all(len(s) == n for s, n in zip(structures, tr.n_atoms)), "enumeration order changed"
    energies = tr.E_per_atom.values
    fits = []
    for name, cut in CUTOFF_SETS.items():
        ce, info = fit_cluster_expansion(prim, syms, cut, structures, energies, fit_method="ardr", n_splits=10)
        fits.append((info["rmse_validation"], name, ce, info))
        log(f"cutoffs {name} {cut}: {info['n_nonzero_parameters']}/{info['n_parameters']} ECIs, rmse train {info['rmse_train']*1000:.2f} / CV {info['rmse_validation']*1000:.2f} meV/atom")
    fits.sort(key=lambda t: t[0])
    _, best, ce, info = fits[0]
    ce_file = os.path.join(OUT, f"agcu_{best}.ce"); ce.write(ce_file)
    pd.DataFrame([dict(name=n, cutoffs=str(i["cutoffs"]), n_parameters=i["n_parameters"], n_nonzero=i["n_nonzero_parameters"], rmse_train_meV=i["rmse_train"] * 1000, rmse_cv_meV=i["rmse_validation"] * 1000) for _, n, _, i in fits]).to_csv(os.path.join(OUT, "ce_cutoff_scan.tsv"), sep="\t", index=False)
    log(f"best CE: {best}")
    vfile = os.path.join(OUT, "vcsgc.tsv")
    if not a.skip_mc:
        jobs = [(T, float(phi), ce_file, 1000 * int(T) + k) for T in a.T for k, phi in enumerate(PHIS)]
        t0 = time.time()
        with Pool(a.procs) as pool:
            rows = pool.map(_vcsgc_point, jobs, chunksize=1)
        log(f"{len(rows)} VCSGC points in {time.time()-t0:.0f} s on {a.procs} processes")
        pd.DataFrame(rows).to_csv(vfile, sep="\t", index=False)
    v = pd.read_csv(vfile, sep="\t")
    gaps = []
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
    sc = bulk("Ag", "fcc", a=3.85, cubic=True).repeat((8, 8, 8))
    for T in a.T:
        rows = v[np.isclose(v["T"], T)].to_dict("records")
        res = solvus_from_vcsgc(rows)
        dil = dilute_solvus(ce, sc, ("Ag", "Cu"), T, res["dmu_star"]) if np.isfinite(res["dmu_star"]) else {"x_alpha": np.nan, "x_beta": np.nan, "E_imp_B_in_A": np.nan, "E_imp_A_in_B": np.nan}
        gaps.append({"T": T, "x_alpha": res["x_alpha"], "x_beta": res["x_beta"], "dmu_star": res["dmu_star"], "x_alpha_dilute": dil["x_alpha"], "x_beta_dilute": dil["x_beta"], "E_imp_Cu_in_Ag": dil["E_imp_B_in_A"], "E_imp_Ag_in_Cu": dil["E_imp_A_in_B"]})
        axs[0].plot(res["x"], res["dF_dx"], ".-", ms=3, label=f"{T:.0f} K")
        axs[1].plot(res["x"], res["F"] * 1000, ".-", ms=3, label=f"{T:.0f} K")
        if np.isfinite(res["x_alpha"]):
            fa, fb = np.interp([res["x_alpha"], res["x_beta"]], res["x"], res["F"]) * 1000
            axs[1].plot([res["x_alpha"], res["x_beta"]], [fa, fb], "k--", lw=0.8)
        log(f"VCSGC {T:.0f} K: dmu* = {res['dmu_star']:+.3f} eV, x_alpha = {res['x_alpha']:.3f}, x_beta = {res['x_beta']:.3f}; dilute estimate {dil['x_alpha']:.3f} / {dil['x_beta']:.3f} (E_imp Cu in Ag {dil['E_imp_B_in_A']:.3f}, Ag in Cu {dil['E_imp_A_in_B']:.3f} eV)")
    axs[0].set_xlabel("x_Cu"); axs[0].set_ylabel("dF/dx (eV/atom)"); axs[1].set_xlabel("x_Cu"); axs[1].set_ylabel("F - F(Ag) (meV/atom), configurational, static CE"); axs[1].legend(fontsize=8)
    fig.suptitle(f"Ag-Cu CE ({best}) + VCSGC, 2048 sites", fontsize=9); fig.tight_layout(); fig.savefig(os.path.join(OUT, "F_vcsgc.png"), dpi=140)
    pd.DataFrame(gaps).to_csv(os.path.join(OUT, "gap_vs_T_vcsgc.tsv"), sep="\t", index=False)
    # SGC re-analysis with the repaired jump detection (first-pass CE, p7t5)
    iso = pd.read_csv(os.path.join(OUT, "sgc_ce_isotherms.tsv"), sep="\t")
    sgc = {}
    for T in a.T:
        up = iso[np.isclose(iso["T"], T) & (iso.direction == "up")][["dmu", "x_B"]].values
        dn = iso[np.isclose(iso["T"], T) & (iso.direction == "down")][["dmu", "x_B"]].values
        if len(up) and len(dn):
            r = integrate_isotherm(up, dn); sgc[T] = (r["x_alpha"], r["x_beta"], float(r["jump_up"][2]), float(r["jump_down"][3]))
    direct = pd.read_csv(os.path.join(HERE, "agcu_sgcmc/out/gap_vs_T.tsv"), sep="\t")
    rk = pd.read_csv(os.path.join(HERE, "agcu_sgcmc/out/rk_gap.tsv"), sep="\t")
    f = lambda df, col, T: f"{float(df[np.isclose(df['T'], T)][col].iloc[0]):.3f}" if len(df[np.isclose(df["T"], T)]) else "-"
    L = ["# Ag-Cu fcc miscibility gap: cluster expansion (icet, EAM-trained) + MC vs direct-potential SGC MC vs ideal + RK", "",
         "## Cluster expansion (631 enumerated fcc orderings with 1-8 atoms, EAM Williams-Mishin-Hamilton 2006, positions + cell relaxed)", "",
         "| cutoffs (pair, triplet, quadruplet; A) | ECIs (nonzero/total) | rmse train | rmse 10-fold CV (meV/atom) |", "|---|---|---|---|"]
    for _, n, _, i in sorted(fits, key=lambda t: t[1]):
        L.append(f"| {n} {i['cutoffs']} | {i['n_nonzero_parameters']}/{i['n_parameters']} | {i['rmse_train']*1000:.2f} | {i['rmse_validation']*1000:.2f} |")
    L += ["", f"Formation energies of the training set are 0-134 meV/atom (all positive); the CV error of about 10 meV/atom (any cutoff) is the lattice-CE limit for this 13 % size-mismatch pair with relaxed energies. VCSGC used `{best}`; the SGC pass used p7t5.", "",
          "## Solvus (fcc miscibility gap), x_Cu", "",
          "| T (K) | CE+VCSGC x_alpha | CE dilute x_alpha | CE+SGC x_alpha | direct MC x_alpha | RK x_alpha | CE+VCSGC x_beta | CE dilute x_beta | CE+SGC x_beta | direct MC x_beta | RK x_beta | dmu* VCSGC / direct (eV) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for g in gaps:
        T = g["T"]; s = sgc.get(T, (np.nan,) * 4)
        L.append(f"| {T:.0f} | {g['x_alpha']:.3f} | {g['x_alpha_dilute']:.3f} | {s[0]:.3f} | {f(direct, 'x_alpha_tangent', T)} | {f(rk, 'x_alpha', T)} | {g['x_beta']:.3f} | {g['x_beta_dilute']:.3f} | {s[1]:.3f} | {f(direct, 'x_beta_tangent', T)} | {f(rk, 'x_beta', T)} | {g['dmu_star']:+.3f} / {f(direct, 'dmu_star_eV', T)} |")
    g0 = gaps[0]
    L += ["", f"* CE+VCSGC: variance-constrained SGC (kappa = 200, {len(PHIS)} phi points per T, 20 + 20 sweeps, 2048 sites, independent random starts), dF/dx = -k_B T kappa (phi + 2<x>); inside the gap the 2048-site cell is two-phase and dF/dx follows the common-tangent slope, but not exactly flat (it varies by about 0.1 eV across the gap: the interface free energy of the precipitate changes with its size and shape), so the solvus is where the ideal dilute branch c + k_B T ln(x/(1-x)), with c fitted to the 4 points nearest the pure element, reaches the two-phase level measured just inside the gap (median of dF/dx over 0.05 < x < 0.15 and 0.85 < x < 0.95; ftphase.ce.solvus_from_vcsgc); dmu* is the median of dF/dx over the gap.",
          f"* CE dilute: ideal dilute solution with the CE impurity energies (Cu in Ag {g0['E_imp_Cu_in_Ag']:.3f} eV, Ag in Cu {g0['E_imp_Ag_in_Cu']:.3f} eV, 2048-site cells) and the VCSGC dmu*: x_alpha = exp((dmu*_mix - E_imp)/k_B T).",
          "* CE+SGC: the first pass (agcu_ce_mc.py), branch integration with the repaired jump detection; the lattice CE shows no hysteresis, so the alpha branch ends at the coexistence dmu and the last pre-jump point of a 2048-site SGC run is already a two-phase state (first-pass table: 0.122 / 0.341 / 0.141).",
          "* direct MC: LAMMPS fix atom/swap SGC on the EAM (agcu_sgcmc/), 2048 atoms with MD, branch integration.  RK: random 32-atom cells + ideal mixing + calphy/QHA vibrations (example 9).",
          "* CE+MC (both ensembles) is static: no vibrational contribution, lattice-mapped relaxed energies; the CE truncation error (10 meV/atom) is larger than k_B T x ln x differences that set a dilute solvus, so the CE route is not expected to reproduce the direct-potential gap for Ag-Cu."]
    with open(os.path.join(OUT, "REPORT.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
