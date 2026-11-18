"""The 'phase with a composition range' treatment of example 6's B32 (small cells with one anti-site on each side of stoichiometry,
QHA free energy, two-sublattice anti-site configurational entropy, spline through the three compositions) applied to the three line
compounds, for comparison with their Wagner-Schottky curves in curvature_figure.py (Fig. 18).
Cells: Al3Li 2x2x2 (32 atoms, x = 7/32, 8/32, 9/32), Al2Li3 2x1x1 (30 atoms, x = 17/30, 18/30, 19/30), Al4Li9 1x1x1 (26 atoms,
x = 17/26, 18/26, 19/26); the anti-site sits on the cheapest symmetry-inequivalent site (static energy in that cell).
    python range_phase_compounds.py run Al3Li|Al2Li3|Al4Li9      -> out/6_range_<name>.tsv / .json   (QHA, ACE, a few minutes each)
"""
import json, os, sys, time
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram"); sys.path.insert(0, EX6)
SPEC = {"Al3Li": (None, (2, 2, 2), [2, 2, 2], 0.25), "Al2Li3": ("mp-16506-Li3Al2.cif", (2, 1, 1), [2, 3, 1], 0.6), "Al4Li9": ("mp-568404-Li9Al4.cif", (1, 1, 1), [1, 3, 2], 9 / 13)}


def run(name):
    import spglib
    from ase.io import read
    from ftphase.validate import relax
    from ftphase.qha import phonopy_volume_scan
    from ftphase.quantum import quantum_minus_classical
    from pipeline import ace, l12_al3li, T_QHA, MODEL
    from pipeline_full import SC_FCC, MESH_LENGTH
    cif, rep, psc, x0 = SPEC[name]; calc = ace(); prim = l12_al3li() if cif is None else read(os.path.join(EX6, "structures", cif))
    base = relax(prim, calc, fmax=1e-3, cell=True).atoms; base.calc = None
    ds = spglib.get_symmetry_dataset((base.cell[:], base.get_scaled_positions(), base.numbers), symprec=1e-3); eq = np.asarray(ds.equivalent_atoms if hasattr(ds, "equivalent_atoms") else ds["equivalent_atoms"])
    sc = base.repeat(rep); e0 = relax(sc, calc, fmax=2e-3, cell=False).energy_per_atom * len(sc); cells = {"stoich": sc.copy()}; info = {"n_atoms": len(sc), "x0": x0, "static": {}}
    for host, other, tag in (("Li", "Al", "Al_on_Li"), ("Al", "Li", "Li_on_Al")):
        best = None
        for i in sorted(set(eq.tolist())):
            if base[i].symbol != host:
                continue
            at = sc.copy(); at[i].symbol = other; e = relax(at, calc, fmax=2e-3, cell=False).energy_per_atom * len(at) - e0
            if best is None or e < best[0]:
                best = (float(e), i, at)
        cells[tag] = best[2]; info["static"][tag] = {"raw_eV_fixed_cell": round(best[0], 4), "site": int(best[1])}
    rows = []
    for tag, at in cells.items():
        t0 = time.time(); r = relax(at, calc, fmax=1e-3, cell=True); a0 = r.atoms.copy(); a0.calc = None; x = a0.get_chemical_symbols().count("Li") / len(a0)
        res, data = phonopy_volume_scan(a0, calc, np.diag(psc), T_QHA, scales=tuple(SC_FCC), mesh=MESH_LENGTH, imaginary="drop", eos="vinet")
        G, V = res.per_atom(); i1 = int(np.argmin(np.abs(np.asarray(SC_FCC) - 1.0))); hw, w = data["frequencies"][i1]; T = np.asarray(T_QHA, dtype=float); dF = np.zeros(len(T)); pos = T > 0
        dF[pos] = quantum_minus_classical(hw, T[pos], weights=w, imaginary="drop") / len(a0)
        info[tag] = {"x": x, "E0_eV_per_atom": float(r.energy_per_atom), "n_imag_modes": int(np.sum(hw < -1e-4)), "imag_weight_fraction": float(np.sum(w[hw < -1e-4]) / np.sum(w)), "sg": f"{r.spacegroup_before}->{r.spacegroup_after}", "seconds": time.time() - t0}
        for Tk, g, v in zip(T, G - dF, V):
            rows.append({"phase": name, "kind": "limited", "x": x, "T": float(Tk), "P_GPa": 0.0, "G": float(g), "G_err": 0.0, "V": float(v), "model": MODEL, "reference_state": "absolute ACE energy",
                         "method": f"QHA vinet, phonopy sc={psc} mesh=60.0, classical level; {len(a0)}-atom cell, {tag} (range_phase_compounds.py)", "config_entropy": "none", "quantum": "classical+harmonic-correction",
                         "n_atoms": len(a0), "source": f"calphad_user_needs range {name} {tag}"})
        print(name, tag, json.dumps(info[tag]), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, f"6_range_{name}.tsv"), sep="\t", index=False); json.dump(info, open(os.path.join(OUT, f"6_range_{name}.json"), "w"), indent=1)


if __name__ == "__main__":
    run(sys.argv[2]) if sys.argv[1] == "run" else None
