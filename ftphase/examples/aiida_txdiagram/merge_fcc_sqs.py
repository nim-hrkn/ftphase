"""Re-assemble an Al-Li run with the fcc solid solution from 64-atom SQS cells (the *_fccsqs_solid WorkChain) and its own liquids.

    ./env/ftphase/bin/python ftphase/examples/aiida_txdiagram/merge_fcc_sqs.py out/alli_ace_m6 [out/...]     -> out/<run>_sqs/ (+ lowT/)

The 13-MLIP comparison used two 32-atom random fcc cells per composition; their configuration noise makes an apparent fcc+fcc
region (x = 0.03-0.12) and shifts the fcc solvus.  `run_aiida.py --fcc-sqs --solid-only` recomputed the solids with one 64-atom icet
SQS per fcc composition (plus B32 and Al3Li, same settings as before).  This takes the liquid rows of the original run and all
solid rows of the SQS run, applies the run's configurational terms and fits, and writes the liquid-window assembly (700-1100 K) and
the solids-only assembly below it (300-690 K) in the layout the figure scripts read.  Prints the fcc solvus and the number of
same-phase (fcc+fcc) rows before and after; out/fcc_sqs_compare.tsv."""
import json, os, shutil, sys
import numpy as np
import pandas as pd


def main():
    import matplotlib; matplotlib.use("Agg")
    from aiida import load_profile, orm
    from ftphase.aiida.functions import _site_model
    from ftphase.assemble import builder_from_table, interpolate_T, add_configurational_term
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable
    load_profile("ftphase"); here = os.path.dirname(os.path.abspath(__file__)); rows = []
    for run in sys.argv[1:]:
        run = os.path.abspath(run); name = os.path.basename(run); base = run[:-3] if run.endswith("_m6") else run; sq = base + "_fccsqs_solid"
        if not os.path.exists(os.path.join(sq, "05_free_energies.tsv")):
            print(name, "no SQS run yet -> skipped"); continue
        asm = orm.load_node(json.load(open(run + ".pk.json"))["pk"]).inputs.spec.get_dict().get("assemble", {})
        old = FreeEnergyTable.from_tsv(os.path.join(run, "05_free_energies.tsv")); new = FreeEnergyTable.from_tsv(os.path.join(sq, "05_free_energies.tsv"))
        df = pd.concat([new.df[new.df.phase != "liquid"], old.df[old.df.phase == "liquid"]], ignore_index=True)

        def with_terms(d):
            for ph, term in (asm.get("config_terms") or {}).items():
                sub = d[d.phase == ph]
                if len(sub) and (sub.config_entropy == "none").any() and sub["x"].nunique() > 1:
                    tmp = FreeEnergyTable.from_dataframe(d, old.meta)
                    if term == "ideal":
                        tmp = add_configurational_term(tmp, ph, "ideal")
                    else:
                        n, _, st = term.partition("sublattice:")[2].partition("@"); tmp = add_configurational_term(tmp, ph, "sublattice", site_model=_site_model(n, float(st) if st else None))
                    d = tmp.df
            return d
        out = run + "_sqs"; os.makedirs(os.path.join(out, "lowT"), exist_ok=True); shutil.copy(run + ".pk.json", out + ".pk.json")
        tab = FreeEnergyTable.from_dataframe(with_terms(df), dict(old.meta, solids="fcc from 64-atom SQS (" + os.path.basename(sq) + ")")); tab.to_tsv(os.path.join(out, "05_free_energies.tsv"))
        tab0 = FreeEnergyTable.from_dataframe(with_terms(old.df.copy()), old.meta); phases = set(tab.df.phase)
        kw = dict(fit=asm.get("fit", "spline"), fits={k: v for k, v in asm.get("fits", {}).items() if k in phases}, poly_order=int(asm.get("poly_order", 3)), poly_orders=asm.get("poly_orders", {}))
        hull = asm.get("hull", {"min_width": 0.005, "gap_tol": 2.5}); res = {"run": name}
        for tag, t in (("random32", tab0), ("sqs64", tab)):
            for part, Ts, liq in (("high", np.arange(float(asm.get("T_min", 700.0)), float(asm.get("T_max", 1100.0)) + 1e-6, 10.0), True), ("low", np.arange(300.0, float(asm.get("T_min", 700.0)) - 1e-6, 10.0), False)):
                d = t.df if liq else t.df[t.df.phase != "liquid"]; ti = interpolate_T(FreeEnergyTable.from_dataframe(d, t.meta), Ts)
                if liq:
                    nl = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].nunique(); ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(nl[nl >= 3].index)], ti.meta)
                Tg = np.array(sorted(ti.df["T"].unique())); reg = scan(builder_from_table(ti, **{**kw, "fits": {k: v for k, v in kw["fits"].items() if k in set(ti.df.phase)}}), Tg, **hull)
                if liq and asm.get("drop_edge_beyond_liquid", True):      # as in the WorkChain assembly: no segment that starts at the liquid's composition edge
                    xl = float(d[d.phase == "liquid"]["x"].max())
                    if xl < 1.0 - 1e-6:
                        reg = reg[~(reg["x_a"] >= xl - 1e-6)].reset_index(drop=True)
                r = reg[reg.phase_a != reg.phase_b]
                same = reg[(reg.phase_a == "fcc") & (reg.phase_b == "fcc")]; res[f"fccfcc_rows_{part}_{tag}"] = int(len(same))
                for T in ((700.0, 760.0) if liq else (500.0, 650.0)):
                    s = r[np.isclose(r["T"], T) & (r.phase_a == "fcc") & (r.phase_b.isin(["B32", "Al3Li"]))]; res[f"solvus{int(T)}_{tag}"] = round(float(s.x_a.max()), 3) if len(s) else np.nan
                if liq:
                    eu = r[(r.phase_a == "fcc") & (r.phase_b == "B32")]; res[f"eutectic_{tag}"] = f"{eu['T'].max():.0f}-{eu['T'].max() + 10:.0f}" if len(eu) else "none"
                    g = ti.df[ti.df.x < 1e-6]; dG = (g[g.phase == "liquid"].set_index("T")["G"] - g[g.phase == "fcc"].groupby("T")["G"].mean()).dropna().sort_index(); k = np.where(np.diff(np.sign(dG.to_numpy())))[0]
                    res[f"Al_Tm_{tag}"] = round(float(dG.index[k[0]] - dG.iloc[k[0]] * (dG.index[k[0] + 1] - dG.index[k[0]]) / (dG.iloc[k[0] + 1] - dG.iloc[k[0]])), 1) if len(k) else np.nan
                if tag == "sqs64":
                    o = out if liq else os.path.join(out, "lowT")
                    write_records(os.path.join(o, "07_two_phase_regions.tsv"), reg, {"example": name + " with fcc from 64-atom SQS", "part": part, "fits": str(kw["fits"]), "hull": str(hull)})
                    invariants(reg).to_csv(os.path.join(o, "07_invariants.tsv"), sep="\t", index=False)
                    ax = plot_tx(r, xlabel="x_Li", dT=10.0); ax.set_title(f"{name}: fcc from 64-atom SQS ({part})", fontsize=8); ax.figure.savefig(os.path.join(o, "07_phase_diagram.png"), dpi=130, bbox_inches="tight")
        rows.append(res); print(json.dumps(res), flush=True)
    if rows:
        pd.DataFrame(rows).to_csv(os.path.join(here, "out", "fcc_sqs_compare.tsv"), sep="\t", index=False)


if __name__ == "__main__":
    main()
