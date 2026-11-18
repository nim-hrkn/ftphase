"""Step 5 of the uniform compound procedure: concentration dependence of the defect free energies.  For each Al-Li compound (ACE) and
each side of stoichiometry, cells with k = 2, 4, 6, 8 anti-sites of the constitutional kind at random sites of the largest supercell
of defect_free_energy.py (3 configurations each) get a QHA free energy;
        dG_k(T) = N_cell g_cell(T) - N_perf g_perf(T)      (raw, like eps_d(T));   non-interacting: k eps_d(T)
        interaction coefficient  w(T) = [dG_k - k eps_d] N / k^2   (eV per site per unit concentration squared), least squares over k, configs
so that G(x, T) = Wagner-Schottky(eps_d(T)) + w_side(T) (x - x0)^2 for anti-site constitutional defects.
The anti-sites are placed on the symmetry class of the cheapest single-defect site when it has enough sites, otherwise on all host sites.
    python defect_interaction_cells.py run <Al3Li|B32|Al2Li3|Al4Li9>   -> out/9_interaction_<name>.json
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "alli_ace_txdiagram"))
KS = (2, 4, 6, 8); NCONF = 3


def run(name, ks=KS, sides=("Al_on_Li", "Li_on_Al")):
    import spglib
    from ase.io import read
    from ftphase.validate import relax
    from pipeline import ace, l12_al3li, b32_alli
    import defect_free_energy as dfe
    src, _, sizes, x0 = dfe.SPEC[name]; calc = ace(); rep, psc = sizes[-1]
    prim = l12_al3li() if src == "l12" else b32_alli() if src == "b32" else read(os.path.join(dfe.EX6, "structures", src))
    base = relax(prim, calc, fmax=1e-3, cell=True).atoms; base.calc = None; nb = len(base); sc = base.repeat(rep); N = len(sc)
    ds = spglib.get_symmetry_dataset((base.cell[:], base.get_scaled_positions(), base.numbers), symprec=1e-3); eq = np.asarray(ds.equivalent_atoms if hasattr(ds, "equivalent_atoms") else ds["equivalent_atoms"])
    single = json.load(open(os.path.join(OUT, f"7_defectF_{name}.json")))["sizes"][str(N)]
    f = os.path.join(OUT, f"9_interaction_{name}.json"); res = json.load(open(f)) if os.path.exists(f) else {"x0": x0, "n_sites": N, "cells": {}}
    T, Gp, E0p, ni, fr = dfe.qha(sc.copy(), calc, psc); res["T"] = [float(v) for v in T]; res["perfect_n_imag"] = ni; rng = np.random.default_rng(20261119 + sum(ks))
    for tag, host, new in (("Al_on_Li", "Li", "Al"), ("Li_on_Al", "Al", "Li")):
        if tag not in sides:
            continue
        cls = eq[single["defects"][tag]["site"]]; sites = [i for i in range(N) if eq[i % nb] == cls]
        if len(sites) < 3 * max(ks):
            sites = [i for i in range(N) if base[i % nb].symbol == host]
        for k in ks:
            for c in range(NCONF):
                key = f"{tag}_k{k}_c{c}"; pick = rng.choice(sites, k, replace=False)
                if key in res["cells"]:
                    continue
                at = sc.copy(); t0 = time.time()
                for i in pick:
                    at[int(i)].symbol = new
                x = at.get_chemical_symbols().count("Li") / N
                try:
                    _, Gd, E0d, nid, frd = dfe.qha(at, calc, psc)
                    res["cells"][key] = {"side": tag, "k": k, "x": x, "dG_T_eV": [float(v) for v in (Gd - Gp)], "dE0_eV": E0d - E0p, "n_imag": nid, "imag_weight": frd, "n_site_pool": len(sites), "seconds": time.time() - t0}
                except Exception as e:
                    res["cells"][key] = {"side": tag, "k": k, "x": x, "error": repr(e)[:300]}
                r = res["cells"][key]; print(name, key, "x=%.4f" % x, "dE0 %.4f (k eps_static %.4f)" % (r.get("dE0_eV", np.nan), k * single["defects"][tag]["raw_static_relaxed_cell_eV"]), "n_imag", r.get("n_imag"), r.get("error", ""), f"{time.time() - t0:.0f} s", flush=True)
                json.dump(res, open(f, "w"), indent=1)


if __name__ == "__main__":
    # python defect_interaction_cells.py run <name> [k1,k2,...] [side1,side2]   (extension: more defects per cell on one side)
    run(sys.argv[2], tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else KS, tuple(sys.argv[4].split(",")) if len(sys.argv) > 4 else ("Al_on_Li", "Li_on_Al"))
