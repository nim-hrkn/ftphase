"""Route A with a cluster expansion (CE + MC, icet) for Ag-Cu, to be compared with route B (direct-potential SGC MC,
agcu_sgcmc/) and the ideal + Redlich-Kister route (AiiDA example 9).

Steps (EAM Williams-Mishin-Hamilton 2006, static energies):
  1. enumerate fcc orderings with 1-8 atoms per cell (icet), relax positions + cell with the EAM, energies per atom
  2. fit a CE (pairs to 7.0 A, triplets to 5.0 A, ARDR with 10-fold CV), report rmse
  3. SGC MC on the CE (8x8x8 conventional = 2048 sites) at 800, 900, 1000 K, dmu = mu_Cu - mu_Ag from -1.0 to -0.3 eV up
     and down (same protocol as the direct MC), branch integration -> solvus
  4. compare: CE+MC vs direct SGC MC (agcu_sgcmc/out/gap_vs_T.tsv) vs RK (agcu_sgcmc/out/rk_gap.tsv)

    python agcu_ce_mc.py            (CPU, about 20-40 min; writes out_agcu_ce/)
"""

import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POT = os.path.join(ROOT, "potentials/agcu/CuAg.eam.alloy")
OUT = os.path.join(HERE, "out_agcu_ce")
T_LIST = [800.0, 900.0, 1000.0]
DMU = np.round(np.arange(-1.0, -0.299, 0.02), 3)


def log(m):
    print(time.strftime("%H:%M:%S"), m, flush=True)


def main():
    import pandas as pd
    from ase.build import bulk
    from ase.calculators.lammpslib import LAMMPSlib

    from ftphase.ce import enumerate_training_structures, fit_cluster_expansion, integrate_isotherm, relaxed_energies, sgc_scan

    os.makedirs(OUT, exist_ok=True)
    calc = LAMMPSlib(lmpcmds=["pair_style eam/alloy", f"pair_coeff * * {POT} Ag Cu"], atom_types={"Ag": 1, "Cu": 2}, keep_alive=True, log_file=None)
    prim = bulk("Ag", "fcc", a=3.85)          # between Ag (4.09) and Cu (3.615); the lattice is only the CE's reference, cells are relaxed
    syms = [["Ag", "Cu"]]
    t0 = time.time()
    structures = enumerate_training_structures(prim, syms, range(1, 9))
    log(f"{len(structures)} enumerated structures (1-8 atoms)")
    energies = relaxed_energies(structures, calc, fmax=2e-3, cell=True)
    e_ag = energies[[i for i, s in enumerate(structures) if set(s.get_chemical_symbols()) == {"Ag"}][0]]
    e_cu = energies[[i for i, s in enumerate(structures) if set(s.get_chemical_symbols()) == {"Cu"}][0]]
    log(f"relaxed in {time.time()-t0:.0f} s; E(Ag) = {e_ag:.4f}, E(Cu) = {e_cu:.4f} eV/atom")
    cutoffs = [7.0, 5.0]
    ce, info = fit_cluster_expansion(prim, syms, cutoffs, structures, energies, fit_method="ardr", n_splits=10)
    log(f"CE: {info}")
    ce.write(os.path.join(OUT, "agcu.ce"))
    x = np.array([np.mean(np.array(s.get_chemical_symbols()) == "Cu") for s in structures])
    e_form = energies - (1 - x) * e_ag - x * e_cu
    pd.DataFrame({"x_Cu": x, "n_atoms": [len(s) for s in structures], "E_per_atom": energies, "E_form": e_form, "E_ce": [ce.predict(s) for s in structures]}).to_csv(os.path.join(OUT, "training.tsv"), sep="\t", index=False)
    log(f"formation energies: min {e_form.min()*1000:.1f} meV/atom (all positive = phase separating: {bool((e_form > -1e-6).all())})")
    sc = bulk("Ag", "fcc", a=3.85, cubic=True).repeat((8, 8, 8))
    rows, gaps = [], []
    for T in T_LIST:
        for d in ("up", "down"):
            t1 = time.time()
            r = sgc_scan(ce, sc, T, DMU, ("Ag", "Cu"), n_sweeps_eq=20, n_sweeps_av=20, direction=d, seed=int(T))
            rows += r
            log(f"T={T:.0f} {d}: {len(r)} dmu points in {time.time()-t1:.0f} s; x from {r[0]['x_B']:.3f} to {r[-1]['x_B']:.3f}")
        up = np.array([[q["dmu"], q["x_B"]] for q in rows if q["T"] == T and q["direction"] == "up"])
        down = np.array([[q["dmu"], q["x_B"]] for q in rows if q["T"] == T and q["direction"] == "down"])
        res = integrate_isotherm(up, down)
        gaps.append({"T": T, "x_alpha": res["x_alpha"], "x_beta": res["x_beta"], "dmu_star": res["dmu_star"], "x_alpha_jump": float(res["jump_up"][2]), "x_beta_jump": float(res["jump_down"][3])})
        log(f"T={T:.0f}: tangent x_alpha={res['x_alpha']:.3f} x_beta={res['x_beta']:.3f} dmu*={res['dmu_star']:+.3f}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "sgc_ce_isotherms.tsv"), sep="\t", index=False)
    pd.DataFrame(gaps).to_csv(os.path.join(OUT, "gap_vs_T.tsv"), sep="\t", index=False)
    L = ["# Ag-Cu fcc miscibility gap: cluster expansion (icet, EAM-trained) + SGC MC vs direct-potential SGC MC vs ideal + RK", "",
         f"CE: {info['n_structures']} structures (1-8 atoms, relaxed), cutoffs {cutoffs} A, {info['n_nonzero_parameters']}/{info['n_parameters']} nonzero ECIs (ARDR), rmse train {info['rmse_train']*1000:.2f} / validation {info['rmse_validation']*1000:.2f} meV/atom", "",
         "| T (K) | CE+MC x_alpha | direct MC x_alpha | RK x_alpha | CE+MC x_beta | direct MC x_beta | RK x_beta |", "|---|---|---|---|---|---|---|"]
    direct = pd.read_csv(os.path.join(HERE, "agcu_sgcmc/out/gap_vs_T.tsv"), sep="\t") if os.path.exists(os.path.join(HERE, "agcu_sgcmc/out/gap_vs_T.tsv")) else None
    rk = pd.read_csv(os.path.join(HERE, "agcu_sgcmc/out/rk_gap.tsv"), sep="\t") if os.path.exists(os.path.join(HERE, "agcu_sgcmc/out/rk_gap.tsv")) else None
    for g in gaps:
        dm = direct[np.isclose(direct["T"], g["T"])] if direct is not None else None
        rr = rk[np.isclose(rk["T"], g["T"])] if rk is not None else None
        f = lambda df, col: f"{float(df[col].iloc[0]):.3f}" if (df is not None and len(df)) else "-"
        L.append(f"| {g['T']:.0f} | {g['x_alpha']:.3f} | {f(dm, 'x_alpha_tangent')} | {f(rr, 'x_alpha')} | {g['x_beta']:.3f} | {f(dm, 'x_beta_tangent')} | {f(rr, 'x_beta')} |")
    L += ["", "CE+MC and direct MC share the SGC protocol; their difference is the CE truncation (static, lattice-mapped energies, no vibrations in either MC).",
          "The RK route uses random 32-atom cells + ideal mixing + calphy/QHA vibrations; its difference from the MC routes is the interpolation + no short-range order."]
    with open(os.path.join(OUT, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
