"""Copy the outputs of a finished TxDiagramWorkChain to out/<name>/ and print the summary.

    env/ftphase/bin/python fetch_results.py <pk or name> [--profile ftphase]

Writes REPORT.md, 07_phase_diagram.png, 05_free_energies.tsv, 07_two_phase_regions.tsv,
07_invariants.tsv, 07_sensitivity.tsv, 06_fit_residuals.tsv, summary.json, hull.json,
solid_params.json, liquid_params.json and calcjobs.tsv (pk, label, state, exit status, remote dir).
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ident", help="pk, uuid or the name written by run_aiida.py (out/<name>.pk.json)")
    ap.add_argument("--profile", default=os.environ.get("AIIDA_PROFILE", "ftphase"))
    a = ap.parse_args()
    from aiida import load_profile, orm

    load_profile(a.profile)
    ident = a.ident
    rec = os.path.join(HERE, "out", f"{ident}.pk.json")
    if os.path.exists(rec):
        ident = json.load(open(rec))["pk"]
    node = orm.load_node(int(ident) if str(ident).isdigit() else ident)
    name = node.label.replace("ftphase txdiagram ", "") or f"pk{node.pk}"
    out = os.path.join(HERE, "out", name)
    os.makedirs(out, exist_ok=True)
    print(f"{node.process_label} pk={node.pk} state={node.process_state.value} exit={node.exit_status} label='{node.label}'")
    files = {"report": "REPORT.md", "figure": "07_phase_diagram.png", "free_energies": "05_free_energies.tsv", "regions": "07_two_phase_regions.tsv",
             "invariants": "07_invariants.tsv", "sensitivity": "07_sensitivity.tsv", "fit_residuals": "06_fit_residuals.tsv"}
    for key, fn in files.items():
        if key in node.outputs:
            with node.outputs[key].open(mode="rb") as f, open(os.path.join(out, fn), "wb") as g:
                g.write(f.read())
    for key in ("summary", "hull", "solid_params", "liquid_params"):
        if key in node.outputs:
            with open(os.path.join(out, f"{key}.json"), "w") as f:
                json.dump(node.outputs[key].get_dict(), f, indent=1, ensure_ascii=False, default=str)
    rows = ["pk\tlabel\tstate\texit\tremote_workdir"]
    for link in node.base.links.get_outgoing(node_class=orm.ProcessNode).all():
        c = link.node
        rows.append(f"{c.pk}\t{c.label}\t{c.process_state.value if c.process_state else ''}\t{c.exit_status}\t{c.get_remote_workdir() if isinstance(c, orm.CalcJobNode) else ''}")
    with open(os.path.join(out, "calcjobs.tsv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    print("\n".join(rows))
    if "summary" in node.outputs:
        s = node.outputs.summary.get_dict()
        print(json.dumps({k: s.get(k) for k in ("T_grid", "lowest_T_with_liquid_K", "coexistence_at_that_T", "pure_A_melting_bracket_K", "invariants", "solids_missing", "liquids_missing")}, indent=1, default=str))
    print(f"files in {out}")


if __name__ == "__main__":
    sys.exit(main())
