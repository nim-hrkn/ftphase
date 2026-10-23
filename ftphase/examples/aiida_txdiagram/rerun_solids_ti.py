"""Ag-Cu (example 9): redo the solid calphy TI of the terminal fcc cells with 2048-atom cells (the 256-atom
Frenkel-Ladd cells are ~7 meV/atom too low, agcu_sgcmc/ti_convergence.py) and re-assemble.

    python rerun_solids_ti.py submit [--pk 428]     submit CalphyCalculation for every solid cell of the WorkChain
                                                    with x <= 0.3 or x >= 0.7, structure repeated to >= 2000 atoms
                                                    (records out/agcu_eam/solids_ti_2048.json)
    python rerun_solids_ti.py assemble              when all finished: assemble_diagram with the new sweeps (QHA and
                                                    liquid nodes of the original run) -> out/agcu_eam_2048/, then
                                                    reassemble_agcu.py --in out/agcu_eam_2048
"""

import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "agcu_eam")
REC = os.path.join(OUT, "solids_ti_2048.json")
MIN_ATOMS = 2000


def _workchain(pk):
    from aiida import orm

    wc = orm.load_node(pk)
    kids = {}
    for link in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all():
        kids.setdefault(link.node.process_label, []).append(link.node)
    prep = [n for n in kids.get("prepare_cells", []) if n.is_finished_ok][0]
    return wc, kids, prep


def submit(pk, only=None, t_hi=None):
    """only: comma-separated solid keys to (re)submit; t_hi: {key: T_hi} sweep-end overrides (e.g. cells that melted at the
    default 1.1 T_m cap: alloy cells inside the gap are metastable and melt well below the pure-end cap)."""
    from aiida import orm
    from aiida.engine import submit as aiida_submit
    from aiida.plugins import CalculationFactory

    from ftphase.aiida.functions import repeat_structure

    wc, kids, prep = _workchain(pk)
    sp = wc.inputs.spec.get_dict(); sti = sp["solids_ti"]
    sol_p = prep.outputs.solid_params.get_dict()
    extra = wc.inputs.calphy_extra.get_dict() if "calphy_extra" in wc.inputs else {}
    Calphy = CalculationFactory("ftphase.calphy")
    rec = json.load(open(REC)) if (only and os.path.exists(REC)) else {"pk_workchain": pk, "jobs": {}}
    t_hi = t_hi or {}
    for key, m in sol_p.items():
        if only and key not in only:
            continue
        if not only and 0.3 < m["x"] < 0.7:
            continue
        structure = prep.outputs[f"solid_{key}"]
        n_rep = max(1, int(np.ceil((MIN_ATOMS / m["n_atoms"]) ** (1 / 3) - 1e-9)))
        big = repeat_structure(structure, orm.Int(n_rep))
        T_sw = list(sti.get("T_sweep", [900.0, 1400.0]))
        pts = sorted(sti["T_hi_by_x"]); T_sw[1] = float(t_hi.get(key, np.interp(m["x"], [q[0] for q in pts], [q[1] for q in pts])))
        params = {"name": f"sol_{key}", "folder_prefix": f"sol_{key}", "mode": "ts", "elements": sp["elements"], "masses": sp["masses"], "pair_style": sp["pair_style"],
                  "pair_coeff": sp["pair_coeff"], "temperature": T_sw, "pressure": 0.0, "reference_phase": "solid", "n_equilibration_steps": int(sti.get("n_equilibration_steps", 10000)),
                  "n_switching_steps": sti.get("n_switching_steps", [10000, 10000]), "n_iterations": int(sti.get("n_iterations", 1))}
        params.update(extra)
        b = Calphy.get_builder()
        b.code = wc.inputs.calphy_code; b.structure = big; b.potential = wc.inputs.potential; b.parameters = orm.Dict(dict=params)
        b.metadata.options = wc.inputs.calphy_options.get_dict()
        b.metadata.label = f"calphy solid 2048 {key} x={m['x']:.4f} ({len(big.sites)} atoms)"
        node = aiida_submit(b)
        rec["jobs"][key] = {"pk": node.pk, "n_atoms": len(big.sites), "x": m["x"], "T_sweep": T_sw}
        print(key, node.pk, len(big.sites), "atoms", T_sw)
    os.makedirs(OUT, exist_ok=True)
    with open(REC, "w") as f:
        json.dump(rec, f, indent=1)
    print(f"{len(rec['jobs'])} solid TI jobs submitted; record {REC}")


def assemble():
    from aiida import orm

    from ftphase.aiida.functions import assemble_diagram

    rec = json.load(open(REC))
    wc, kids, prep = _workchain(rec["pk_workchain"])
    nodes = {}
    for n in kids.get("QhaCalculation", []):
        if n.is_finished_ok:
            key = n.label.split()[1]
            nodes[f"qha_{key}"] = n.outputs.arrays
    for n in kids.get("CalphyCalculation", []):
        if n.is_finished_ok and "sweep" in n.outputs and n.label.startswith("calphy lqd"):
            tag = n.label.split()[1]
            key = "".join(c if c.isalnum() else "_" for c in tag)
            nodes[f"liq_{key}"] = n.outputs.sweep
    missing = []
    for key, j in rec["jobs"].items():
        n = orm.load_node(j["pk"])
        if n.is_finished_ok and "sweep" in n.outputs:
            nodes[f"sti_{key}"] = n.outputs.sweep
        else:
            missing.append((key, j["pk"], n.process_state.value if n.process_state else None, n.exit_status))
    if missing:
        print("not finished / failed:", missing)
        if any(m[2] not in ("finished",) for m in missing):
            print("waiting for running jobs; run again later"); return
    res = assemble_diagram(wc.inputs.spec, prep.outputs.solid_params, prep.outputs.liquid_params, **nodes)
    out = os.path.join(HERE, "out", "agcu_eam_2048"); os.makedirs(out, exist_ok=True)
    for label, fn in (("report", "REPORT.md"), ("figure", "07_phase_diagram.png"), ("free_energies", "05_free_energies.tsv"), ("regions", "07_two_phase_regions.tsv"), ("invariants", "07_invariants.tsv"), ("sensitivity", "07_sensitivity.tsv")):
        with res[label].open(mode="rb") as f, open(os.path.join(out, fn), "wb") as g:
            g.write(f.read())
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(res["summary"].get_dict(), f, indent=1, default=str)
    print("assembled ->", out, "| qha", sum(k.startswith("qha_") for k in nodes), "liq", sum(k.startswith("liq_") for k in nodes), "sti", sum(k.startswith("sti_") for k in nodes))
    subprocess.run([sys.executable, os.path.join(HERE, "reassemble_agcu.py"), "--in", out])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["submit", "assemble"]); ap.add_argument("--pk", type=int, default=428)
    ap.add_argument("--profile", default="ftphase")
    ap.add_argument("--only", default=None, help="comma-separated solid keys, e.g. s07_fcc,s08_fcc (others keep their recorded jobs)")
    ap.add_argument("--T-hi", dest="t_hi", default=None, help="sweep-end overrides key=T,key=T")
    a = ap.parse_args()
    from aiida import load_profile

    load_profile(a.profile)
    only = set(a.only.split(",")) if a.only else None
    t_hi = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in a.t_hi.split(",")} if a.t_hi else None
    submit(a.pk, only, t_hi) if a.cmd == "submit" else assemble()
