"""Ni-Al / Ag-Cu MLIP runs (QHA solids, 2026-10-30): calphy solid TI (>= 2000-atom cells) of the melting-point cells,
because QHA puts the melting points of several MLIPs far off (GRACE-FS / SevenNet-0 fcc Al: S_solid > S_liquid at
1000 K).  Stage 1 (user decision 2026-10-31): only the pure / stoichiometric cells (fcc Al, fcc Ni, B2 NiAl, L1_2
Ni3Al; fcc Ag, fcc Cu), one CalphyCalculation each, on the calphy code of the original WorkChain.

    python mlip_solids_ti.py submit                 all six WorkChains (records out/<name>/solids_ti.json)
    python mlip_solids_ti.py submit --names nial_sevenn_0 --only s03_fccNi --T-hi s03_fccNi=1700
    python mlip_solids_ti.py status
    python mlip_solids_ti.py melt                   solid(TI)-liquid crossings -> out/mlip_compare_nial_agcu/melting_ti.tsv
    python mlip_solids_ti.py assemble [--names ..]  assemble_diagram with the TI sweeps -> out/<name>_ti/
"""

import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
MIN_ATOMS = 2000
RUNS = {"nial_grace_fs": 4784, "nial_grace_1l": 4798, "nial_sevenn_0": 4813, "agcu_grace_fs": 4869, "agcu_grace_1l": 4900, "agcu_sevenn_0": 4928}
#: (phase, x) -> sweep [T_lo, T_hi]; T_hi about 1.05 T_m(expt).  The first try with 1.2 T_m (pk 6503-6595) failed: GRACE-FS
#: fcc Al melted at ~1000 K on the way to 1150 K (MeltedError, pk 6503), so the MLIP melting points are near the experimental
#: ones and a superheated cell does not survive 1.2 T_m.  A crossing above T_hi is reported as "> T_hi" plus a linear extrapolation.
CELLS = {"nial": {("fccAl", 0.0): [600.0, 920.0], ("fccNi", 1.0): [1200.0, 1800.0], ("B2", 0.5): [1300.0, 2000.0], ("L12", 0.75): [1200.0, 1750.0]},
         "agcu": {("fcc", 0.0): [800.0, 1250.0], ("fcc", 1.0): [900.0, 1420.0]}}
EXPT = {("nial", "fccAl", 0.0): 933, ("nial", "fccNi", 1.0): 1728, ("nial", "B2", 0.5): 1911, ("nial", "L12", 0.75): 1645, ("agcu", "fcc", 0.0): 1235, ("agcu", "fcc", 1.0): 1358}


def _workchain(pk):
    from aiida import orm

    wc = orm.load_node(pk)
    kids = {}
    for link in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all():
        kids.setdefault(link.node.process_label, []).append(link.node)
    prep = [n for n in kids.get("prepare_cells", []) if n.is_finished_ok][0]
    return wc, kids, prep


def _rec_path(name):
    return os.path.join(OUT, name, "solids_ti.json")


def submit(names, only=None, t_hi=None):
    from aiida import orm
    from aiida.engine import submit as aiida_submit
    from aiida.plugins import CalculationFactory

    from ftphase.aiida.functions import repeat_structure

    Calphy = CalculationFactory("ftphase.calphy")
    for name in names:
        wc, kids, prep = _workchain(RUNS[name])
        sp = wc.inputs.spec.get_dict(); sol_p = prep.outputs.solid_params.get_dict()
        extra = wc.inputs.calphy_extra.get_dict() if "calphy_extra" in wc.inputs else {}
        rec = json.load(open(_rec_path(name))) if os.path.exists(_rec_path(name)) else {"pk_workchain": RUNS[name], "jobs": {}}
        done = set()
        for key, m in sorted(sol_p.items()):
            cell = next((c for c in CELLS[name[:4]] if c[0] == m["phase"] and abs(c[1] - m["x"]) < 1e-6), None)
            if cell is None or cell in done or (only and key not in only) or (not only and key in rec["jobs"]):
                continue
            done.add(cell)
            structure = prep.outputs[f"solid_{key}"]
            n_rep = max(1, int(np.ceil((MIN_ATOMS / m["n_atoms"]) ** (1 / 3) - 1e-9)))
            big = repeat_structure(structure, orm.Int(n_rep))
            T_sw = list(CELLS[name[:4]][cell]); T_sw[1] = float((t_hi or {}).get(key, T_sw[1]))
            params = {"name": f"sol_{key}", "folder_prefix": f"sol_{key}", "mode": "ts", "elements": sp["elements"], "masses": sp["masses"], "pair_style": sp["pair_style"],
                      "pair_coeff": sp["pair_coeff"], "temperature": T_sw, "pressure": 0.0, "reference_phase": "solid", "n_equilibration_steps": 10000,
                      "n_switching_steps": [10000, 10000], "n_iterations": 1}
            params.update(extra)
            b = Calphy.get_builder()
            b.code = wc.inputs.calphy_code; b.structure = big; b.potential = wc.inputs.potential; b.parameters = orm.Dict(dict=params)
            b.metadata.options = wc.inputs.calphy_options.get_dict()
            b.metadata.label = f"calphy solid ti {name} {key} {m['phase']} x={m['x']:.4f} ({len(big.sites)} atoms)"
            node = aiida_submit(b)
            rec["jobs"][key] = {"pk": node.pk, "phase": m["phase"], "x": m["x"], "n_atoms": len(big.sites), "T_sweep": T_sw}
            print(name, key, node.pk, len(big.sites), "atoms", T_sw, wc.inputs.calphy_code.full_label)
        with open(_rec_path(name), "w") as f:
            json.dump(rec, f, indent=1)


def status(names):
    from aiida import orm

    for name in names:
        if not os.path.exists(_rec_path(name)):
            continue
        for key, j in json.load(open(_rec_path(name)))["jobs"].items():
            n = orm.load_node(j["pk"])
            print(f"{name:15s} {key:11s} pk {j['pk']} {n.process_state.value if n.process_state else '?':9s} exit {n.exit_status} {n.ctime:%m-%d %H:%M} -> {n.mtime:%m-%d %H:%M}")


def melt(names):
    """Crossing of the TI solid sweep with the liquid sweep of the same composition (05 table of the original run)."""
    import pandas as pd
    from aiida import orm

    rows = []
    for name in names:
        if not os.path.exists(_rec_path(name)):
            continue
        t = pd.read_csv(os.path.join(OUT, name, "05_free_energies.tsv"), sep="\t")
        for key, j in json.load(open(_rec_path(name)))["jobs"].items():
            n = orm.load_node(j["pk"])
            liq = t[(t.phase == "liquid") & np.isclose(t.x, j["x"], atol=2e-3)].groupby("T")["G"].mean()
            qha = t[(t.phase == j["phase"]) & np.isclose(t.x, j["x"])].groupby("T")["G"].mean()
            r = {"run": name, "cell": key, "phase": j["phase"], "x": j["x"], "T_expt": EXPT.get((name[:4], j["phase"], j["x"])), "state": n.process_state.value, "exit": n.exit_status}
            if n.is_finished_ok and "sweep" in n.outputs and len(liq) > 1:
                Ts, Gs = n.outputs.sweep.get_array("temperature"), n.outputs.sweep.get_array("free_energy")
                lo, hi = max(Ts.min(), liq.index.min()), min(Ts.max(), liq.index.max())
                grid = np.linspace(lo, hi, 400) if hi > lo else np.array([])
                d = np.interp(grid, liq.index, liq.values) - np.interp(grid, Ts, Gs) if grid.size else np.array([])
                s = np.where(np.diff(np.sign(d)) != 0)[0]
                r["T_m_ti"] = f"{grid[s[0]]:.0f}" if s.size else ("> %.0f" % hi if d.size and d[-1] > 0 else "< %.0f" % lo if d.size else "no overlap")
                if not s.size and d.size > 20:   # linear extrapolation of dG = G_liq - G_sol from the last/first 20 % of the overlap
                    k = max(5, d.size // 5); sl = slice(-k, None) if d[-1] > 0 else slice(0, k)
                    c = np.polyfit(grid[sl], d[sl], 1); r["T_m_extrap"] = round(float(-c[1] / c[0])) if c[0] != 0 else None
                tm = 0.5 * (Ts.min() + Ts.max())
                r["qha_minus_ti_meV@%s" % "mid"] = round(float((np.interp(tm, qha.index, qha.values) - np.interp(tm, Ts, Gs)) * 1000), 1) if len(qha) else None
                r["T_mid"] = round(float(tm))
            rows.append(r)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(OUT, "mlip_compare_nial_agcu"), exist_ok=True)
    df.to_csv(os.path.join(OUT, "mlip_compare_nial_agcu", "melting_ti.tsv"), sep="\t", index=False)
    print(df.to_string(index=False))


def assemble(names):
    from aiida import orm

    from ftphase.aiida.functions import assemble_diagram

    for name in names:
        rec = json.load(open(_rec_path(name)))
        wc, kids, prep = _workchain(rec["pk_workchain"])
        nodes = {}
        for n in kids.get("QhaCalculation", []):
            if n.is_finished_ok:
                nodes[f"qha_{n.label.split()[1]}"] = n.outputs.arrays
        for n in kids.get("CalphyCalculation", []):
            if n.is_finished_ok and "sweep" in n.outputs and n.label.startswith("calphy lqd"):
                nodes[f"liq_{''.join(c if c.isalnum() else '_' for c in n.label.split()[1])}"] = n.outputs.sweep
        for key, j in rec["jobs"].items():
            n = orm.load_node(j["pk"])
            if n.is_finished_ok and "sweep" in n.outputs:
                nodes[f"sti_{key}"] = n.outputs.sweep
        res = assemble_diagram(wc.inputs.spec, prep.outputs.solid_params, prep.outputs.liquid_params, **nodes)
        out = os.path.join(OUT, name + "_ti"); os.makedirs(out, exist_ok=True)
        for label, fn in (("report", "REPORT.md"), ("figure", "07_phase_diagram.png"), ("free_energies", "05_free_energies.tsv"), ("regions", "07_two_phase_regions.tsv"), ("invariants", "07_invariants.tsv")):
            with res[label].open(mode="rb") as f, open(os.path.join(out, fn), "wb") as g:
                g.write(f.read())
        with open(os.path.join(out, "summary.json"), "w") as f:
            json.dump(res["summary"].get_dict(), f, indent=1, default=str)
        print(name, "->", out, "| sti", sum(k.startswith("sti_") for k in nodes))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["submit", "status", "melt", "assemble"])
    ap.add_argument("--names", default=",".join(RUNS)); ap.add_argument("--profile", default="ftphase")
    ap.add_argument("--only", default=None, help="comma-separated solid keys to (re)submit")
    ap.add_argument("--T-hi", dest="t_hi", default=None, help="sweep-end overrides key=T,key=T")
    a = ap.parse_args()
    from aiida import load_profile

    load_profile(a.profile)
    names = a.names.split(",")
    only = set(a.only.split(",")) if a.only else None
    t_hi = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in a.t_hi.split(",")} if a.t_hi else None
    {"submit": lambda: submit(names, only, t_hi), "status": lambda: status(names), "melt": lambda: melt(names), "assemble": lambda: assemble(names)}[a.cmd]()
