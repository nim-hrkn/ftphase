"""calcfunctions of the T-x WorkChain: stages 01/02 (``prepare_cells``) and 04-07 (``assemble_diagram``).

Both run inside the daemon worker (seconds to a minute); the heavy stages 03A/03B are CalcJobs.

``spec`` (Dict) describes the system; all keys documented in :func:`prepare_cells` and
:func:`assemble_diagram`.  Candidate 0 K structures come in as StructureData.
"""

import io
import json
import os
import tempfile
import time
from functools import partial

import numpy as np
import pandas as pd
from aiida import orm
from aiida.engine import calcfunction

from ftphase.records import FreeEnergyTable

SITE_MODELS = {
    "b32_antisite": ("ftphase.configurational", "b32_antisite_site_fractions"),
    "b2_triple_defect": ("ftphase.configurational", "b2_triple_defect_site_fractions"),
}


def _site_model(name: str, stoich_x=None):
    import importlib

    mod, fn = SITE_MODELS[name]
    f = getattr(importlib.import_module(mod), fn)
    return partial(f, stoich_x=stoich_x) if stoich_x is not None else f


def _series(base, xel, others, xs, seed, n_configs):
    """composition_series that also works when the host of ``base`` is the x element itself (Ni-rich fcc, Ni-side
    liquid): then the other element is substituted with fraction 1 - x and x is converted back.
    Returns [(x_target, x_actual, seed, atoms, counts)]."""
    from ftphase.structures import composition_series

    host = set(base.get_chemical_symbols())
    if host == {xel}:
        sub = [e for e in others if e != xel][0]
        res = composition_series(base, sub, [1.0 - v for v in xs if v < 1.0], seed=seed, n_configs=n_configs)
        return [(1.0 - m.x_target, 1.0 - m.x_actual, m.seed, m.atoms, m.counts) for m in res]
    res = composition_series(base, xel, [v for v in xs if v > 0], seed=seed, n_configs=n_configs)
    return [(m.x_target, m.x_actual, m.seed, m.atoms, m.counts) for m in res]


def _defect_cells(base, xel, ops, seed=0):
    """Defect series of an ordered cell: ops = [{"replace": [from_el, to_el], "n": k} | {"vacancy": el, "n": k}].
    Atoms are chosen at random (seed) among the sites of the named element; returns [(x, atoms, label)]."""
    rng = np.random.default_rng(seed)
    out = []
    for op in ops:
        at = base.copy()
        syms = np.array(at.get_chemical_symbols())
        if "replace" in op:
            a, b = op["replace"]
            idx = rng.choice(np.where(syms == a)[0], int(op["n"]), replace=False)
            for i in idx:
                at[int(i)].symbol = b
            label = f"{op['n']} {b} on {a} sites"
        else:
            el = op["vacancy"]
            idx = sorted(rng.choice(np.where(syms == el)[0], int(op["n"]), replace=False), reverse=True)
            for i in idx:
                del at[int(i)]
            label = f"{op['n']} {el} vacancies"
        sy = at.get_chemical_symbols()
        out.append((sy.count(xel) / len(sy), at, label))
    return out


def _key(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in s)


def _calculator(spec: dict, potential_path: str):
    from ftphase.aiida.runners import make_calculator

    # same calculator as the QHA stage: spec["qha_*"] keys select Kokkos arguments (GRACE 1L/2L/3L on the GPU) or a torch-based
    # ASE calculator (SevenNet / MACE); stage 01 then runs inside the daemon worker with that calculator
    inp = {"pair_style": spec.get("qha_pair_style", spec["pair_style"]), "pair_coeff": spec["pair_coeff"], "atom_types": spec["atom_types"],
           **{k: spec[f"qha_{k}"] for k in ("cmdargs", "calculator", "device", "dtype", "modal") if f"qha_{k}" in spec}}
    return make_calculator(inp, potential_path)


def _antisite_cells(atoms, x_element: str):
    """x -1/N and +1/N cells of an ordered AB cell: swap the first B atom to A and the first A atom to B."""
    syms = atoms.get_chemical_symbols()
    others = [s for s in sorted(set(syms)) if s != x_element]
    other = others[0]
    i_b = syms.index(x_element)
    i_a = syms.index(other)
    lo = atoms.copy(); lo[i_b].symbol = other
    hi = atoms.copy(); hi[i_a].symbol = x_element
    n = len(atoms)
    nb = syms.count(x_element)
    return [((nb - 1) / n, lo), ((nb + 1) / n, hi)]


@calcfunction
def prepare_cells(spec: orm.Dict, potential: orm.SinglefileData, **candidates: orm.StructureData):
    """Stages 01 and 02: relax the candidates, 0 K hull and ground-state check, build the solid
    cells for QHA and the liquid cells for calphy.

    spec keys used here
      elements, masses, x_element, pair_style, pair_coeff ("... {potential} ..."), atom_types,
      candidates: {name: x} for each StructureData passed as keyword,
      known_ground_states: [names],
      relax: {fmax, cell},
      solids: [ {phase, kind (solution|limited|point), base, repeat, x: [..], n_configs, series
                 (random|sqs), seed, supercell, mesh, antisites (bool), icet: {cutoffs, n_steps}} ],
      liquids: {base, repeat, x: [..], seed, T_sweep: [T_start, T_stop], T_override: {"0.10": 800},
                n_repeats, n_equilibration_steps, n_switching_steps, n_iterations, mode}
    Returns hull (Dict), solid_params (Dict: key -> meta), liquid_params (Dict: tag -> meta) and
    one StructureData per cell (solid_<key>, liquid_<tag>).
    """
    from ftphase.structures import composition_series, sqs_icet
    from ftphase.validate import compare_ground_states, hull_0K, relax

    sp = spec.get_dict()
    out = {}
    with potential.as_path() as ppath:
        rel = sp.get("relax", {})
        rows, relaxed = [], {}
        names = list(sp["candidates"])
        if sp.get("qha_calculator", "lammps") != "lammps" and sp.get("qha_python"):
            # torch-based calculator: relax in a subprocess of its own env (the daemon's env has no torch)
            import json
            import subprocess
            import tempfile

            from ase.io import read, write

            with tempfile.TemporaryDirectory(prefix="ftphase_relax_") as td:
                write(os.path.join(td, "in.extxyz"), [candidates[_key(n)].get_ase() for n in names])
                inp = {"structures": os.path.join(td, "in.extxyz"), "potential": str(ppath), "relax": rel, "pair_style": sp.get("qha_pair_style", sp["pair_style"]),
                       "pair_coeff": sp["pair_coeff"], "atom_types": sp["atom_types"], "output": os.path.join(td, "out.json"), "output_structures": os.path.join(td, "relaxed.extxyz"),
                       **{k: sp[f"qha_{k}"] for k in ("cmdargs", "calculator", "device", "dtype", "modal") if f"qha_{k}" in sp}}
                json.dump(inp, open(os.path.join(td, "input.json"), "w"))
                env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
                subprocess.run([sp["qha_python"], "-m", "ftphase.aiida.runners", "relax", os.path.join(td, "input.json")], check=True, cwd=td, env=env)
                res = json.load(open(os.path.join(td, "out.json"))); rl = read(os.path.join(td, "relaxed.extxyz"), index=":")
            for name, r, a in zip(names, res, rl):
                relaxed[name] = a.copy(); relaxed[name].calc = None
                rows.append({"name": name, "x": float(sp["candidates"][name]), **r})
        else:
            calc = _calculator(sp, str(ppath))
            for name, x in sp["candidates"].items():
                at = candidates[_key(name)].get_ase()
                r = relax(at, calc, fmax=float(rel.get("fmax", 1e-3)), cell=bool(rel.get("cell", True)))
                relaxed[name] = r.atoms.copy()
                relaxed[name].calc = None
                rows.append({"name": name, "x": float(x), "e": r.energy_per_atom, "V": r.volume_per_atom, "sg_before": r.spacegroup_before,
                             "sg_after": r.spacegroup_after, "converged": bool(r.converged), "transformed": bool(r.transformed)})
        df = pd.DataFrame(rows)
        hull = hull_0K(df["name"], df["x"], df["e"])
        cmp = compare_ground_states(hull, sp.get("known_ground_states", []))
        out["hull"] = orm.Dict(dict={"relaxed": rows, "hull": hull.to_dict("records"), "ground_state_check": cmp.to_dict("records"),
                                     "potential": potential.filename, "finished": time.strftime("%F %T")})
    xel = sp["x_element"]
    # ---- 02A solids
    solid_params = {}
    k = 0
    for s in sp["solids"]:
        base = relaxed[s["base"]].repeat(tuple(s.get("repeat", [1, 1, 1])))
        cells = []
        if s["kind"] == "point":
            cells.append((float(s["x"][0]) if s.get("x") else float(sp["candidates"][s["base"]]), 0, base.copy()))
        elif s.get("defects"):
            x0 = float(sp["candidates"][s["base"]])
            cells.append((x0, 0, base.copy()))
            for x, at, _label in _defect_cells(base, xel, s["defects"], seed=int(s.get("seed", 0))):
                cells.append((float(x), 0, at))
        elif s.get("antisites"):
            x0 = float(sp["candidates"][s["base"]])
            cells.append((x0, 0, base.copy()))
            for x, at in _antisite_cells(base, xel):
                cells.append((float(x), 0, at))
        elif s.get("series", "random") == "sqs":
            ic = s.get("icet", {})
            for x in s["x"]:
                if x <= 0.0:
                    cells.append((0.0, 0, base.copy())); continue
                n_b = int(round(x * len(base)))
                prim = relaxed[s["base"]]
                others = [e for e in sp["elements"] if e != xel]
                at, info = sqs_icet(prim, [[others[0], xel]] * len(prim), ic.get("cutoffs", [7.0, 4.5]), {others[0]: 1 - n_b / len(base), xel: n_b / len(base)},
                                    len(base), method="supercells", n_steps=ic.get("n_steps", 5000), seed=int(s.get("seed", 0)), supercells=[base.copy()])
                cells.append((n_b / len(base), 0, at))
        else:
            host_is_x = set(base.get_chemical_symbols()) == {xel}
            x_host = 1.0 if host_is_x else 0.0
            if any(abs(float(v) - x_host) < 1e-9 for v in s["x"]):
                cells.append((x_host, 0, base.copy()))
            for x_t, x_a, sd, at, _c in _series(base, xel, sp["elements"], [float(v) for v in s["x"]], int(s.get("seed", 0)), int(s.get("n_configs", 1))):
                cells.append((float(x_a), int(sd), at.copy()))
        for x, cfg, at in cells:
            key = f"s{k:02d}_{_key(s['phase'])}"
            at.calc = None
            solid_params[key] = {"phase": s["phase"], "kind": s["kind"], "x": float(x), "config": int(cfg), "n_atoms": len(at),
                                 "supercell": s.get("supercell", [1, 1, 1]), "mesh": s.get("mesh", 60.0),
                                 "counts": {e: at.get_chemical_symbols().count(e) for e in sorted(set(at.get_chemical_symbols()))}}
            out[f"solid_{key}"] = orm.StructureData(ase=at)
            k += 1
    out["solid_params"] = orm.Dict(dict=solid_params)
    # ---- 02B liquids
    lq = sp.get("liquids")
    liquid_params = {}
    if lq:
        base = relaxed[lq["base"]].repeat(tuple(lq.get("repeat", [4, 4, 4])))
        T0, T1 = [float(v) for v in lq.get("T_sweep", [1100.0, 700.0])]
        override = {float(a): float(b) for a, b in lq.get("T_override", {}).items()}
        xs = [float(v) for v in lq["x"]]
        members = []
        # optional second base for the x element's side, e.g. "base_hi": [0.5, "fcc-Ni"]: x > 0.5 from the Ni lattice
        split, base_hi = (lq["base_hi"][0], relaxed[lq["base_hi"][1]].repeat(tuple(lq.get("repeat", [4, 4, 4])))) if lq.get("base_hi") else (2.0, None)
        lo_x = [v for v in xs if v <= split]; hi_x = [v for v in xs if v > split]
        for b, group in ((base, lo_x), (base_hi, hi_x)):
            if not group:
                continue
            host_x = 1.0 if set(b.get_chemical_symbols()) == {xel} else 0.0
            if any(abs(v - host_x) < 1e-9 for v in group):
                members.append((host_x, host_x, 0, b.copy(), {e: b.get_chemical_symbols().count(e) for e in sp["elements"]}))
            for x_t, x_a, sd, at, counts in _series(b, xel, sp["elements"], group, int(lq.get("seed", 100)), 1):
                members.append((x_t, x_a, sd, at.copy(), counts))
        members.sort(key=lambda m: m[0])
        for rep in range(int(lq.get("n_repeats", 1))):
            for x_t, x_a, seed, at, counts in members:
                tag = f"lqd_x{x_t:.2f}" + (f"_r{rep}" if rep else "")
                key = _key(tag)
                t_stop = next((v for k2, v in override.items() if abs(k2 - x_t) < 1e-6), T1)
                at.calc = None
                liquid_params[key] = {"tag": tag, "x_target": float(x_t), "x_actual": float(x_a), "seed": int(seed), "repeat": rep, "counts": counts,
                                      "temperature": [T0, t_stop] if lq.get("mode", "ts") == "ts" else T0, "mode": lq.get("mode", "ts"),
                                      "n_atoms": len(at)}
                out[f"liquid_{key}"] = orm.StructureData(ase=at)
    out["liquid_params"] = orm.Dict(dict=liquid_params)
    return out


@calcfunction
def repeat_structure(structure: orm.StructureData, n: orm.Int):
    """n x n x n repetition of a cell (calphy TI needs >= ~200 atoms)."""
    at = structure.get_ase().repeat((int(n), int(n), int(n)))
    at.calc = None
    return orm.StructureData(ase=at)


def _lower_to_classical(T, G, hw, w, n_atoms):
    from ftphase.quantum import quantum_minus_classical

    T = np.asarray(T, dtype=float); G = np.asarray(G, dtype=float).copy()
    pos = T > 0
    G[pos] = G[pos] - quantum_minus_classical(hw, T[pos], weights=w, imaginary="drop") / int(n_atoms)
    return G


@calcfunction
def assemble_diagram(spec: orm.Dict, solid_params: orm.Dict, liquid_params: orm.Dict, **nodes):
    """Stages 04-07: one free-energy table, configurational terms, lower convex hull per T,
    invariants, Monte Carlo error bands, T-x figure, REPORT.md.

    ``nodes``: ``qha_<key>`` ArrayData from QhaCalculation (keys of solid_params),
    ``liq_<key>`` ArrayData (sweep) from CalphyCalculation (keys of liquid_params) and, optionally,
    ``sti_<key>`` ArrayData (sweep of a calphy solid ts run of the same cell, spec["solids_ti"]).
    Where a solid TI sweep exists its rows replace the QHA rows inside the sweep's temperature
    range (anharmonic level); QHA rows (lowered to the classical level) are kept below it.
    summary["qha_minus_ti_meV"] records the difference per cell at the sweep ends.

    spec["assemble"] keys: T_min, T_max, T_step, fits {phase: spline|poly|rk|smooth}, poly_orders,
    config_terms {phase: ideal | "sublattice:<site model>"}, entropy_models {phase: [site model,
    stoich_x]}, sigma {phase: eV/atom}, hull {min_width, gap_tol}, drop_edge_beyond_liquid (bool),
    sensitivity_samples, title, xlabel, liquid_sigma_floor (eV/atom).
    """
    import matplotlib

    matplotlib.use("Agg")
    from ftphase.assemble import add_configurational_term, builder_from_table, fit_residuals, interpolate_T
    from ftphase.diagram import invariants, plot_tx, scan, sensitivity, write_records

    sp = spec.get_dict(); asm = sp.get("assemble", {})
    sol_p = solid_params.get_dict(); liq_p = liquid_params.get_dict()
    model = sp.get("model", sp.get("pair_style", ""))
    summary = {"started": time.strftime("%F %T"), "solids_used": [], "solids_missing": [], "liquids_used": [], "liquids_missing": []}
    # ---- 03A -> 04B
    rows = []
    for key, meta in sol_p.items():
        node = nodes.get(f"qha_{key}")
        ti = nodes.get(f"sti_{key}")
        if node is None and ti is None:
            summary["solids_missing"].append(key); continue
        summary["solids_used"].append(key)
        if node is not None:
            T = node.get_array("T"); G = _lower_to_classical(T, node.get_array("G"), node.get_array("hw_eV"), node.get_array("weights"), meta["n_atoms"])
            V = node.get_array("V")
        else:
            T = G = V = np.array([])
            summary.setdefault("solids_ti_only", []).append(key)
        T_ti_lo = None
        if ti is not None:
            Tt, Gt, Et = ti.get_array("temperature"), ti.get_array("free_energy"), ti.get_array("error")
            T_ti_lo = float(Tt.min())
            summary.setdefault("solids_ti_used", []).append(key)
            if T.size:
                summary.setdefault("qha_minus_ti_meV", {})[key] = {f"{t:.0f}": float((np.interp(t, T, G) - np.interp(t, Tt, Gt)) * 1000) for t in (Tt.min(), 0.5 * (Tt.min() + Tt.max()), Tt.max()) if T.min() <= t <= T.max()}
            for t, g, e in zip(Tt, Gt, Et):
                rows.append({"phase": meta["phase"], "kind": meta["kind"], "x": meta["x"], "T": float(np.round(t, 3)), "P_GPa": float(asm.get("pressure_GPa", 0.0)), "G": float(g), "G_err": float(e),
                             "V": float(np.interp(t, T, V)) if T.size else np.nan,
                             "model": model, "reference_state": "absolute potential energy", "method": f"calphy ts solid (Frenkel-Ladd + reversible scaling), {sol_p[key]['n_atoms']}-atom cell repeated; config {meta['config']}",
                             "config_entropy": "none", "quantum": "classical", "n_atoms": meta["n_atoms"], "source": f"aiida calphy-solid {key}"})
        for t, g, v in zip(T, G, V):
            if T_ti_lo is not None and t >= T_ti_lo - 1e-6:
                continue
            rows.append({"phase": meta["phase"], "kind": meta["kind"], "x": meta["x"], "T": float(t), "P_GPa": float(asm.get("pressure_GPa", 0.0)), "G": float(g), "G_err": 0.0, "V": float(v),
                         "model": model, "reference_state": "absolute potential energy", "method": f"QHA phonopy sc={meta['supercell']} mesh={meta['mesh']}; lowered by F_q-F_cl (harmonic); config {meta['config']}",
                         "config_entropy": "none", "quantum": "classical+harmonic-correction", "n_atoms": meta["n_atoms"], "source": f"aiida qha {key}"})
    sol = pd.DataFrame(rows)
    agg = []
    if not sol.empty:
        for (ph, x, T), g in sol.groupby(["phase", "x", "T"]):
            r = g.iloc[0].to_dict()
            r["G"] = float(g["G"].mean()); r["G_err"] = max(float((g["G"].max() - g["G"].min()) / 2) if len(g) > 1 else 0.0, float(g["G_err"].max()))
            r["V"] = float(g["V"].mean()); r["source"] = f"aiida {'calphy-solid' if 'calphy' in r['method'] else 'qha'} {ph} x={x:.4f} ({len(g)} configs)"
            r["method"] = r["method"].split("; config")[0] + f"; mean of {len(g)} configurations"
            agg.append(r)
    sol = pd.DataFrame(agg)
    # ---- 03B liquids: average repeats per (x, T)
    lrows = []
    for key, meta in liq_p.items():
        node = nodes.get(f"liq_{key}")
        if node is None:
            summary["liquids_missing"].append(key); continue
        summary["liquids_used"].append(key)
        for t, g, e in zip(node.get_array("temperature"), node.get_array("free_energy"), node.get_array("error")):
            lrows.append({"x": float(meta["x_actual"]), "T": float(np.round(t, 3)), "G": float(g), "err": float(e), "key": key})
    if not lrows:
        raise ValueError("no finished liquid calculations: " + json.dumps(summary))
    ld = pd.DataFrame(lrows)
    floor = float(asm.get("liquid_sigma_floor", 0.0014))
    lagg = []
    for (x, T), g in ld.groupby(["x", "T"]):
        spread = float(g["G"].std(ddof=0)) if len(g) > 1 else 0.0
        lagg.append({"phase": "liquid", "kind": "solution", "x": x, "T": T, "P_GPa": float(asm.get("pressure_GPa", 0.0)), "G": float(g["G"].mean()),
                     "G_err": max(spread, float(g["err"].mean())), "V": np.nan, "model": model, "reference_state": "absolute potential energy",
                     "method": f"calphy reversible scaling, UFM reference; mean of {len(g)} runs", "config_entropy": "liquid-ti", "quantum": "classical",
                     "n_atoms": int(liq_p[g['key'].iloc[0]]["n_atoms"]), "source": "aiida calphy " + ",".join(sorted(set(g["key"])))})
    liq = pd.DataFrame(lagg)
    summary["liquid_x_available"] = sorted(float(v) for v in liq["x"].unique())
    summary["liquid_runs_per_x"] = {f"{x:.4f}": int(len(set(g["key"]))) for x, g in ld.groupby("x")}
    summary["liquid_T_min_K"] = {f"{x:.4f}": float(g["T"].min()) for x, g in ld.groupby("x")}
    # ---- 05 / 04A
    allrows = pd.concat([sol, liq], ignore_index=True)
    for ph, g in allrows.groupby("phase"):
        if g["kind"].iloc[0] != "point" and g["x"].nunique() < 2:
            allrows.loc[allrows.phase == ph, "kind"] = "point"
            summary.setdefault("degraded_to_point", []).append(ph)
    tab = FreeEnergyTable.from_rows(allrows.to_dict("records"), {"potential": model, "pressure_GPa": float(asm.get("pressure_GPa", 0.0)), "level": "classical"})
    phases = set(tab.df.phase)
    for ph, term in asm.get("config_terms", {}).items():
        if ph not in phases:
            continue
        if term == "ideal":
            tab = add_configurational_term(tab, ph, "ideal")
        elif term.startswith("sublattice:") and tab.df[tab.df.phase == ph]["x"].nunique() > 1:
            name, _, stoich = term[len("sublattice:"):].partition("@")
            tab = add_configurational_term(tab, ph, "sublattice", site_model=_site_model(name, float(stoich) if stoich else None))
    summary["table_check"] = [str(w) for w in tab.check()]
    T_diag = np.arange(float(asm.get("T_min", 700.0)), float(asm.get("T_max", 1100.0)) + 1e-6, float(asm.get("T_step", 10.0)))
    ti = interpolate_T(tab, T_diag)
    # keep only temperatures where every liquid composition has data
    cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"])
    if asm.get("liquid_partial", False):
        # liquids end at composition-dependent T_stop (Ni-Al): keep every T with >= 3 liquid compositions; segments
        # whose liquid end sits at the sampled liquid range edge (not 0 or 1) are removed after the scan
        ok_T = cover[cover["size"] >= 3].index
    else:
        ok_T = cover[(cover["min"] <= liq["x"].min() + 1e-6) & (cover["max"] >= liq["x"].max() - 1e-6) & (cover["size"] >= min(3, liq["x"].nunique()))].index
    ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(ok_T)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique()))
    summary["T_grid"] = [float(Ts.min()), float(Ts.max()), int(Ts.size)]
    def _sm(name):
        n, _, st = name.partition("@")
        return _site_model(n, float(st) if st else None)
    ent = {ph: (_sm(v[0]), float(v[1])) for ph, v in asm.get("entropy_models", {}).items() if ph in phases}
    hull_kw = asm.get("hull", {"min_width": 0.005, "gap_tol": 2.5})
    builder = builder_from_table(ti, fit=asm.get("fit", "spline"), fits=asm.get("fits", {}), poly_order=int(asm.get("poly_order", 3)),
                                 poly_orders=asm.get("poly_orders", {}), entropy_models=ent or None)
    T_res = float(Ts[np.argmin(np.abs(Ts - float(asm.get("T_residuals", 900.0))))])
    resid = fit_residuals(builder, T_res)
    reg = scan(builder, Ts, **hull_kw)
    x_liq_max = float(liq["x"].max())
    if asm.get("drop_edge_beyond_liquid", True) and x_liq_max < 1.0 - 1e-6:
        edge = reg["x_a"] >= x_liq_max - 1e-6
        summary["edge_segments_dropped"] = int(edge.sum())
        reg = reg[~edge].reset_index(drop=True)
    if asm.get("liquid_partial", False) and len(reg):
        lr = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max"])
        def _edge(r):
            if r["T"] not in lr.index:
                return False
            lo, hi = lr.loc[r["T"], "min"], lr.loc[r["T"], "max"]
            ends = [r["x_a"]] if r["phase_a"] == "liquid" else []
            ends += [r["x_b"]] if r["phase_b"] == "liquid" else []
            return any((abs(e - hi) < 1e-3 and hi < 1 - 1e-6) or (abs(e - lo) < 1e-3 and lo > 1e-6) for e in ends)
        edge = reg.apply(_edge, axis=1)
        summary["liquid_edge_segments_dropped"] = int(edge.sum())
        reg = reg[~edge].reset_index(drop=True)
    inv = invariants(reg)
    sig = {ph: float(asm.get("sigma", {}).get(ph, 0.002)) for ph in set(reg.phase_a) | set(reg.phase_b) | phases}
    sens = sensitivity(builder, Ts[::2], sig, n_samples=int(asm.get("sensitivity_samples", 30)), rng=0, **hull_kw)
    # ---- summary numbers
    liqreg = reg[(reg.phase_a == "liquid") | (reg.phase_b == "liquid")]
    if not liqreg.empty:
        Tm = float(liqreg["T"].min())
        summary["lowest_T_with_liquid_K"] = Tm
        summary["coexistence_at_that_T"] = liqreg[liqreg["T"] == Tm][["phase_a", "x_a", "phase_b", "x_b"]].to_dict("records")
    fl = reg[((reg.phase_a == "liquid") ^ (reg.phase_b == "liquid")) & ((reg.x_a < 0.02) | (reg.x_b < 0.02))]
    summary["pure_A_melting_bracket_K"] = [float(fl["T"].max()), float(fl["T"].max() + float(asm.get("T_step", 10.0)))] if not fl.empty else None
    summary["invariants"] = inv.to_dict("records")
    for T in (700, 800, 900, 1000):
        summary[f"regions_at_{T}K"] = reg[np.isclose(reg["T"], T)][["phase_a", "x_a", "phase_b", "x_b"]].to_dict("records")
    same = reg[reg.phase_a == reg.phase_b]
    summary["same_phase_segments"] = [{"phase": r.phase_a, "T": float(r.T), "x_a": float(r.x_a), "x_b": float(r.x_b)} for r in same.itertuples()]
    summary["fit_residuals"] = {"T": T_res, "rows": resid.to_dict("records")}
    summary["sigma_used_eV"] = sig
    summary["finished"] = time.strftime("%F %T")
    # ---- files
    out = {"summary": orm.Dict(dict=json.loads(json.dumps(summary, default=str)))}
    with tempfile.TemporaryDirectory() as d:
        tab.to_tsv(os.path.join(d, "05_free_energies.tsv"))
        resid.to_csv(os.path.join(d, "06_fit_residuals.tsv"), sep="\t", index=False)
        write_records(os.path.join(d, "07_two_phase_regions.tsv"), reg, {"workflow": "ftphase.txdiagram", "fits": str(asm.get("fits")), "hull": str(hull_kw),
                                                                          "T_step": float(asm.get("T_step", 10.0)), "level": "classical (QHA lowered by F_q-F_cl)"})
        inv.to_csv(os.path.join(d, "07_invariants.tsv"), sep="\t", index=False)
        sens.table.to_csv(os.path.join(d, "07_sensitivity.tsv"), sep="\t", index=False)
        ax = plot_tx(reg, xlabel=asm.get("xlabel", "x"), dT=float(asm.get("T_step", 10.0)))
        if x_liq_max < 1.0 - 1e-6:
            ax.set_xlim(0.0, x_liq_max + 0.05)
        ax.set_title(asm.get("title", "ftphase T-x diagram"), fontsize=9)
        ax.figure.savefig(os.path.join(d, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
        with open(os.path.join(d, "REPORT.md"), "w") as f:
            f.write(_report_text(sp, summary, reg, sens.table))
        for name, label in (("05_free_energies.tsv", "free_energies"), ("06_fit_residuals.tsv", "fit_residuals"), ("07_two_phase_regions.tsv", "regions"),
                            ("07_invariants.tsv", "invariants"), ("07_sensitivity.tsv", "sensitivity"), ("07_phase_diagram.png", "figure"), ("REPORT.md", "report")):
            out[label] = orm.SinglefileData(file=os.path.join(d, name))
    return out


def _report_text(sp, summary, reg, sens):
    asm = sp.get("assemble", {})
    L = [f"# {asm.get('title', 'ftphase T-x diagram')} (AiiDA workflow ftphase.txdiagram)", "",
         f"Assembled {summary['finished']}.  Classical level, {asm.get('pressure_GPa', 0.0)} GPa, model {sp.get('model', '')}.", "",
         "## Inputs", "", f"* solids (QHA, lowered to the classical level): {len(summary['solids_used'])} cells used, missing {summary['solids_missing']}",
         f"* liquids (calphy reversible scaling): {len(summary['liquids_used'])} runs used, missing {summary['liquids_missing']}; runs per x {summary.get('liquid_runs_per_x')}",
         f"* configurational terms: {asm.get('config_terms')}; fits: {asm.get('fits')} (poly = excess over analytic ideal mixing)",
         f"* temperature grid: {summary.get('T_grid')} (K, min, max, points); sigma (eV/atom): {summary.get('sigma_used_eV')}", "",
         "## Key numbers", ""]
    if "lowest_T_with_liquid_K" in summary:
        L.append(f"* lowest temperature with liquid on the grid: {summary['lowest_T_with_liquid_K']:.0f} K; coexistences: " +
                 "; ".join(f"{c['phase_a']}({c['x_a']:.3f}) + {c['phase_b']}({c['x_b']:.3f})" for c in summary["coexistence_at_that_T"]))
    if summary.get("pure_A_melting_bracket_K"):
        L.append(f"* pure-A melting bracket (x < 0.02): {summary['pure_A_melting_bracket_K'][0]:.0f}-{summary['pure_A_melting_bracket_K'][1]:.0f} K")
    L.append("* invariant reactions:")
    for r in summary.get("invariants", []):
        L.append(f"  * {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}")
    for T in (700, 800, 900, 1000):
        rr = summary.get(f"regions_at_{T}K", [])
        if rr:
            L.append(f"* two-phase regions at {T} K: " + "; ".join(f"{c['phase_a']}({c['x_a']:.3f})-{c['phase_b']}({c['x_b']:.3f})" for c in rr))
    same = reg[reg.phase_a == reg.phase_b]
    if not same.empty:
        L += ["", "## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)", ""]
        for (pa, lo, hi), g in same.groupby(["phase_a", same.x_a.round(2), same.x_b.round(2)]):
            L.append(f"* {pa}+{pa} x = {lo:.3f}-{hi:.3f} at T = {g['T'].min():.0f}-{g['T'].max():.0f} K ({len(g)} temperatures)")
    L += ["", "## Error bands (Monte Carlo over per-phase offsets)", ""]
    avail = np.unique(np.asarray(sens["T"], dtype=float)) if len(sens) else np.array([])
    for t in sorted({avail[np.argmin(np.abs(avail - t))] for t in (700.0, 800.0, 900.0)} if avail.size else []):
        for _, r in sens[np.isclose(sens["T"], t)].iterrows():
            L.append(f"* {t:.0f} K {r['pair']}: x_a = {r['x_a_mean']:.3f} +/- {r['x_a_std']:.3f}, x_b = {r['x_b_mean']:.3f} +/- {r['x_b_std']:.3f} ({int(r['n_found'])}/{int(r['n_samples'])} samples)")
    if summary.get("qha_minus_ti_meV"):
        L += ["", "## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)", ""]
        for key, d in summary["qha_minus_ti_meV"].items():
            L.append(f"* {key}: " + ", ".join(f"{t} K {v:+.1f}" for t, v in d.items()))
    L += ["", "## Caveats", "", f"* table check: {summary.get('table_check')}", f"* fit residuals at {summary['fit_residuals']['T']:.0f} K: {summary['fit_residuals']['rows']}",
          "* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.", ""]
    return "\n".join(L)
