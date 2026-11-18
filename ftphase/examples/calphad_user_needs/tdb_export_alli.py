"""TDB of ACE Al-Li written from the free-energy table by ftphase.tdb (2026-11-19), and its check with pycalphad.
Solutions fcc / bcc / liquid: Redlich-Kister fitted to the table (fcc Li and bcc Al ends are not in the table of example 6 + the
full-range cells that survived: their lattice stabilities are fitted); the four compounds as two-sublattice phases whose
end-members come from the anti-site free energies (kind 'cef'), written as formation quantities relative to fcc Al and bcc Li.
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/tdb_export_alli.py [stoichiometric|cef]  -> out/10_alli_ace_<kind>.tdb, .json, .md
"""
import json, os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram"); sys.path.insert(0, EX6); sys.path.insert(0, HERE)
KIND = sys.argv[1] if len(sys.argv) > 1 else "cef"
WS = {"Al3Li": ("AL3LI", (3, 1)), "B32": ("B32", (1, 1)), "Al2Li3": ("AL2LI3", (2, 3)), "Al4Li9": ("AL4LI9", (4, 9))}
MAP = {"A_on_B": "Al_on_Li", "B_on_A": "Li_on_Al", "Va_on_B": "Va_Li", "Va_on_A": "Va_Al"}


def main():
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import add_configurational_term, interpolate_T, check_with_pycalphad
    from ftphase.compounds import CompoundModel
    from ftphase.tdb import write_tdb
    import extend_range as er
    st = json.load(open(er.STAT)); new = pd.read_csv(er.TSV, sep="\t"); bad = {(v["phase"], v["x"]) for v in st.values() if v.get("ok") and (v["n_imag_modes"] > 0 or v["disp_max_A"] > 0.5)}
    new = new[[(p, x) not in bad for p, x in zip(new.phase, new.x)]]; tabn = FreeEnergyTable.from_rows(new.to_dict("records"), {})
    for ph in ("fcc", "bcc"):
        if (tabn.df.phase == ph).any() and tabn.df[tabn.df.phase == ph]["x"].nunique() > 1:
            tabn = add_configurational_term(tabn, ph, "ideal")
    old = FreeEnergyTable.from_tsv(os.path.join(EX6, "out_full", "05_free_energies.tsv")); df = pd.concat([old.df, tabn.df], ignore_index=True)
    df = pd.concat([df[df.phase != "B32"], df[(df.phase == "B32") & np.isclose(df.x, 0.5)]], ignore_index=True)
    Ts = np.arange(660.0, 1000.1, 20.0); ti = interpolate_T(FreeEnergyTable.from_dataframe(df, old.meta), Ts)
    models = {}
    for k, (_, sc) in WS.items():
        d = json.load(open(os.path.join(OUT, f"7_defectF_{k}.json")))["sizes"]; big = d[str(max(int(q) for q in d))]
        models[k] = CompoundModel(k, sc[1] / (sc[0] + sc[1]), sc, big["T"], {a: big["defects"][b]["eps_T_eV"] for a, b in MAP.items()})
    path = os.path.join(OUT, f"10_alli_ace_{KIND}.tdb")
    text, rep = write_tdb(ti, ("Al", "Li"), {"fcc": "FCC_A1", "bcc": "BCC_A2", "liquid": "LIQUID"}, {k: {"name": v[0], "site_counts": v[1], "kind": KIND} for k, v in WS.items()},
                          T_fit=(660.0, 1000.0), terms=3, rk_order=3, compound_terms=2, models=models, reference=("fcc", "bcc"), path=path, comment=f"ACE Al-Li, example 6 + full-range fcc/bcc, compounds {KIND}")
    json.dump(rep, open(path.replace(".tdb", ".json"), "w"), indent=1)
    L = [f"# TDB of ACE Al-Li from the free-energy table (compounds: {KIND})", "", "## Loss against the table (rms of the fits, meV/atom)", ""]
    L += [f"* {ph} -> {r['tdb']}: RK order {r['rk_order']}, rms {r['rms_meV']:.2f} over x = {r['x_range'][0]:.3f}-{r['x_range'][1]:.3f}" + (f"; pure {r['ends_not_computed']} not computed: kept above the hull of the table + 20 meV/atom outside the sampled range" if r["ends_not_computed"] else "") for ph, r in rep["solutions"].items()]
    L += [f"* {ph} -> {r['tdb']}: dH_f {r['dH_f_J'] / 1000:.2f} kJ/mol, dS_f {r['dS_f_J_K']:.2f} J/mol/K (vs fcc Al, bcc Li), rms {r['rms_meV']:.2f}" for ph, r in rep["compounds"].items()]
    # ---- check with pycalphad against the hull of the same free energies (uniform_diagram.py noninteracting)
    chk = check_with_pycalphad(path, ("Al", "Li"), [700.0, 800.0, 900.0], x_grid=np.linspace(0.01, 0.99, 99)); chk.to_csv(path.replace(".tdb", "_pycalphad.tsv"), sep="\t", index=False)
    hull = pd.read_csv(os.path.join(OUT, "8_uniform_two_phase_regions.tsv"), sep="\t", comment="#"); REN = {"FCC_A1": "fcc", "BCC_A2": "bcc", "LIQUID": "liquid", "AL3LI": "Al3Li", "AL2LI3": "Al2Li3", "AL4LI9": "Al4Li9", "B32": "B32"}
    L += ["", "## pycalphad on the TDB against the hull of the table (two-phase boundaries, x_Li)", "", "| T (K) | two-phase region | hull (table) | pycalphad (TDB) |", "|---|---|---|---|"]
    for T in (700.0, 800.0, 900.0):
        g = chk[np.isclose(chk["T"], T)]; reg = {}
        for r in g.itertuples():
            ph = "+".join(sorted(REN.get(p, p) for p in r.phases.split("+")))
            if "+" in ph:
                reg.setdefault(ph, []).append(r.x)
        h = hull[np.isclose(hull["T"], T)]; hh = {"+".join(sorted((c.phase_a, c.phase_b))): (c.x_a, c.x_b) for c in h.itertuples()}
        for key in sorted(set(reg) | set(hh)):
            L.append(f"| {T:.0f} | {key} | " + (f"{hh[key][0]:.3f}–{hh[key][1]:.3f}" if key in hh else "—") + " | " + (f"{min(reg[key]):.2f}–{max(reg[key]):.2f}" if key in reg else "—") + " |")
    open(path.replace(".tdb", ".md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
