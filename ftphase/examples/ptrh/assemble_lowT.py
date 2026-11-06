"""Solid-only re-assembly of a Pt-Rh AiiDA run over the ordering window (default 100-1900 K) from its 05_free_energies.tsv.

    ./env/ftphase/bin/python ftphase/examples/ptrh/assemble_lowT.py aiida_txdiagram/out/ptrh_grace_2l [--T 100 1900] [--step 10]

The WorkChain assembly keeps only temperatures with >= 3 liquid compositions (1910-2400 K here), so the 100-300 K
region where Saengdeejing et al. (2026) place the fcc <-> PtRh / PtRh3 / Pt3Rh ordering reactions is not scanned.
This script drops the liquid rows and scans the solid phases with the same fits, configurational terms and entropy
models as the WorkChain spec (fcc: ideal mixing + Redlich-Kister; ordered phases: two-sublattice anti-site entropy +
per-branch linear defect energy).  Classical level (QHA lowered by F_q - F_cl), as in the WorkChain.
Output: <run>/lowT/07_two_phase_regions.tsv, 07_invariants.tsv, 07_phase_diagram.png, REPORT.md."""

import argparse
import json
import os

import numpy as np
import pandas as pd

FITS = {"fcc": "rk", "PtRh": "poly", "PtRh3": "poly", "Pt3Rh": "poly"}
POLY = {"fcc": 4, "PtRh": 1, "PtRh3": 1, "Pt3Rh": 1}
CONFIG = {"fcc": "ideal", "PtRh": ("b32_antisite", None), "PtRh3": ("b32_antisite", 0.75), "Pt3Rh": ("b32_antisite", 0.25)}
ENTROPY = {"PtRh": ("b32_antisite", 0.5), "PtRh3": ("b32_antisite@0.75", 0.75), "Pt3Rh": ("b32_antisite@0.25", 0.25)}


def quantum_table(run):
    """FreeEnergyTable at the quantum harmonic level from the QHA nodes of the run's WorkChain (per-atom G from phonopy QHA)."""
    import pandas as pd
    from aiida import load_profile, orm

    from ftphase.records import FreeEnergyTable

    load_profile("ftphase")
    rec = json.load(open(os.path.abspath(run) + ".pk.json"))
    wc = orm.load_node(rec["pk"])
    sp = wc.inputs.spec.get_dict()
    prep = [l.node for l in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all() if l.node.process_label == "prepare_cells" and l.node.is_finished_ok][0]
    sol_p = prep.outputs.solid_params.get_dict()
    rows = []
    for l in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all():
        n = l.node
        if n.process_label != "QhaCalculation" or not n.is_finished_ok:
            continue
        key = n.label.split()[1]
        meta = sol_p[key]
        arr = n.outputs.arrays
        T, G, V = arr.get_array("T"), arr.get_array("G"), arr.get_array("V")
        for t, g, v in zip(T, G, V):
            rows.append({"phase": meta["phase"], "kind": meta["kind"], "x": meta["x"], "T": float(t), "P_GPa": 0.0, "G": float(g), "G_err": 0.0, "V": float(v),
                         "model": sp.get("model", ""), "reference_state": "absolute potential energy", "method": f"QHA phonopy (quantum harmonic); config {meta['config']}",
                         "config_entropy": "none", "quantum": "quantum-harmonic", "n_atoms": meta["n_atoms"], "source": f"aiida qha {key}"})
    sol = pd.DataFrame(rows)
    agg = []
    for (ph, x, T), g in sol.groupby(["phase", "x", "T"]):
        r = g.iloc[0].to_dict(); r["G"] = float(g["G"].mean()); r["G_err"] = float((g["G"].max() - g["G"].min()) / 2) if len(g) > 1 else 0.0; r["V"] = float(g["V"].mean())
        r["source"] = f"aiida qha {ph} x={x:.4f} ({len(g)} configs)"; agg.append(r)
    return FreeEnergyTable.from_rows(agg, {"potential": sp.get("model", ""), "pressure_GPa": 0.0, "level": "quantum-harmonic"})


def main():
    import matplotlib

    matplotlib.use("Agg")
    from ftphase.aiida.functions import _site_model
    from ftphase.assemble import add_configurational_term, builder_from_table, interpolate_T
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable

    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--T", nargs=2, type=float, default=[100.0, 1900.0])
    ap.add_argument("--step", type=float, default=10.0)
    ap.add_argument("--no-ordered", action="store_true", help="fcc only (reference: what the hull gives without the ordered phases)")
    ap.add_argument("--quantum", action="store_true", help="quantum (harmonic) level: take the QHA free energies straight from the AiiDA QHA nodes "
                    "instead of the classical-lowered 05 table (needs the profile; the WorkChain pk is read from <run>.pk.json)")
    a = ap.parse_args()
    out = os.path.join(a.run, "lowT_quantum" if a.quantum else "lowT")
    os.makedirs(out, exist_ok=True)
    if a.quantum:
        tab = quantum_table(a.run)
    else:
        tab = FreeEnergyTable.from_tsv(os.path.join(a.run, "05_free_energies.tsv"))
    df = tab.df[tab.df.phase != "liquid"].copy()
    if a.no_ordered:
        df = df[df.phase == "fcc"]
    tab = FreeEnergyTable.from_dataframe(df, dict(tab.meta, stage="ptrh low-T re-assembly (solids only)"))
    phases = set(tab.df.phase)
    # the WorkChain table already carries the configurational terms (config_entropy ideal / sublattice); add them only to rows that lack them
    for ph, term in CONFIG.items():
        if ph not in phases or (tab.df[tab.df.phase == ph].config_entropy != "none").all():
            continue
        if term == "ideal":
            tab = add_configurational_term(tab, ph, "ideal")
        elif tab.df[tab.df.phase == ph]["x"].nunique() > 1:
            name, st = term
            tab = add_configurational_term(tab, ph, "sublattice", site_model=_site_model(name, st))
    Ts = np.arange(a.T[0], a.T[1] + 1e-6, a.step)
    ti = interpolate_T(tab, Ts)
    ent = {ph: (_site_model(v[0].partition("@")[0], float(v[0].partition("@")[2]) if "@" in v[0] else None), v[1]) for ph, v in ENTROPY.items() if ph in phases}
    builder = builder_from_table(ti, fit="spline", fits={k: v for k, v in FITS.items() if k in phases}, poly_order=3, poly_orders=POLY, entropy_models=ent or None)
    reg = scan(builder, Ts, min_width=0.005, gap_tol=2.5)
    inv = invariants(reg)
    write_records(os.path.join(out, "07_two_phase_regions.tsv"), reg, {"example": os.path.basename(os.path.abspath(a.run)) + " low-T solids-only re-assembly", "fits": str(FITS), "T_step": a.step})
    inv.to_csv(os.path.join(out, "07_invariants.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Rh", dT=a.step)
    ax.set_title(f"{tab.meta.get('potential', '')} Pt-Rh, solids only, {a.T[0]:.0f}-{a.T[1]:.0f} K ({'quantum harmonic' if a.quantum else 'classical'} QHA, re-assembled)", fontsize=8)
    ax.figure.savefig(os.path.join(out, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
    # ordered-phase stability: highest T at which each ordered phase appears in a two-phase region
    top = {}
    for ph in ("PtRh", "PtRh3", "Pt3Rh"):
        r = reg[(reg.phase_a == ph) | (reg.phase_b == ph)]
        top[ph] = float(r["T"].max()) if len(r) else None
    L = [f"# {os.path.basename(os.path.abspath(a.run))}: low-T solids-only re-assembly ({a.T[0]:.0f}-{a.T[1]:.0f} K, {a.step:.0f} K)", "",
         ("Quantum (harmonic) level: QHA free energies as computed (zero-point + Bose-Einstein), no classical lowering." if a.quantum else "Classical level") + " Liquid rows dropped, same fits/entropy models as the WorkChain spec.", "",
         "## Highest temperature with the ordered phase in a two-phase region", ""]
    L += [f"* {ph}: {t if t is not None else 'never stable on the grid'}" for ph, t in top.items()]
    L += ["", "## Invariant reactions (pair-set changes)", ""] + [f"* {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}" for r in inv.to_dict("records")]
    same = reg[reg.phase_a == reg.phase_b]
    L += ["", "## Same-phase segments (fit noise)", ""] + ([f"* {r.phase_a}+{r.phase_a} x = {r.x_a:.3f}-{r.x_b:.3f} at {r.T:.0f} K" for r in same.itertuples()][:20] or ["* none"])
    for T in (150.0, 200.0, 300.0, 500.0, 1000.0):
        r = reg[np.isclose(reg["T"], T)]
        L.append(f"* two-phase regions at {T:.0f} K: " + ("; ".join(f"{c.phase_a}({c.x_a:.3f})-{c.phase_b}({c.x_b:.3f})" for c in r.itertuples()) or "none"))
    with open(os.path.join(out, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    json.dump({"T_grid": [float(Ts.min()), float(Ts.max()), int(Ts.size)], "ordered_top_T": top, "invariants": inv.to_dict("records")}, open(os.path.join(out, "summary.json"), "w"), indent=1, default=str)
    print("\n".join(L))


if __name__ == "__main__":
    main()
