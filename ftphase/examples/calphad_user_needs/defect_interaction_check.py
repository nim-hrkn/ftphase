"""Is G(x) of a line compound away from the tip an extrapolation?  The Wagner-Schottky curve uses the energy of ONE defect in a
108-site cell (x0 +- 0.009) and assumes that defects do not interact.  Check for Al3Li (ACE): cells with 2, 3 and 4 anti-sites of
one kind at random sites (5 configurations each) against n times the single-defect energy.
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/defect_interaction_check.py  -> out/2_defect_interaction.json
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "alli_ace_txdiagram"))


def main():
    from ftphase.validate import relax
    from pipeline import ace, l12_al3li
    calc = ace(); base = relax(l12_al3li(), calc, fmax=1e-3, cell=True).atoms; base.calc = None; sc = base.repeat((3, 3, 3)); sym = np.array(sc.get_chemical_symbols())
    e0 = relax(sc, calc, fmax=2e-3, cell=False).energy_per_atom * len(sc); rng = np.random.default_rng(0); res = {}
    for kind, host, new in (("Li on Al site (Li-rich side)", "Al", "Li"), ("Al on Li site (Al-rich side)", "Li", "Al")):
        sites = np.where(sym == host)[0]; rows = []
        for n in (1, 2, 3, 4):
            es = []
            for c in range(1 if n == 1 else 5):
                at = sc.copy(); pick = rng.choice(sites, n, replace=False)
                for i in pick:
                    at[i].symbol = new
                es.append(relax(at, calc, fmax=2e-3, cell=False).energy_per_atom * len(at) - e0)
            x = (np.sum(sym == "Li") + (n if new == "Li" else -n)) / len(sc); rows.append((n, round(float(x), 4), [round(float(v), 4) for v in es]))
        e1 = rows[0][2][0]
        res[kind] = {"single_defect_eV": e1, "cells": [{"n_defects": n, "x_Li": x, "E_minus_perfect_eV": es, "mean_per_defect_eV": round(float(np.mean(es)) / n, 4),
                                                     "deviation_from_n_times_single_meV_per_atom": round(float(np.mean(es) - n * e1) / len(sc) * 1000, 3),
                                                     "spread_meV_per_atom": round(float(np.std(es)) / len(sc) * 1000, 3)} for n, x, es in rows]}
        for r in res[kind]["cells"]:
            print(kind, r["n_defects"], "x =", r["x_Li"], "E/defect", r["mean_per_defect_eV"], "| deviation from non-interacting:", r["deviation_from_n_times_single_meV_per_atom"], "meV/atom, spread", r["spread_meV_per_atom"], flush=True)
    json.dump(res, open(os.path.join(HERE, "out", "2_defect_interaction.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
