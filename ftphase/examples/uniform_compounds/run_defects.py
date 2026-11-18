"""Defect free energies for the uniform compound procedure (ftphase.compounds), for any system registered in SYSTEMS.

    python run_defects.py <system> single <compound>     four point defects (cheapest symmetry-inequivalent site) x 3 cell sizes x QHA
    python run_defects.py <system> multi  <compound>     cells with k constitutional defects per side (kind read from the single-defect
                                                         free energies of the largest cell), 3 random configurations each, QHA
Output: out/<system>/defects_<compound>.json
    sizes[N]: T, g_perfect_per_atom(T), defects[key]: eps_T (raw, eV per defect), static energies, site, n_imag
    multi: constitutional {A_rich, B_rich}, cells[key]: side, defect, k, x, dG_T (raw), n_imag
Defect keys: A_on_B (an A atom on a B site), B_on_A, Va_on_A, Va_on_B; A, B = the two elements of the system in this order,
x = fraction of B.  Free energies at the classical level (QHA lowered by F_q - F_cl), like the free-energy tables.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXA = os.path.join(HERE, "..")
KEYS = (("A_on_B", 1, "sub"), ("B_on_A", 0, "sub"), ("Va_on_A", 0, "vac"), ("Va_on_B", 1, "vac"))      # key, host element index, kind


def _nial_eam():
    sys.path.insert(0, os.path.join(EXA, "nial_eam")); import pipeline as p
    st = p.structures()
    return {"elements": ("Al", "Ni"), "calc": p.eam, "T": np.arange(0.0, 2001.0, 50.0), "scales": p.SCALES, "mesh": p.MESH_LENGTH, "T_decide": 1200.0,
            "compounds": {"NiAl3": {"atoms": st["NiAl3"][0], "site_counts": (3, 1), "sizes": [((1, 1, 2), [2, 2, 1]), ((2, 1, 2), [1, 2, 1]), ((2, 2, 2), [1, 1, 1])]},
                          "Ni2Al3": {"atoms": st["Ni2Al3"][0], "site_counts": (3, 2), "sizes": [((2, 2, 2), [2, 2, 2]), ((3, 3, 2), [1, 1, 1]), ((3, 3, 3), [1, 1, 1])]},
                          "B2": {"atoms": st["B2-NiAl"][0], "site_counts": (1, 1), "sizes": [((3, 3, 3), [2, 2, 2]), ((4, 4, 4), [1, 1, 1]), ((5, 5, 5), [1, 1, 1])]},
                          "L12": {"atoms": st["L12-Ni3Al"][0], "site_counts": (1, 3), "sizes": [((2, 2, 2), [2, 2, 2]), ((3, 3, 3), [1, 1, 1]), ((4, 4, 4), [1, 1, 1])]}}}


SYSTEMS = {"nial_eam": _nial_eam}


def qha(at, calc, psc, cfg):
    from ftphase.validate import relax
    from ftphase.qha import phonopy_volume_scan
    from ftphase.quantum import quantum_minus_classical
    r = relax(at, calc, fmax=1e-3, cell=True); a0 = r.atoms.copy(); a0.calc = None; sc = tuple(cfg["scales"]); T = np.asarray(cfg["T"], dtype=float)
    res, data = phonopy_volume_scan(a0, calc, np.diag(psc), T, scales=sc, mesh=cfg["mesh"], imaginary="drop", eos="vinet")
    G, V = res.per_atom(); i1 = int(np.argmin(np.abs(np.asarray(sc) - 1.0))); hw, w = data["frequencies"][i1]; dF = np.zeros(len(T)); pos = T > 0
    dF[pos] = quantum_minus_classical(hw, T[pos], weights=w, imaginary="drop") / len(a0)
    return (G - dF) * len(a0), float(r.energy_per_atom * len(a0)), int(np.sum(hw < -1e-4)), float(np.sum(w[hw < -1e-4]) / np.sum(w))


def _setup(system, name):
    import spglib
    from ftphase.validate import relax
    cfg = SYSTEMS[system](); c = cfg["compounds"][name]; calc = cfg["calc"](); A, B = cfg["elements"]
    base = relax(c["atoms"], calc, fmax=1e-3, cell=True).atoms; base.calc = None
    ds = spglib.get_symmetry_dataset((base.cell[:], base.get_scaled_positions(), base.numbers), symprec=1e-3); eq = np.asarray(ds.equivalent_atoms if hasattr(ds, "equivalent_atoms") else ds["equivalent_atoms"])
    out = os.path.join(HERE, "out", system); os.makedirs(out, exist_ok=True); f = os.path.join(out, f"defects_{name}.json")
    res = json.load(open(f)) if os.path.exists(f) else {"system": system, "compound": name, "elements": [A, B], "site_counts": list(c["site_counts"]), "x0": c["site_counts"][1] / float(sum(c["site_counts"])), "sizes": {}}
    return cfg, c, calc, base, eq, f, res


def _defect(sc, i_list, kind, other):
    at = sc.copy()
    if kind == "sub":
        for i in i_list:
            at[int(i)].symbol = other
    else:
        del at[[int(i) for i in i_list]]
    return at


def single(system, name):
    from ftphase.validate import relax
    cfg, c, calc, base, eq, f, res = _setup(system, name); el = cfg["elements"]; nb = len(base)
    for rep, psc in c["sizes"]:
        sc = base.repeat(rep); N = len(sc); key = str(N)
        if res["sizes"].get(key, {}).get("done"):
            continue
        t0 = time.time(); e0s = relax(sc, calc, fmax=2e-3, cell=False).energy_per_atom * N; out = {"n_sites": N, "phonon_supercell": psc, "defects": {}, "T": [float(v) for v in cfg["T"]]}
        try:
            Gp, E0p, ni, fr = qha(sc.copy(), calc, psc, cfg); out["perfect"] = {"E0": E0p, "n_imag": ni, "imag_weight": fr}; out["g_perfect_per_atom"] = [float(v) for v in Gp / N]
        except Exception as e:
            out["error"] = repr(e)[:300]; res["sizes"][key] = out; json.dump(res, open(f, "w"), indent=1); print(name, key, "perfect failed", out["error"], flush=True); continue
        for dk, host, kind in KEYS:
            best = None
            for i in sorted(set(eq.tolist())):
                if base[i].symbol != el[host]:
                    continue
                at = _defect(sc, [i], kind, el[1 - host]); e = relax(at, calc, fmax=2e-3, cell=False).energy_per_atom * len(at) - e0s
                if best is None or e < best[0]:
                    best = (float(e), int(i), at)
            d = {"raw_static_fixed_cell_eV": best[0], "site": best[1]}
            try:
                Gd, E0d, ni, fr = qha(best[2].copy(), calc, psc, cfg); d.update({"raw_static_relaxed_cell_eV": E0d - E0p, "eps_T_eV": [float(v) for v in (Gd - Gp)], "n_imag": ni, "imag_weight": fr})
            except Exception as e:
                d["error"] = repr(e)[:300]
            out["defects"][dk] = d
            print(name, key, dk, "static %.4f" % best[0], "eps(mid, high T)", [round(d["eps_T_eV"][i], 4) for i in (len(cfg["T"]) // 2, -1)] if "eps_T_eV" in d else d.get("error"), "n_imag", d.get("n_imag"), f"{time.time() - t0:.0f} s", flush=True)
        out["done"] = True; out["seconds"] = time.time() - t0; res["sizes"][key] = out; json.dump(res, open(f, "w"), indent=1)


def multi(system, name, ks=(2, 4, 8, 12), nconf=3):
    from ftphase.compounds import CompoundModel
    cfg, c, calc, base, eq, f, res = _setup(system, name); el = cfg["elements"]; nb = len(base); rep, psc = c["sizes"][-1]; sc = base.repeat(rep); N = len(sc)
    big = res["sizes"][str(N)]; T = np.array(big["T"]); ok = {k: v["eps_T_eV"] for k, v in big["defects"].items() if "eps_T_eV" in v}
    m = CompoundModel(name, res["x0"], tuple(c["site_counts"]), T, ok); g0 = float(np.interp(cfg["T_decide"], T, big["g_perfect_per_atom"])); sd = m.constitutional_defects(cfg["T_decide"], g0)
    mu = res.setdefault("multi", {"n_sites": N, "cells": {}}); mu["constitutional_defects"] = sd; mu["T_decide"] = cfg["T_decide"]; print(name, "constitutional defects", sd, flush=True)
    Gp, E0p, ni, fr = qha(sc.copy(), calc, psc, cfg); rng = np.random.default_rng(20261119)
    for side in ("A_rich", "B_rich"):
        dk = sd[side]; host, kind = {k: (h, kd) for k, h, kd in KEYS}[dk]; cls = eq[big["defects"][dk]["site"]]
        sites = [i for i in range(N) if eq[i % nb] == cls]
        if len(sites) < 3 * max(ks):
            sites = [i for i in range(N) if base[i % nb].symbol == el[host]]
        for k in ks:
            for cc in range(nconf):
                key = f"{dk}_k{k}_c{cc}"; pick = rng.choice(sites, k, replace=False)
                if key in mu["cells"]:
                    continue
                at = _defect(sc, pick, kind, el[1 - host]); t0 = time.time(); x = at.get_chemical_symbols().count(el[1]) / len(at)
                try:
                    Gd, E0d, nid, frd = qha(at, calc, psc, cfg); mu["cells"][key] = {"side": side, "defect": dk, "k": k, "x": x, "dG_T_eV": [float(v) for v in (Gd - Gp)], "dE0_eV": E0d - E0p, "n_imag": nid, "imag_weight": frd}
                except Exception as e:
                    mu["cells"][key] = {"side": side, "defect": dk, "k": k, "x": x, "error": repr(e)[:300]}
                print(name, key, "x=%.4f" % x, "n_imag", mu["cells"][key].get("n_imag"), mu["cells"][key].get("error", ""), f"{time.time() - t0:.0f} s", flush=True)
                json.dump(res, open(f, "w"), indent=1)


if __name__ == "__main__":
    {"single": single, "multi": multi}[sys.argv[2]](sys.argv[1], sys.argv[3])
