"""Solids-only re-assembly of an AiiDA txdiagram run below its liquid window, from its 05_free_energies.tsv and the WorkChain spec.

    ./env/ftphase/bin/python ftphase/examples/aiida_txdiagram/assemble_solids_lowT.py out/alli_mace_mpa_0 [out/...] [--T 300 700] [--step 10]

The WorkChain assembly keeps only grid temperatures covered by the liquid (Al-Li: 700-1100 K), although the QHA solids of the
same run go down to 0 K.  This script drops the liquid rows and scans the solid phases alone with the run's own fits,
configurational terms and entropy models (read from the WorkChain node's spec; generalisation of ptrh/assemble_lowT.py).
Classical level as in the WorkChain.  Output: <run>/lowT/07_two_phase_regions.tsv, 07_invariants.tsv, 07_phase_diagram.png,
REPORT.md, summary.json.  Solid-solid two-phase fields below the liquid window (fcc solvus, fcc+B32, Al3Li ...) only; the
noise caveats of the main assembly (same-phase segments, sample-edge boundaries) apply unchanged."""
import argparse
import json
import os

import numpy as np


def main():
    import matplotlib
    matplotlib.use("Agg")
    from aiida import load_profile, orm
    from ftphase.aiida.functions import _site_model
    from ftphase.assemble import builder_from_table, interpolate_T
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable

    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--T", nargs=2, type=float, default=[300.0, 700.0])
    ap.add_argument("--step", type=float, default=10.0)
    a = ap.parse_args()
    load_profile("ftphase")
    for run in a.runs:
        rec = json.load(open(os.path.abspath(run) + ".pk.json"))
        asm = orm.load_node(rec["pk"]).inputs.spec.get_dict().get("assemble", {})
        tab = FreeEnergyTable.from_tsv(os.path.join(run, "05_free_energies.tsv"))
        df = tab.df[tab.df.phase != "liquid"].copy()
        tab = FreeEnergyTable.from_dataframe(df, dict(tab.meta, stage="solids-only low-T re-assembly"))
        phases = set(tab.df.phase)
        Ts = np.arange(a.T[0], a.T[1] + 1e-6, a.step)
        ti = interpolate_T(tab, Ts)

        def _sm(name):
            n, _, st = name.partition("@")
            return _site_model(n, float(st) if st else None)
        ent = {ph: (_sm(v[0]), float(v[1])) for ph, v in asm.get("entropy_models", {}).items() if ph in phases}
        hull_kw = asm.get("hull", {"min_width": 0.005, "gap_tol": 2.5})
        builder = builder_from_table(ti, fit=asm.get("fit", "spline"), fits={k: v for k, v in asm.get("fits", {}).items() if k in phases},
                                     poly_order=int(asm.get("poly_order", 3)), poly_orders=asm.get("poly_orders", {}), entropy_models=ent or None)
        reg = scan(builder, Ts, **hull_kw)
        inv = invariants(reg)
        out = os.path.join(run, "lowT"); os.makedirs(out, exist_ok=True)
        write_records(os.path.join(out, "07_two_phase_regions.tsv"), reg, {"example": os.path.basename(os.path.abspath(run)) + " solids-only low-T re-assembly", "fits": str(asm.get("fits")), "hull": str(hull_kw), "T_step": a.step, "level": "classical"})
        inv.to_csv(os.path.join(out, "07_invariants.tsv"), sep="\t", index=False)
        ax = plot_tx(reg, xlabel=asm.get("xlabel", "x"), dT=a.step)
        ax.set_title(f"{tab.meta.get('potential', '')} solids only, {a.T[0]:.0f}-{a.T[1]:.0f} K (classical QHA, re-assembled)", fontsize=8)
        ax.figure.savefig(os.path.join(out, "07_phase_diagram.png"), dpi=130, bbox_inches="tight")
        same = reg[reg.phase_a == reg.phase_b]
        L = [f"# {os.path.basename(os.path.abspath(run))}: solids-only re-assembly {a.T[0]:.0f}-{a.T[1]:.0f} K", "",
             f"* phases {sorted(phases)}; fits {asm.get('fits')}; entropy models {asm.get('entropy_models')}; liquid rows dropped",
             f"* {len(reg)} two-phase rows, {len(same)} same-phase (fit-noise) rows", "", "## Invariant reactions", ""]
        L += [f"* {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}" for r in inv.to_dict("records")] or ["* none"]
        for T in (300.0, 400.0, 500.0, 600.0, 700.0):
            r = reg[np.isclose(reg["T"], T) & (reg.phase_a != reg.phase_b)]
            L.append(f"* two-phase regions at {T:.0f} K: " + ("; ".join(f"{c.phase_a}({c.x_a:.3f})-{c.phase_b}({c.x_b:.3f})" for c in r.itertuples()) or "none"))
        open(os.path.join(out, "REPORT.md"), "w").write("\n".join(L) + "\n")
        json.dump({"T_grid": [float(Ts.min()), float(Ts.max()), int(Ts.size)], "invariants": inv.to_dict("records")}, open(os.path.join(out, "summary.json"), "w"), indent=1, default=str)
        print(os.path.basename(run), "|", L[-5][:70], "|", L[-1][:90])


if __name__ == "__main__":
    main()
