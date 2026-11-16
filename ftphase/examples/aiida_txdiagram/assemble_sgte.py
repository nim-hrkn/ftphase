"""Re-assemble an Al-Li txdiagram run with SGTE pure-element references (ftphase.assemble.reference_pure_elements).

    ./env/ftphase/bin/python ftphase/examples/aiida_txdiagram/assemble_sgte.py out/alli_ace_m6 [out/...]   -> <run>/sgte/

Per phase G += (1-x) d_Al + x d_Li with d_i = G_i^SGTE(lattice) - G_i^MLIP(lattice): fcc uses fcc Al of the run; the liquid uses
liquid Al of the run; Li has no pure-liquid run for x_Li <= 0.5, so the Li end of every phase uses the stable-element shift
(bcc Li, taken from the run's <run>_liside_solid table), i.e. the MLIP's bcc -> liquid difference of Li is kept.  The compounds
use the stable-element shifts.  SGTE values: ../calphad_user_needs/sgte_unary.json (sgte_unary.py, Dinsdale 1991).
Prints the Al melting bracket and the eutectic bracket before and after, and writes out/sgte_compare.tsv."""
import json, os, sys
import numpy as np
import pandas as pd


def main():
    import matplotlib; matplotlib.use("Agg")
    from aiida import load_profile, orm
    from ftphase.aiida.functions import _site_model
    from ftphase.assemble import builder_from_table, interpolate_T, add_configurational_term, reference_pure_elements
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable
    load_profile("ftphase"); here = os.path.dirname(os.path.abspath(__file__))
    U = json.load(open(os.path.join(here, "..", "calphad_user_needs", "sgte_unary.json"))); TU = np.array(U["T"])
    ref = {(i, lat): (lambda T, el=el, lat=lat: np.interp(T, TU, U[el][lat])) for i, el in ((0, "Al"), (1, "Li")) for lat in U[el]}
    rows = []
    for run in sys.argv[1:]:
        run = os.path.abspath(run); name = os.path.basename(run)
        asm = orm.load_node(json.load(open(run + ".pk.json"))["pk"]).inputs.spec.get_dict().get("assemble", {})
        tab = FreeEnergyTable.from_tsv(os.path.join(run, "05_free_energies.tsv")); df = tab.df.copy()
        for ph, term in (asm.get("config_terms") or {}).items():
            sub = df[df.phase == ph]
            if len(sub) and (sub.config_entropy == "none").any() and sub["x"].nunique() > 1:
                tmp = FreeEnergyTable.from_dataframe(df, tab.meta)
                if term == "ideal":
                    tmp = add_configurational_term(tmp, ph, "ideal")
                else:
                    n, _, st = term.partition("sublattice:")[2].partition("@"); tmp = add_configurational_term(tmp, ph, "sublattice", site_model=_site_model(n, float(st) if st else None))
                df = tmp.df
        tab = FreeEnergyTable.from_dataframe(df, tab.meta); phases = set(df.phase)
        Ts = np.arange(float(asm.get("T_min", 700.0)), float(asm.get("T_max", 1100.0)) + 1e-6, float(asm.get("T_step", 10.0))); ti = interpolate_T(tab, Ts)
        nl = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].nunique(); ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(nl[nl >= 3].index)], ti.meta)
        Tg = np.array(sorted(ti.df["T"].unique()))
        # Li end: no phase of an x_Li <= 0.5 run has its own pure-Li row, so every phase would get the same stable-element shift
        # x * d_Li, which cannot change the diagram (and the MLIP's bcc Li QHA stops near the Li melting point, far below 700 K).
        # It is therefore set to zero: model value := reference value.
        extra = {(1, "bcc"): (TU, np.interp(TU, TU, U["Li"]["bcc"]))}
        fa = ti.df[(ti.df.phase == "fcc") & (ti.df.x < 1e-6)]["T"]; la = ti.df[(ti.df.phase == "liquid") & (ti.df.x < 1e-6)]["T"]
        Tok = sorted(set(fa) & set(la)); ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(Tok)], ti.meta); Tg = np.array(Tok)   # both pure-Al rows needed
        kw = dict(fit=asm.get("fit", "spline"), fits={k: v for k, v in asm.get("fits", {}).items() if k in phases}, poly_order=int(asm.get("poly_order", 3)), poly_orders=asm.get("poly_orders", {}))
        hull = asm.get("hull", {"min_width": 0.005, "gap_tol": 2.5}); res = {"run": name}
        try:
            tr = reference_pure_elements(ti, ref, ser=("fcc", "bcc"), extra_pure=extra)
        except ValueError as e:
            print(name, "reference failed:", e); continue
        for tag, t in (("mlip", ti), ("sgte", tr)):
            reg = scan(builder_from_table(t, **kw), Tg, **hull); xl = float(t.df[t.df.phase == "liquid"]["x"].max())
            if asm.get("drop_edge_beyond_liquid", True) and xl < 1.0 - 1e-6:   # as in the WorkChain assembly
                reg = reg[~(reg["x_a"] >= xl - 1e-6)].reset_index(drop=True)
            r = reg[reg.phase_a != reg.phase_b]
            fl = r[(r.phase_a == "fcc") & (r.phase_b == "liquid")]; eu = r[(r.phase_a == "fcc") & (r.phase_b == "B32")]
            g = t.df[(t.df.x < 1e-6)]; dG = (g[g.phase == "liquid"].set_index("T")["G"] - g[g.phase == "fcc"].set_index("T")["G"]).dropna().sort_index()
            k = np.where(np.diff(np.sign(dG.to_numpy())))[0]
            res[f"Al_Tm_crossing_{tag}"] = round(float(dG.index[k[0]] - dG.iloc[k[0]] * (dG.index[k[0] + 1] - dG.index[k[0]]) / (dG.iloc[k[0] + 1] - dG.iloc[k[0]])), 1) if len(k) else ("> %.0f" % dG.index.max() if dG.iloc[-1] > 0 else "< %.0f" % dG.index.min())
            liq = r[(r.phase_a == "liquid") | (r.phase_b == "liquid")]
            res[f"T_grid_{tag}"] = f"{Tg.min():.0f}-{Tg.max():.0f}"
            res[f"eutectic_{tag}"] = f"{eu['T'].max():.0f}-{eu['T'].max() + 10:.0f}" if len(eu) else "none"
            res[f"lowest_liquid_{tag}"] = float(liq["T"].min()) if len(liq) else np.nan
            s8 = r[np.isclose(r["T"], 700.0) & (r.phase_a == "fcc") & (r.phase_b == "B32")]; res[f"solvus700_{tag}"] = round(float(s8.x_a.iloc[0]), 3) if len(s8) else np.nan
            if tag == "sgte":
                out = os.path.join(run, "sgte"); os.makedirs(out, exist_ok=True)
                write_records(os.path.join(out, "07_two_phase_regions.tsv"), reg, {"example": name + " with SGTE pure-element references", "lattices": str(tr.meta["pure_reference"])})
                invariants(reg).to_csv(os.path.join(out, "07_invariants.tsv"), sep="\t", index=False)
                ax = plot_tx(r, xlabel="x_Li", dT=10.0); ax.set_title(f"{name}: SGTE pure-element references", fontsize=8); ax.figure.savefig(os.path.join(out, "07_phase_diagram.png"), dpi=130, bbox_inches="tight")
        d = tr.df[(tr.df.phase == "fcc") & (tr.df.x < 1e-6)].set_index("T")["G"] - ti.df[(ti.df.phase == "fcc") & (ti.df.x < 1e-6)].set_index("T")["G"]
        l = tr.df[(tr.df.phase == "liquid") & (tr.df.x < 1e-6)].set_index("T")["G"] - ti.df[(ti.df.phase == "liquid") & (ti.df.x < 1e-6)].set_index("T")["G"]
        res["Al_liq_minus_fcc_shift_900K_meV"] = round(float((l - d).get(900.0, np.nan)) * 1000, 2)
        rows.append(res); print(json.dumps(res), flush=True)
    if rows:
        pd.DataFrame(rows).to_csv(os.path.join(here, "out", "sgte_compare.tsv"), sep="\t", index=False)


if __name__ == "__main__":
    main()
