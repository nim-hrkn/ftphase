"""Curvature of G(x) at the tip of every line compound of ACE Al-Li from point-defect energies (item 2).

For each compound (Al3Li L1_2, Al2Li3 R-3m, Al4Li9 C2/m; B32 is already a phase with a composition range): relax the cell with ACE,
build a supercell of about 100 sites, and for every symmetry-inequivalent Al site put a Li atom / a vacancy on it, for every
inequivalent Li site an Al atom / a vacancy (static relaxation at fixed cell).  The cheapest site of each defect type gives the
raw defect energy E(defect cell) - E(perfect cell); the Wagner-Schottky model (two sublattices Al_a Li_b, non-interacting defects)
then gives G(x, T) around stoichiometry, whose parabola fit yields d2G/dx2 and dG/dx.  Static energies only (no defect
vibrational entropy).      ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/curvature_compounds.py   -> out/2_curvature.*
"""
# NOTE 2026-11-19: this early script calls the Wagner-Schottky model with g0_atom=0.0, which mis-weights vacancies (their cost per atom is
# eps_Va + g0); harmless here because anti-sites dominate in ACE Al-Li, but use curvature_figure.py / ftphase.compounds for anything new.

import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram")
sys.path.insert(0, EX6)
EV2KJ = 96.48533212


def main():
    import spglib
    from ase.io import read
    from ftphase.validate import relax
    from ftphase.configurational import wagner_schottky_curve
    from pipeline import ace, l12_al3li
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    calc = ace(); sd = os.path.join(EX6, "structures"); os.makedirs(OUT, exist_ok=True)
    comps = [("Al3Li (L1_2)", l12_al3li(), (3, 3, 3), (3, 1)), ("Al2Li3 (R-3m)", read(os.path.join(sd, "mp-16506-Li3Al2.cif")), (3, 3, 1), (2, 3)),
             ("Al4Li9 (C2/m)", read(os.path.join(sd, "mp-568404-Li9Al4.cif")), (1, 2, 2), (4, 9))]
    res = {}; fig, axes = plt.subplots(1, len(comps), figsize=(5.0 * len(comps), 4.0))
    for ax, (name, prim, rep, (a, b)) in zip(axes, comps):
        base = relax(prim, calc, fmax=1e-3, cell=True).atoms; base.calc = None
        ds = spglib.get_symmetry_dataset((base.cell[:], base.get_scaled_positions(), base.numbers), symprec=1e-3)
        eq = np.asarray(ds.equivalent_atoms if hasattr(ds, "equivalent_atoms") else ds["equivalent_atoms"]); sc = base.repeat(rep); n = len(base)
        e0 = relax(sc, calc, fmax=2e-3, cell=False).energy_per_atom * len(sc); raw = {}; table = []
        for i in sorted(set(eq.tolist())):
            host = base[i].symbol; other = "Li" if host == "Al" else "Al"
            for kind in ("antisite", "vacancy"):
                at = sc.copy()
                if kind == "antisite":
                    at[i].symbol = other
                else:
                    del at[i]
                e = relax(at, calc, fmax=2e-3, cell=False).energy_per_atom * len(at) - e0
                key = {("Al", "antisite"): "B_on_A", ("Al", "vacancy"): "Va_on_A", ("Li", "antisite"): "A_on_B", ("Li", "vacancy"): "Va_on_B"}[(host, kind)]
                table.append((f"{host} site {i} (x{int((eq == i).sum())})", kind, round(float(e), 4))); raw[key] = min(raw.get(key, np.inf), float(e))
        x0 = b / (a + b); out = {"sites": len(sc), "x0": round(x0, 5), "inequivalent_sites": int(len(set(eq.tolist()))), "defect_energies_raw_eV": {k: round(v, 4) for k, v in raw.items()}, "cells": table, "T": {}}
        xs = np.linspace(x0 - 0.03, x0 + 0.03, 121)
        for T in (300.0, 500.0, 700.0):
            xf = np.linspace(x0 - 0.012, x0 + 0.012, 25); g = np.array(wagner_schottky_curve(xf, T, (a, b), raw, g0_atom=0.0)); c = np.polyfit(xf - x0, g, 2)
            rms = float(np.sqrt(np.mean((np.polyval(c, xf - x0) - g) ** 2))) * 1000
            out["T"][int(T)] = {"d2G_dx2_eV": round(2 * c[0], 2), "d2G_dx2_kJ_mol": round(2 * c[0] * EV2KJ, 0), "dG_dx_eV": round(c[1], 4), "parabola_rms_meV_within_0.012": round(rms, 3)}
            ax.plot(xs, np.array(wagner_schottky_curve(xs, T, (a, b), raw, g0_atom=0.0)) * 1000, label=f"{T:.0f} K: {2 * c[0]:.1f} eV")
        ax.set(xlabel="x_Li", ylabel="G - G(perfect)  (meV/atom)", title=f"{name}: G(x) from point defects"); ax.title.set_fontsize(9); ax.legend(fontsize=8, title="d2G/dx2")
        res[name] = out; print(name, json.dumps(out["defect_energies_raw_eV"]), {T: v["d2G_dx2_eV"] for T, v in out["T"].items()}, flush=True)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "2_curvature.png"), dpi=150); json.dump(res, open(os.path.join(OUT, "2_curvature.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
