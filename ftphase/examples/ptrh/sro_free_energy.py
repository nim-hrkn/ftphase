"""Configurational free energy of the Pt-Rh fcc solid solution WITH short-range order: canonical MC on the cluster expansion of
ce_mc.py (out_ce_<mlip>/ce.icet) integrated over 1/T from the random state (ftphase.ce.canonical_free_energy).
    env/ftphase/bin/python sro_free_energy.py --mlip mace-mpa-0 [--T-min 100] [--n-beta 48] [--cell 8] [--procs 8]
-> out_ce_<mlip>/sro.tsv : x, T, E, E_random, F_conf, F_ideal (= E_random - T S_ideal, what random cells + ideal mixing assume),
   dF_sro = F_conf - F_ideal, S_conf, Cv, alpha1 (Warren-Cowley, first shell).  eV/atom, k_B/atom.  No vibrations (lattice CE).
"""
import argparse, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); KB = 8.617333262e-5


def one(args):
    mlip, x, Ts, cell, neq, nav = args
    from ase.build import bulk, make_supercell
    from icet import ClusterExpansion
    from ftphase.ce import canonical_free_energy
    ce = ClusterExpansion.read(os.path.join(HERE, f"out_ce_{mlip}", "ce.icet"))
    sc = make_supercell(bulk("Pt", "fcc", a=3.87), cell * np.array([[-1, 1, 1], [1, -1, 1], [1, 1, -1]]))
    t0 = time.time(); rows = canonical_free_energy(ce, sc, x, ("Pt", "Rh"), Ts, n_sweeps_eq=neq, n_sweeps_av=nav, seed=int(round(x * 1000)))
    print(f"x={x:.3f} done in {time.time() - t0:.0f} s", flush=True); return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mlip", required=True); ap.add_argument("--T-min", type=float, default=100.0); ap.add_argument("--n-beta", type=int, default=48)
    ap.add_argument("--cell", type=int, default=8); ap.add_argument("--procs", type=int, default=8); ap.add_argument("--n-eq", type=int, default=20); ap.add_argument("--n-av", type=int, default=40)
    ap.add_argument("--xs", type=float, nargs="+", default=[round(0.05 * i, 2) for i in range(1, 20)]); a = ap.parse_args()
    import multiprocessing as mp
    import pandas as pd
    Ts = 1.0 / (KB * np.linspace(0, 1.0 / (KB * a.T_min), a.n_beta + 1)[1:])           # uniform in beta, descending T
    with mp.Pool(a.procs) as pool:
        res = pool.map(one, [(a.mlip, x, Ts, a.cell, a.n_eq, a.n_av) for x in a.xs], chunksize=1)
    df = pd.DataFrame([r for rows in res for r in rows]); out = os.path.join(HERE, f"out_ce_{a.mlip}", "sro.tsv"); df.to_csv(out, sep="\t", index=False, float_format="%.8g"); print("wrote", out)


if __name__ == "__main__":
    main()
