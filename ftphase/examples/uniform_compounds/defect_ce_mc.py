"""Option for the uniform compound procedure: configurational free energy of the defects of ONE compound by a cluster expansion on
its own lattice + Monte Carlo, for the cases where the point-defect model (random, non-interacting or polynomial interaction) is not
enough (the anti-sites avoid or attract each other: regular and random arrangements at the same composition differ by several
meV/atom, e.g. the Al-rich side of ACE B32).

    python defect_ce_mc.py <system> <compound> cells     training cells on the largest supercell of run_defects.py (ideal lattice sites kept):
                                                         perfect, single anti-sites, anti-site pairs by distance (same kind and mixed), regular
                                                         arrays, random sets of 3-16 anti-sites on either side, mixed sets; QHA free energy of each
    python defect_ce_mc.py <system> <compound> fit       one cluster expansion per temperature of G_cell(T) / site (vibrations coarse-grained into
                                                         temperature-dependent ECIs), cross-validated
    python defect_ce_mc.py <system> <compound> check     relax every cell: cells that leave the parent structure are marked and excluded
    python defect_ce_mc.py <system> <compound> harvest   configurations the Monte Carlo runs into (training supercell) -> harvest.extxyz; then
                                                         cells -> check -> fit again, until nothing new is harvested
    python defect_ce_mc.py <system> <compound> mc        semi-grand-canonical MC at each temperature starting from the ordered compound;
                                                         G(x) - G(x0) = integral of (mu_B - mu_A) dx along the branch of the compound
Output: out/<system>/ce_<compound>/ (cells.json, cells.extxyz, ce_<T>.icet, fit.json, mc_<T>.tsv, G_<T>.tsv)
Only anti-sites (both sublattices open to both species); vacancies are not in the lattice model.
The method lives in ftphase.defect_ce (training_plan, structure_check, fit_expansion, harvest, sgc_scan, branch_free_energy); this file is
the driver that computes the cells with the system's calculator (QHA) and keeps the files.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
KB = 8.617333262e-5
TS = (300.0, 500.0, 700.0)


def _dirs(system, name):
    d = os.path.join(HERE, "out", system, f"ce_{name}"); os.makedirs(d, exist_ok=True); return d


def _load(system, name):
    from ase.io import read
    import run_defects as rd
    cfg = rd.SYSTEMS[system](); out = _dirs(system, name); data = json.load(open(os.path.join(out, "cells.json"))); ideal = read(os.path.join(out, "cells.extxyz"), ":")
    return cfg, out, data, ideal, np.array(data["T"])


def _usable(data, ideal):
    ok = lambda r: "G_T_eV" in r and r.get("n_imag", 0) == 0 and not r.get("left_parent", False)
    return [(s, data["cells"][s.info["tag"]]) for s in ideal if ok(data["cells"].get(s.info["tag"], {}))]


def _plateau(data, i):
    from ftphase.defect_ce import plateau
    g = {k: data["cells"][k]["G_T_eV"][i] - data["cells"]["perfect"]["G_T_eV"][i] for k in ("single_B_on_A", "single_A_on_B")}
    return plateau(g["single_B_on_A"], g["single_A_on_B"])


def cells(system, name, rpair=4.0):
    from ase.io import read, write
    from ftphase.defect_ce import training_plan
    import run_defects as rd
    cfg, c, calc, base, eq, f, res = rd._setup(system, name); A, B = cfg["elements"]; rep, psc = c["sizes"][-1]; sc = base.repeat(rep); N = len(sc); out = _dirs(system, name)
    sym = np.array(sc.get_chemical_symbols()); plan = training_plan(sc, A, B, rpair=rpair, blocks=rep)
    fh = os.path.join(out, "harvest.extxyz")           # configurations the Monte Carlo ran into (`harvest`): computed and added to the training set
    if os.path.exists(fh):
        for h in read(fh, ":"):
            hs = np.array(h.get_chemical_symbols()); plan.append((h.info["tag"], [int(k) for k in np.where((sym == A) & (hs == B))[0]], [int(k) for k in np.where((sym == B) & (hs == A))[0]]))
    fj = os.path.join(out, "cells.json"); done = json.load(open(fj)) if os.path.exists(fj) else {"n_sites": N, "T": [float(v) for v in cfg["T"]], "cells": {}}; ideal = []
    for tag, la, lb in plan:
        at = sc.copy()
        for i in la: at[i].symbol = B
        for i in lb: at[i].symbol = A
        ideal.append(at.copy()); ideal[-1].info["tag"] = tag
        if tag in done["cells"] and "G_T_eV" in done["cells"][tag]:
            continue
        t0 = time.time()
        try:
            G, E0, ni, fr = rd.qha(at.copy(), calc, psc, cfg); done["cells"][tag] = {"x": float(np.mean(np.array(at.get_chemical_symbols()) == B)), "G_T_eV": [float(v) for v in G], "E0_eV": E0, "n_imag": ni, "n_B_on_A": len(la), "n_A_on_B": len(lb)}
        except Exception as e:
            done["cells"][tag] = {"error": repr(e)[:200]}
        print(tag, {k: v for k, v in done["cells"][tag].items() if k != "G_T_eV"}, f"{time.time() - t0:.0f} s", flush=True); json.dump(done, open(fj, "w"), indent=1)
    write(os.path.join(out, "cells.extxyz"), ideal)


def check(system, name, strain_max=0.02):
    from ftphase.defect_ce import structure_check
    from ftphase.validate import relax
    cfg, out, data, ideal, T = _load(system, name); calc = cfg["calc"](); fj = os.path.join(out, "cells.json")
    c0 = relax(ideal[0].copy(), calc, fmax=1e-3, cell=True).atoms.cell[:]; assert ideal[0].info["tag"] == "perfect"
    for s in ideal:
        r = data["cells"].get(s.info["tag"], {})
        if "G_T_eV" not in r or "strain_max" in r:
            continue
        r.update(structure_check(s, relax(s.copy(), calc, fmax=1e-3, cell=True).atoms, c0, strain_max))
        print(s.info["tag"], "shape strain %.4f" % r["strain_max"], "disp rms %.3f" % r["disp_rms_A"], "LEFT THE PARENT STRUCTURE" if r["left_parent"] else "", flush=True)
        json.dump(data, open(fj, "w"), indent=1)


def fit(system, name):
    from ftphase.defect_ce import fit_expansion
    cfg, out, data, ideal, T = _load(system, name); use = _usable(data, ideal); idx = [int(np.argmin(abs(T - Tq))) for Tq in TS]
    Y = np.array([[r["G_T_eV"][i] / len(s) for i in idx] for s, r in use]); info = {"n_structures": len(use)}
    info["excluded_left_parent"] = sorted(k for k, v in data["cells"].items() if v.get("left_parent")); info["excluded_imaginary"] = sorted(k for k, v in data["cells"].items() if v.get("n_imag", 0) > 0)
    try:
        f = fit_expansion([s for s, _ in use], Y, cfg["elements"], verbose=True, allow_rank_deficit=int(os.environ.get("CE_RANK_DEFICIT", 0)))   # CE_RANK_DEFICIT=n: see fit_expansion
    except ValueError as e:
        json.dump(info, open(os.path.join(out, "fit.json"), "w"), indent=1); raise SystemExit(str(e)[:300])
    info.update({"x_range_of_training": list(f.x_range), "cutoffs": f.cutoffs, "fit_method": f.method, "n_parameters": len(f.cluster_space), "cells_that_alone_fix_a_parameter": f.n_single_cell_parameters,
                 "candidates": [{k: (v * 1000 if k == "rmse_cv" else v) for k, v in c.items()} for c in f.candidates]})
    for k, Tq in enumerate(TS):
        ce = f.expansion(k); ce.write(os.path.join(out, f"ce_{int(Tq)}.icet")); pred = np.array([ce.predict(s) for s, _ in use])
        info[int(Tq)] = {"rmse_train_meV": float(f.rmse_train[k] * 1000), "rmse_cv_meV": float(f.rmse_cv[k] * 1000), "n_nonzero": int(np.count_nonzero(f.parameters[k])), "max_abs_error_meV": float(np.abs(pred - Y[:, k]).max() * 1000)}
        print(Tq, info[int(Tq)], flush=True)
    json.dump(info, open(os.path.join(out, "fit.json"), "w"), indent=1)


def harvest(system, name):
    from ase.io import read, write
    from icet import ClusterExpansion
    import ftphase.defect_ce as dc
    cfg, out, data, ideal, T = _load(system, name); A, B = cfg["elements"]; fh = os.path.join(out, "harvest.extxyz"); old = read(fh, ":") if os.path.exists(fh) else []
    it = 1 + max([int(h.info["tag"].split("_")[1][1:]) for h in old], default=0); new = []
    for Tq in (TS[0], TS[-1]):
        ce = ClusterExpansion.read(os.path.join(out, f"ce_{int(Tq)}.icet")); mid, half = _plateau(data, int(np.argmin(abs(T - Tq))))
        for h in dc.harvest(ce, ideal[0], Tq, mid, half, species=(A, B), known=old + new):
            h.info = {"tag": f"harvest_i{it}_T{int(Tq)}_{h.info['branch']}_{len(new)}", "ce_G_per_site": h.info["predicted"], "antisite_fraction": h.info["antisite_fraction"]}; new.append(h)
            print(h.info, "x = %.3f" % np.mean(np.array(h.get_chemical_symbols()) == B), flush=True)
    write(fh, old + new); print("harvested", len(new), "new configurations (iteration %d)" % it)


def mc(system, name, cell=4):
    import pandas as pd
    from icet import ClusterExpansion
    import ftphase.defect_ce as dc
    cfg, out, data, ideal, T = _load(system, name); A, B = cfg["elements"]; at0 = ideal[0]; reps = max(1, round((cell ** 3 * 16 / len(at0)) ** (1 / 3))); sc = at0.repeat((reps,) * 3)
    xr = json.load(open(os.path.join(out, "fit.json")))["x_range_of_training"]
    for Tq in TS:
        ce = ClusterExpansion.read(os.path.join(out, f"ce_{int(Tq)}.icet")); mid, half = _plateau(data, int(np.argmin(abs(T - Tq))))
        df = dc.sgc_scan(ce, sc, Tq, mid, half, species=(A, B), x_range=xr); df.insert(0, "T", Tq); df.to_csv(os.path.join(out, f"mc_{int(Tq)}.tsv"), sep="\t", index=False, float_format="%.8g")
        G = []                 # raw integral along each branch from its first point (the curve with the branch ends cut: ftphase.defect_ce.branch_free_energy)
        for br, g in df.groupby("branch"):
            g = g.sort_values("dmu", ascending=(br == "B_rich")); x = g.x.to_numpy(); m = g.dmu.to_numpy(); G0 = np.concatenate([[0.0], np.cumsum(0.5 * (m[1:] + m[:-1]) * np.diff(x))])
            G += [{"T": Tq, "branch": br, "x": x[k], "dmu": m[k], "G_minus_Gx0": G0[k], "antisite_fraction": g.antisite_fraction.iloc[k]} for k in range(len(x))]
        pd.DataFrame(G).to_csv(os.path.join(out, f"G_{int(Tq)}.tsv"), sep="\t", index=False, float_format="%.8g")
        print(Tq, "x range", round(df.x.min(), 4), round(df.x.max(), 4), "points", len(df), flush=True)


def lattice(system, name, cell=3, dx=0.08, step=0.02):
    """G(x) per site of the phase on this compound's lattice in whatever state of order the Monte Carlo finds (integration from the random
    state; ftphase.defect_ce.lattice_free_energy), around the stoichiometric composition and inside the trained range -> lattice_<T>.tsv.
    For compounds whose ordered state does not survive in `mc`, and as a check of `mc` where it does."""
    from icet import ClusterExpansion
    import ftphase.defect_ce as dc
    cfg, out, data, ideal, T = _load(system, name); A, B = cfg["elements"]; at0 = ideal[0]; reps = max(1, round((cell ** 3 * 16 / len(at0)) ** (1 / 3))); sc = at0.repeat((reps,) * 3)
    xr = json.load(open(os.path.join(out, "fit.json")))["x_range_of_training"]; x0 = float(np.mean(np.array(at0.get_chemical_symbols()) == B))
    xs = [x for x in x0 + np.arange(-dx, dx + 1e-9, step) if xr[0] <= x <= xr[1]]
    for Tq in TS:
        ce = ClusterExpansion.read(os.path.join(out, f"ce_{int(Tq)}.icet")); i = int(np.argmin(abs(T - Tq)))
        df = dc.lattice_free_energy(ce, sc, xs, Tq, species=(A, B), n_grid=16); df["G_perfect_compound"] = data["cells"]["perfect"]["G_T_eV"][i] / len(at0)
        df.to_csv(os.path.join(out, f"lattice_{int(Tq)}.tsv"), sep="\t", index=False, float_format="%.8g")
        j = int(np.argmin(abs(df.x - x0))); print(Tq, "sites", len(sc), "| at x0: G_lattice - G_perfect = %+.1f meV/site, alpha1 %.2f, S_conf %.2f k_B" % (1000 * (df.G[j] - df.G_perfect_compound[j]), df.alpha1[j], df.S_conf_kB[j]), flush=True)


if __name__ == "__main__":
    {"cells": cells, "check": check, "fit": fit, "harvest": harvest, "mc": mc, "lattice": lattice}[sys.argv[3]](sys.argv[1], sys.argv[2])
