"""Option for the uniform compound procedure: configurational free energy of the defects of ONE compound by a cluster expansion on
its own lattice + Monte Carlo, for the cases where the point-defect model (random, non-interacting or polynomial interaction) is not
enough (the anti-sites avoid or attract each other: regular and random arrangements at the same composition differ by several
meV/atom, e.g. the Al-rich side of ACE B32).

    python defect_ce_mc.py <system> <compound> cells     training cells on the largest supercell of run_defects.py (ideal lattice sites kept):
                                                         perfect, single anti-sites, anti-site pairs by distance (same kind and mixed), regular
                                                         arrays, random sets of 3-16 anti-sites on either side, mixed sets; QHA free energy of each
    python defect_ce_mc.py <system> <compound> fit       one cluster expansion per temperature of G_cell(T) / site (vibrations coarse-grained into
                                                         temperature-dependent ECIs), cross-validated
    python defect_ce_mc.py <system> <compound> mc        semi-grand-canonical MC at each temperature starting from the ordered compound;
                                                         G(x) - G(x0) = integral of (mu_B - mu_A) dx along the branch of the compound
Output: out/<system>/ce_<compound>/ (cells.json, cells.extxyz, ce_<T>.icet, fit.json, mc_<T>.tsv, G_<T>.tsv)
Only anti-sites (both sublattices open to both species); vacancies are not in the lattice model.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
KB = 8.617333262e-5
TS = (300.0, 500.0, 700.0)


def _dirs(system, name):
    d = os.path.join(HERE, "out", system, f"ce_{name}"); os.makedirs(d, exist_ok=True); return d


def cells(system, name, rpair=4.0):
    from ase.io import write
    import run_defects as rd
    cfg, c, calc, base, eq, f, res = rd._setup(system, name); A, B = cfg["elements"]; rep, psc = c["sizes"][-1]; sc = base.repeat(rep); N = len(sc); out = _dirs(system, name)
    sym = np.array(sc.get_chemical_symbols()); iA = np.where(sym == A)[0]; iB = np.where(sym == B)[0]; rng = np.random.default_rng(7); D = sc.get_all_distances(mic=True)
    plan = [("perfect", [], [])]                                             # (tag, sites of A made B [B_on_A], sites of B made A [A_on_B])
    a0, b0 = int(iA[0]), int(iB[0]); plan += [("single_B_on_A", [a0], []), ("single_A_on_B", [], [b0])]
    def shells(i0, pool, rmax=7.5):
        d = np.round(D[i0, pool], 2); out_ = []
        for r in sorted(set(d[(d > 0.1) & (d < rmax)])):
            out_.append((float(r), int(pool[np.where(d == r)[0][0]])))
        return out_
    for r, j in shells(a0, iA): plan.append((f"pair_BA_BA_{r:.2f}", [a0, j], []))
    for r, j in shells(b0, iB): plan.append((f"pair_AB_AB_{r:.2f}", [], [b0, j]))
    for r, j in shells(a0, iB): plan.append((f"pair_BA_AB_{r:.2f}", [a0], [j]))
    # Every inequivalent site, not only the first one of each element: a compound with several inequivalent sites (Al4Li9: 7) has many kinds of
    # neighbour pair, and a pair interaction whose two sites are never both exchanged in the training set is exactly a linear combination of
    # the point terms (rank-deficient fit: the Al4Li9 expansion had rank 34 for 43 parameters and a cross-validation error of 3 meV/atom).
    import spglib
    cls = np.array(spglib.get_symmetry_dataset((sc.cell[:], sc.get_scaled_positions(), sc.numbers), symprec=1e-3).equivalent_atoms); seen = set(); kind = lambda i: "BA" if sym[i] == A else "AB"
    for i0 in sorted(set(cls)):
        i0 = int(i0)
        if i0 not in (a0, b0):
            plan.append((f"single_{kind(i0)}_s{i0}", [i0] if sym[i0] == A else [], [i0] if sym[i0] == B else []))
        d = np.round(D[i0], 2)
        for j in np.argsort(d):
            j = int(j); key = (min(cls[i0], cls[j]), max(cls[i0], cls[j]), float(d[j]))
            if j == i0 or d[j] > rpair or key in seen:
                continue
            seen.add(key); la = [k for k in (i0, j) if sym[k] == A]; lb = [k for k in (i0, j) if sym[k] == B]
            if any(set(la) == set(q[1]) and set(lb) == set(q[2]) for q in plan):
                continue
            plan.append((f"pairs_{kind(i0)}_{kind(j)}_s{i0}_{j}_{d[j]:.2f}", la, lb))
    frac = sc.get_scaled_positions()                                         # regular arrays: one anti-site per original conventional/small block
    for tag, pool in (("B_on_A", iA), ("A_on_B", iB)):
        blk = np.floor(frac[pool] * np.array(rep) + 1e-6).astype(int); first = {}
        for i, b in zip(pool, map(tuple, blk)):
            first.setdefault(b, int(i))
        s_ = sorted(first.values()); plan.append((f"regular_{tag}_{len(s_)}", s_ if tag == "B_on_A" else [], s_ if tag == "A_on_B" else []))
    for k in (3, 4, 6, 8, 12, 16):
        for cc in range(3):
            plan.append((f"rand_B_on_A_k{k}_c{cc}", [int(v) for v in rng.choice(iA, k, replace=False)], []))
            plan.append((f"rand_A_on_B_k{k}_c{cc}", [], [int(v) for v in rng.choice(iB, k, replace=False)]))
    for ka, kb in ((2, 2), (4, 4), (4, 2), (2, 4), (8, 2), (2, 8)):
        for cc in range(2):
            plan.append((f"mixed_{ka}_{kb}_c{cc}", [int(v) for v in rng.choice(iA, ka, replace=False)], [int(v) for v in rng.choice(iB, kb, replace=False)]))
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
    """Did each training cell stay in the parent structure?  Relax it (cell + positions) and measure the strain of the cell relative to the
    perfect one and the displacements from the ideal sites.  A cell whose largest principal strain exceeds ``strain_max`` has left the parent
    structure (e.g. Al-rich ACE B32 with >= 6 Al anti-sites per 128 sites shears into a tetragonal cell, c/a = 0.90): it is another phase and
    must not be used for the defect model or the cluster expansion of this compound."""
    from ase.io import read
    from ftphase.validate import relax
    import run_defects as rd
    cfg = rd.SYSTEMS[system](); calc = cfg["calc"](); out = _dirs(system, name); fj = os.path.join(out, "cells.json"); data = json.load(open(fj)); ideal = read(os.path.join(out, "cells.extxyz"), ":")
    c0 = None
    for s in ideal:
        tag = s.info["tag"]
        if "G_T_eV" not in data["cells"].get(tag, {}) or "strain_max" in data["cells"][tag]:
            c0 = c0 if tag != "perfect" else relax(s.copy(), calc, fmax=1e-3, cell=True).atoms.cell[:]
            continue
        b = relax(s.copy(), calc, fmax=1e-3, cell=True).atoms
        if tag == "perfect":
            c0 = b.cell[:]
        F = np.linalg.solve(c0, b.cell[:]).T; U = 0.5 * (F.T @ F - np.eye(3)); ev = np.linalg.eigvalsh(U - np.trace(U) / 3 * np.eye(3))       # deviatoric (shape) strain: a volume change alone is not a change of structure
        d = b.get_scaled_positions() - s.get_scaled_positions(); d -= np.round(d); disp = np.linalg.norm(d @ b.cell[:], axis=1)
        data["cells"][tag].update({"strain_max": float(np.abs(ev).max()), "disp_rms_A": float(np.sqrt(np.mean(disp ** 2))), "left_parent": bool(np.abs(ev).max() > strain_max)})
        print(tag, "shape strain %.4f" % np.abs(ev).max(), "disp rms %.3f" % data["cells"][tag]["disp_rms_A"], "LEFT THE PARENT STRUCTURE" if data["cells"][tag]["left_parent"] else "", flush=True)
        json.dump(data, open(fj, "w"), indent=1)


def fit(system, name, cutoffs=(7.5, 5.0)):
    from ase.io import read
    from icet import ClusterSpace, StructureContainer, ClusterExpansion
    from trainstation import CrossValidationEstimator
    import run_defects as rd
    cfg = rd.SYSTEMS[system](); A, B = cfg["elements"]; out = _dirs(system, name); data = json.load(open(os.path.join(out, "cells.json"))); T = np.array(data["T"]); ideal = read(os.path.join(out, "cells.extxyz"), ":")
    prim = None; info = {}
    import spglib
    at0 = ideal[0]; lat, pos, num = spglib.standardize_cell((at0.cell[:], at0.get_scaled_positions(), at0.numbers), to_primitive=True, no_idealize=True, symprec=1e-3)   # no idealisation: the sites must coincide with those of the training cells
    from ase import Atoms
    prim = Atoms(numbers=num, cell=lat, scaled_positions=pos, pbc=True)
    use = [(s, data["cells"][s.info["tag"]]) for s in ideal if "G_T_eV" in data["cells"].get(s.info["tag"], {}) and data["cells"][s.info["tag"]].get("n_imag", 0) == 0 and not data["cells"][s.info["tag"]].get("left_parent", False)]
    info["n_structures"] = len(use); info["excluded_left_parent"] = sorted(k for k, v in data["cells"].items() if v.get("left_parent")); info["excluded_imaginary"] = sorted(k for k, v in data["cells"].items() if v.get("n_imag", 0) > 0)
    xs_ = [r["x"] for _, r in use]; info["x_range_of_training"] = [float(min(xs_)), float(max(xs_))]
    # The cutoffs and the fit method are not chosen by hand: every candidate is cross-validated at the middle temperature and the best one is used
    # (a low-symmetry compound has many orbits; with too many parameters least squares interpolates the training set and predicts nothing).
    cands = [[c2] for c2 in (4.0, 5.0, 6.5, 7.5)] + [[c2, c3] for c2 in (5.0, 6.5, 7.5) for c3 in (4.0, 5.0) if c3 <= c2]; best = None; info["candidates"] = []
    im = int(np.argmin(abs(T - TS[len(TS) // 2])))
    for cut in cands:
        try:
            cs_ = ClusterSpace(prim, cutoffs=cut, chemical_symbols=[[A, B]] * len(prim), symprec=1e-3, position_tolerance=1e-2)
        except Exception as e:
            continue
        sc_ = StructureContainer(cs_)
        for s_, r in use:
            sc_.add_structure(s_, properties={"g": r["G_T_eV"][im] / len(s_)})
        A_, _y = sc_.get_fit_data(key="g"); rk = int(np.linalg.matrix_rank(A_, tol=1e-8))
        if rk < A_.shape[1]:            # some interactions are not sampled by the training cells: the fit is not determined (add cells; `cells` samples every inequivalent site)
            info["candidates"].append({"cutoffs": cut, "n_parameters": len(cs_), "rank": rk, "skipped": "rank deficient"}); print(info["candidates"][-1], flush=True); continue
        for fm in ("least-squares", "ardr"):
            if fm == "least-squares" and len(cs_) > 0.5 * len(use):
                continue
            cv_ = CrossValidationEstimator(sc_.get_fit_data(key="g"), fit_method=fm, validation_method="k-fold", n_splits=10, seed=1); cv_.validate()
            info["candidates"].append({"cutoffs": cut, "method": fm, "n_parameters": len(cs_), "rmse_cv_meV": float(cv_.rmse_validation * 1000)}); print(info["candidates"][-1], flush=True)
            if best is None or cv_.rmse_validation < best[0]:
                best = (cv_.rmse_validation, cut, fm, cs_)
    if best is None:
        json.dump(info, open(os.path.join(out, "fit.json"), "w"), indent=1); raise SystemExit("no candidate has a full-rank training set: add training cells")
    _, cut, fm, cs = best; info["n_parameters"] = len(cs); info["cutoffs"] = cut; info["fit_method"] = fm
    for Tq in TS:
        i = int(np.argmin(abs(T - Tq))); scn = StructureContainer(cs)
        for s, r in use:
            scn.add_structure(s, properties={"g": r["G_T_eV"][i] / len(s)})
        cve = CrossValidationEstimator(scn.get_fit_data(key="g"), fit_method=fm, validation_method="k-fold", n_splits=10, seed=1); cve.validate(); cve.train()
        ce = ClusterExpansion(cs, cve.parameters); ce.write(os.path.join(out, f"ce_{int(Tq)}.icet"))
        pred = np.array([ce.predict(s) for s, _ in use]); ref = np.array([r["G_T_eV"][i] / len(s) for s, r in use])
        info[int(Tq)] = {"rmse_train_meV": float(cve.rmse_train * 1000), "rmse_cv_meV": float(cve.rmse_validation * 1000), "n_nonzero": int(np.count_nonzero(cve.parameters)), "max_abs_error_meV": float(np.abs(pred - ref).max() * 1000)}
        print(Tq, info[int(Tq)], flush=True)
    json.dump(info, open(os.path.join(out, "fit.json"), "w"), indent=1)


def mc(system, name, cell=4, n_eq=30, n_av=60):
    import pandas as pd
    from ase.io import read
    from icet import ClusterExpansion
    from mchammer.calculators import ClusterExpansionCalculator
    from mchammer.ensembles import SemiGrandCanonicalEnsemble
    import run_defects as rd
    cfg = rd.SYSTEMS[system](); A, B = cfg["elements"]; out = _dirs(system, name); at0 = read(os.path.join(out, "cells.extxyz"), 0); n0 = len(at0)
    reps = max(1, round((cell ** 3 * 16 / n0) ** (1 / 3))); sc = at0.repeat((reps,) * 3); n = len(sc); x0 = float(np.mean(np.array(sc.get_chemical_symbols()) == B)); data = json.load(open(os.path.join(out, "cells.json"))); T = np.array(data["T"])
    xr = json.load(open(os.path.join(out, "fit.json")))["x_range_of_training"]
    for Tq in TS:
        ce = ClusterExpansion.read(os.path.join(out, f"ce_{int(Tq)}.icet")); i = int(np.argmin(abs(T - Tq)))
        # mu_B - mu_A at which the stoichiometric compound sits: between the two single anti-site free energies (raw, per defect)
        gs = {k: data["cells"][k]["G_T_eV"][i] - data["cells"]["perfect"]["G_T_eV"][i] for k in ("single_B_on_A", "single_A_on_B")}
        mid = 0.5 * (gs["single_B_on_A"] - gs["single_A_on_B"]); half = 0.5 * (gs["single_B_on_A"] + gs["single_A_on_B"]); rows = []
        for sign in (+1, -1):                                               # two branches from the stoichiometric plateau: towards B-rich and towards A-rich
            s = sc.copy(); calc = ClusterExpansionCalculator(s, ce)
            for dm in np.linspace(0.0, 1.15 * half, 47)[1:] if True else []:
                dmu = mid + sign * dm
                ens = SemiGrandCanonicalEnsemble(s, calculator=calc, temperature=float(Tq), chemical_potentials={A: 0.0, B: float(dmu)}, random_seed=int(1000 * dm) + (1 if sign > 0 else 2), ensemble_data_write_interval=n)
                ens.run((n_eq + n_av) * n); d = ens.data_container.data; d = d[d["mctrial"] > n_eq * n]; xb = float(d[f"{B}_count"].mean()) / n; e = float(d["potential"].mean()) / n; s = ens.structure
                sym = np.array(s.get_chemical_symbols()); ref = np.array(sc.get_chemical_symbols()); anti = float(np.mean(sym != ref))
                rows.append({"T": Tq, "branch": "B_rich" if sign > 0 else "A_rich", "dmu": dmu, "x": xb, "E_per_site": e, "antisite_fraction": anti, "x_std": float(d[f"{B}_count"].std()) / n})
                if anti > 0.25 or xb < xr[0] - 0.01 or xb > xr[1] + 0.01:      # left the ordered compound, or the compositions the expansion was trained on: stop the branch
                    break
        df = pd.DataFrame(rows); df.to_csv(os.path.join(out, f"mc_{int(Tq)}.tsv"), sep="\t", index=False, float_format="%.8g")
        # G(x) - G(x0): integrate dG/dx = dmu along each branch (trapezoid), from the first point (x ~ x0)
        G = []
        for br, g in df.groupby("branch"):
            g = g.sort_values("dmu", ascending=(br == "B_rich")); x = g.x.to_numpy(); m = g.dmu.to_numpy(); G0 = 0.0; G.append({"T": Tq, "branch": br, "x": x[0], "dmu": m[0], "G_minus_Gx0": 0.0, "antisite_fraction": g.antisite_fraction.iloc[0]})
            for k in range(1, len(x)):
                G0 += 0.5 * (m[k] + m[k - 1]) * (x[k] - x[k - 1]); G.append({"T": Tq, "branch": br, "x": x[k], "dmu": m[k], "G_minus_Gx0": G0, "antisite_fraction": g.antisite_fraction.iloc[k]})
        pd.DataFrame(G).to_csv(os.path.join(out, f"G_{int(Tq)}.tsv"), sep="\t", index=False, float_format="%.8g")
        print(Tq, "x range", round(df.x.min(), 4), round(df.x.max(), 4), "points", len(df), flush=True)


if __name__ == "__main__":
    {"cells": cells, "check": check, "fit": fit, "mc": mc}[sys.argv[3]](sys.argv[1], sys.argv[2])
