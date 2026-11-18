"""Temperature-dependent point-defect free energies of every Al-Li compound in several cell sizes (general procedure, no prior
knowledge of which compound has a composition range):  for each compound and each of three supercells, the four point defects
(Al on Li site, Li on Al site, Li vacancy, Al vacancy; cheapest symmetry-inequivalent site by static energy) get a QHA free energy,
        eps_d(T) = N_def g_def(T) - N_perf g_perf(T)        (eV per defect, 'raw': the added/removed atom is not referenced)
with g the per-atom QHA free energy at the classical level (same settings as the example-6 table).  eps_d(0 K static) is the number
the Wagner-Schottky curves of Fig. 18 used; its T dependence is the defect vibrational free energy, its size dependence the
defect-defect interaction.     python defect_free_energy.py run <Al3Li|B32|Al2Li3|Al4Li9>   -> out/7_defectF_<name>.json
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram"); sys.path.insert(0, EX6)
# name: (cif or builder, primitive?, [(cell repetition, phonon supercell)], x0)
SPEC = {"Al3Li": ("l12", False, [((2, 2, 2), [2, 2, 2]), ((3, 3, 3), [1, 1, 1]), ((4, 4, 4), [1, 1, 1])], 0.25),
        "B32": ("b32", False, [((1, 1, 1), [2, 2, 2]), ("prim222", [2, 2, 2]), ((2, 2, 2), [1, 1, 1])], 0.5),
        "Al2Li3": ("mp-16506-Li3Al2.cif", False, [((2, 1, 1), [2, 3, 1]), ((2, 2, 1), [2, 2, 1]), ((3, 3, 1), [1, 1, 1])], 0.6),
        "Al4Li9": ("mp-568404-Li9Al4.cif", False, [((1, 1, 1), [1, 3, 2]), ((1, 2, 1), [1, 2, 2]), ((1, 2, 2), [1, 1, 1])], 9 / 13)}
DEF = (("Al_on_Li", "Li", "Al"), ("Li_on_Al", "Al", "Li"), ("Va_Li", "Li", None), ("Va_Al", "Al", None))


def qha(at, calc, psc):
    from ftphase.validate import relax
    from ftphase.qha import phonopy_volume_scan
    from ftphase.quantum import quantum_minus_classical
    from pipeline import T_QHA
    from pipeline_full import SC_FCC, MESH_LENGTH
    r = relax(at, calc, fmax=1e-3, cell=True); a0 = r.atoms.copy(); a0.calc = None
    res, data = phonopy_volume_scan(a0, calc, np.diag(psc), T_QHA, scales=tuple(SC_FCC), mesh=MESH_LENGTH, imaginary="drop", eos="vinet")
    G, V = res.per_atom(); i1 = int(np.argmin(np.abs(np.asarray(SC_FCC) - 1.0))); hw, w = data["frequencies"][i1]; T = np.asarray(T_QHA, dtype=float); dF = np.zeros(len(T)); pos = T > 0
    dF[pos] = quantum_minus_classical(hw, T[pos], weights=w, imaginary="drop") / len(a0)
    return T, (G - dF) * len(a0), float(r.energy_per_atom * len(a0)), int(np.sum(hw < -1e-4)), float(np.sum(w[hw < -1e-4]) / np.sum(w))


def run(name):
    import spglib
    from ase import Atoms
    from ase.io import read
    from ftphase.validate import relax
    from pipeline import ace, l12_al3li, b32_alli
    src, _, sizes, x0 = SPEC[name]; calc = ace(); f = os.path.join(OUT, f"7_defectF_{name}.json"); res = json.load(open(f)) if os.path.exists(f) else {"x0": x0, "sizes": {}}
    prim = l12_al3li() if src == "l12" else b32_alli() if src == "b32" else read(os.path.join(EX6, "structures", src))
    base = relax(prim, calc, fmax=1e-3, cell=True).atoms; base.calc = None
    for rep, psc in sizes:
        if rep == "prim222":
            lat, pos, num = spglib.find_primitive((base.cell[:], base.get_scaled_positions(), base.numbers), symprec=1e-3); b = Atoms(numbers=num, cell=lat, scaled_positions=pos, pbc=True); sc = b.repeat((2, 2, 2))
        else:
            b = base; sc = base.repeat(rep)
        key = str(len(sc))
        if res["sizes"].get(key, {}).get("done"):
            continue
        ds = spglib.get_symmetry_dataset((b.cell[:], b.get_scaled_positions(), b.numbers), symprec=1e-3); eq = np.asarray(ds.equivalent_atoms if hasattr(ds, "equivalent_atoms") else ds["equivalent_atoms"])
        t0 = time.time(); e0s = relax(sc, calc, fmax=2e-3, cell=False).energy_per_atom * len(sc); out = {"n_sites": len(sc), "phonon_supercell": psc, "defects": {}}
        try:
            T, Gp, E0p, ni, fr = qha(sc.copy(), calc, psc); out["perfect"] = {"E0": E0p, "n_imag": ni, "imag_weight": fr}; out["T"] = [float(v) for v in T]
        except Exception as e:
            out["error"] = repr(e)[:300]; res["sizes"][key] = out; json.dump(res, open(f, "w"), indent=1); print(name, key, "perfect failed", out["error"], flush=True); continue
        for tag, host, new in DEF:
            best = None
            for i in sorted(set(eq.tolist())):
                if b[i].symbol != host:
                    continue
                at = sc.copy()
                if new: at[i].symbol = new
                else: del at[i]
                e = relax(at, calc, fmax=2e-3, cell=False).energy_per_atom * len(at) - e0s
                if best is None or e < best[0]:
                    best = (float(e), int(i), at)
            d = {"raw_static_fixed_cell_eV": best[0], "site": best[1]}
            try:
                _, Gd, E0d, ni, fr = qha(best[2].copy(), calc, psc)
                d.update({"raw_static_relaxed_cell_eV": E0d - E0p, "eps_T_eV": [float(v) for v in (Gd - Gp)], "n_imag": ni, "imag_weight": fr})
            except Exception as e:
                d["error"] = repr(e)[:300]
            out["defects"][tag] = d; print(name, key, tag, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items() if k != "eps_T_eV"},
                                              "eps(300,700 K)", [round(d["eps_T_eV"][i], 4) for i in (12, 28)] if "eps_T_eV" in d else None, f"{time.time() - t0:.0f} s", flush=True)
        out["done"] = True; out["seconds"] = time.time() - t0; res["sizes"][key] = out; json.dump(res, open(f, "w"), indent=1)


if __name__ == "__main__":
    run(sys.argv[2])
