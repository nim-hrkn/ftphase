"""Line compound or phase with a composition range?  Decide it without prior knowledge: give EVERY compound the same treatment
(four point defects in a ~100-site cell -> Wagner-Schottky G(x, T)), put all G(x) into the lower convex hull and read the width of
each compound from the hull.  ACE Al-Li, example-6 free energies (fcc, bcc, liquid as in extend_range.py); B32 is treated like the
other three (its 16-atom anti-site cells of example 6 are not used).
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/compound_width.py   -> out/5_compound_width.json / .md
"""
import json, os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram"); sys.path.insert(0, EX6); sys.path.insert(0, HERE)
KB = 8.617333262e-5
MODE = sys.argv[1] if len(sys.argv) > 1 else "free"     # free: defect free energies eps_d(T); static: 0 K defect energies


def b32_defects():
    from ftphase.validate import relax
    from pipeline import ace, b32_alli
    calc = ace(); base = relax(b32_alli(), calc, fmax=1e-3, cell=True).atoms; base.calc = None; sc = base.repeat((2, 2, 2)); sym = sc.get_chemical_symbols()
    e0 = relax(sc, calc, fmax=2e-3, cell=False).energy_per_atom * len(sc); iA = sym.index("Al"); iB = sym.index("Li"); out = {}
    for k, i, new in (("A_on_B", iB, "Al"), ("Va_on_B", iB, None), ("B_on_A", iA, "Li"), ("Va_on_A", iA, None)):
        at = sc.copy()
        if new: at[i].symbol = new
        else: del at[i]
        out[k] = round(float(relax(at, calc, fmax=2e-3, cell=False).energy_per_atom * len(at) - e0), 4)
    return {"sites": len(sc), "x0": 0.5, "defect_energies_raw_eV": out}


def main():
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table
    from ftphase.configurational import wagner_schottky_curve
    from ftphase.equilibrium import lower_hull_2d
    import extend_range as er
    C = json.load(open(os.path.join(OUT, "2_curvature.json"))); C["B32 (Fd-3m)"] = {"defect_energies_raw_eV": json.load(open(os.path.join(OUT, "5_compound_width.json")))["defect_energies_raw_eV"]["B32"]} if os.path.exists(os.path.join(OUT, "5_compound_width.json")) else b32_defects()
    WS = {"Al3Li": ("Al3Li (L1_2)", (3, 1)), "B32": ("B32 (Fd-3m)", (1, 1)), "Al2Li3": ("Al2Li3 (R-3m)", (2, 3)), "Al4Li9": ("Al4Li9 (C2/m)", (4, 9))}
    st = json.load(open(er.STAT)); new = pd.read_csv(er.TSV, sep="\t"); bad = {(v["phase"], v["x"]) for v in st.values() if v.get("ok") and (v["n_imag_modes"] > 0 or v["disp_max_A"] > 0.5)}
    new = new[[(p, x) not in bad for p, x in zip(new.phase, new.x)]]; tabn = FreeEnergyTable.from_rows(new.to_dict("records"), {})
    for ph in ("fcc", "bcc"):
        if (tabn.df.phase == ph).any() and tabn.df[tabn.df.phase == ph]["x"].nunique() > 1:
            tabn = add_configurational_term(tabn, ph, "ideal")
    old = FreeEnergyTable.from_tsv(os.path.join(EX6, "out_full", "05_free_energies.tsv")); df = pd.concat([old.df, tabn.df], ignore_index=True)
    b32pt = df[(df.phase == "B32") & np.isclose(df.x, 0.5)].copy(); df = pd.concat([df[df.phase != "B32"], b32pt], ignore_index=True)      # B32: only its stoichiometric cell, like the others
    tab = FreeEnergyTable.from_dataframe(df, old.meta); kw = dict(fit="spline", fits={"fcc": "poly", "bcc": "poly", "liquid": "rk"}, poly_order=3, poly_orders={"liquid": 4, "fcc": 4, "bcc": 4})
    res = {"defect_energies_raw_eV": {k: C[v[0]]["defect_energies_raw_eV"] for k, v in WS.items()}, "pair_energies_eV": {}, "T": {}}
    for k, (key, (a, b)) in WS.items():
        e = C[key]["defect_energies_raw_eV"]; g0 = 0.0     # composition-conserving complexes (vacancy complexes return the removed atoms to the perfect crystal: + n_atoms * E_atom, not needed for the antisite pair)
        res["pair_energies_eV"][k] = {"antisite_pair": round(e["A_on_B"] + e["B_on_A"], 3)}
    for T in (300.0, 400.0, 500.0, 600.0, 700.0, 800.0):
        ti = interpolate_T(tab, np.array([T])); ph = builder_from_table(ti, **kw)(T); pts, lab = [], []
        for p in ph:
            if hasattr(p, "x0"):
                key, sc = WS[p.name]; xw = np.linspace(p.x0 - 0.08, p.x0 + 0.08, 3201)
                DF = json.load(open(os.path.join(OUT, f"7_defectF_{p.name}.json")))["sizes"]; big = DF[str(max(int(q) for q in DF))]      # defect free energies eps_d(T) of the largest cell (defect_free_energy.py)
                eT = {k: float(np.interp(T, big["T"], big["defects"][v]["eps_T_eV"])) for k, v in {"A_on_B": "Al_on_Li", "B_on_A": "Li_on_Al", "Va_on_B": "Va_Li", "Va_on_A": "Va_Al"}.items()}
                gw = np.array(wagner_schottky_curve(xw, T, sc, eT if MODE == "free" else C[key]["defect_energies_raw_eV"], g0_atom=p.g0))     # true g0 (vacancies change the atom count)
                pts += list(zip(xw, gw)); lab += [p.name] * len(xw)
            else:
                xs = np.linspace(p.x_min, p.x_max, 4001); pts += list(zip(xs, p.g(xs))); lab += [p.name] * len(xs)
        pts = np.array(pts); idx = lower_hull_2d(pts); hx = pts[idx, 0]; hl = np.array(lab)[idx]; row = {}
        for k in WS:
            m = hl == k
            row[k] = None if not m.any() else {"x_min": round(float(hx[m].min()), 4), "x_max": round(float(hx[m].max()), 4), "width": round(float(hx[m].max() - hx[m].min()), 4)}
        res["T"][int(T)] = row; print(int(T), row, flush=True)
    json.dump(res, open(os.path.join(OUT, f"5_compound_width{'' if MODE == 'static' else '_free'}.json"), "w"), indent=1)
    x0 = {"Al3Li": 0.25, "B32": 0.5, "Al2Li3": 0.6, "Al4Li9": 9 / 13}
    L = ["# Width of each Al-Li compound from point defects + lower hull (ACE; no prior knowledge of which compound has a range)", "",
         "| compound | x0 | antisite pair (eV) | " + " | ".join(f"{T} K" for T in res["T"]) + " |", "|---|---|---|" + "---|" * len(res["T"])]
    for k in WS:
        L.append(f"| {k} | {x0[k]:.3f} | {res['pair_energies_eV'][k]['antisite_pair']:.2f} | " + " | ".join("not stable" if r[k] is None else f"{r[k]['x_min']:.3f}-{r[k]['x_max']:.3f} ({r[k]['width']:.3f})" for r in res["T"].values()) + " |")
    open(os.path.join(OUT, f"5_compound_width{'' if MODE == 'static' else '_free'}.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
