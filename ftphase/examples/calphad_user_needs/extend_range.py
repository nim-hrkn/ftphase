"""G(x, T) of fcc and bcc over the WHOLE composition range for ACE Al-Li (item 1: metastable phases over a wide range).

Example 6 sampled fcc only for x_Li <= 0.25 and bcc only for x_Li >= 0.75.  This adds one 64-atom icet SQS per composition for
fcc at x = 0.375 ... 1 and bcc at x = 0 ... 0.625 (same settings as example 6: hydrostatic relaxation, QHA with a 2x2x2 phonon
supercell, mesh 60 A, quantum QHA lowered to the classical level, ideal mixing added) and records how stable each cell is
(displacement from the ideal lattice sites after relaxation, imaginary modes dropped).  Mechanically unstable cells (bcc Al-rich)
are kept in the table but flagged: their G is not a thermodynamic quantity.
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/extend_range.py run      (about an hour, ACE on the CPUs; resumable)
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/extend_range.py report   -> out/1_full_range.png, out/1_full_range.json
"""
import json, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram")
sys.path.insert(0, EX6)
NEW = {"fcc": [0.375, 0.5, 0.625, 0.75, 0.875, 1.0], "bcc": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625]}
TSV = os.path.join(OUT, "1_ext_solids.tsv"); STAT = os.path.join(OUT, "1_ext_status.json")


def run():
    from ase.build import bulk
    from ftphase.validate import relax
    from ftphase.qha import phonopy_volume_scan
    from ftphase.quantum import quantum_minus_classical
    from pipeline import ace, T_QHA, MODEL
    from pipeline_full import _sqs, SC_FCC, SC_BCC, MESH_LENGTH
    calc = ace(); os.makedirs(OUT, exist_ok=True)
    status = json.load(open(STAT)) if os.path.exists(STAT) else {}; rows = pd.read_csv(TSV, sep="\t").to_dict("records") if os.path.exists(TSV) else []
    prims = {"fcc": relax(bulk("Al", "fcc", a=4.05), calc, fmax=1e-3, cell=True, hydrostatic=True).atoms, "bcc": relax(bulk("Li", "bcc", a=3.49), calc, fmax=1e-3, cell=True, hydrostatic=True).atoms}
    for ph, xs in NEW.items():
        prim = prims[ph]; prim.calc = None; scales = SC_FCC if ph == "fcc" else SC_BCC
        for i, x in enumerate(xs):
            key = f"{ph}_{x:.4f}"
            scales = SC_BCC if (ph == "bcc" or x > 0.7) else SC_FCC      # Li-rich cells expand far more with temperature: the fcc scan (up to +5 %) left the EOS minimum outside
            if status.get(key, {}).get("ok"):
                continue
            t0 = time.time()
            try:
                if x in (0.0, 1.0):
                    at = prim.repeat((4, 4, 4)); at.set_chemical_symbols(["Al" if x == 0.0 else "Li"] * len(at)); dev = 0.0
                else:
                    at, meta = _sqs(prim, {"Al": 1 - x, "Li": x}, seed=40 + i + (0 if ph == "fcc" else 20)); dev = float(meta["cluster_vector_deviation"])
                ideal = at.get_scaled_positions().copy()
                r = relax(at, calc, fmax=1e-3, cell=True, hydrostatic=True); a0 = r.atoms.copy(); a0.calc = None
                d = a0.get_scaled_positions() - ideal; d -= np.round(d); disp = np.linalg.norm(d @ a0.cell[:], axis=1)
                res, data = phonopy_volume_scan(a0, calc, np.diag([2, 2, 2]), T_QHA, scales=tuple(scales), mesh=MESH_LENGTH, imaginary="drop", eos="vinet")
                G, V = res.per_atom(); i1 = int(np.argmin(np.abs(np.asarray(scales) - 1.0))); hw, w = data["frequencies"][i1]
                T = np.asarray(T_QHA, dtype=float); dF = np.zeros(len(T)); pos = T > 0
                dF[pos] = quantum_minus_classical(hw, T[pos], weights=w, imaginary="drop") / len(a0)
                nimag = int(np.sum(hw < -1e-4)); frac = float(np.sum(w[hw < -1e-4]) / np.sum(w))
                for Tk, g, v in zip(T, G - dF, V):
                    rows.append({"phase": ph, "kind": "solution", "x": x, "T": float(Tk), "P_GPa": 0.0, "G": float(g), "G_err": 0.0, "V": float(v), "model": MODEL, "reference_state": "absolute ACE energy",
                                 "method": "QHA vinet, phonopy sc=[2,2,2] mesh=60.0, classical level; 64-atom SQS (extend_range.py)", "config_entropy": "none", "quantum": "classical+harmonic-correction",
                                 "n_atoms": len(a0), "source": f"calphad_user_needs ext {key}"})
                status[key] = {"ok": True, "phase": ph, "x": x, "E0_eV_per_atom": float(r.energy_per_atom), "V0": float(r.volume_per_atom), "sqs_dev": dev, "disp_rms_A": float(np.sqrt(np.mean(disp ** 2))),
                               "disp_max_A": float(disp.max()), "n_imag_modes": nimag, "imag_weight_fraction": frac, "sg": f"{r.spacegroup_before}->{r.spacegroup_after}", "seconds": time.time() - t0}
            except Exception as e:
                status[key] = {"ok": False, "phase": ph, "x": x, "error": repr(e)[:300], "seconds": time.time() - t0}
            print(key, json.dumps(status[key]), flush=True)
            json.dump(status, open(STAT, "w"), indent=1); pd.DataFrame(rows).to_csv(TSV, sep="\t", index=False)


def report():
    """Full-range table = example-6 table + the new fcc/bcc cells (ideal mixing added, cells with imaginary modes excluded from the
    fits but listed); G(x) of fcc, bcc and liquid over 0..1; the metastable fcc/bcc/liquid diagram without compounds; the spinodal
    of each solution (d2G/dx2 < 0)."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table
    from ftphase.diagram import scan
    st = json.load(open(STAT)); new = pd.read_csv(TSV, sep="\t")
    bad = {(v["phase"], v["x"]) for v in st.values() if v.get("ok") and (v["n_imag_modes"] > 0 or v["disp_max_A"] > 0.5)}
    new = new[[(p, x) not in bad for p, x in zip(new.phase, new.x)]]
    tabn = FreeEnergyTable.from_rows(new.to_dict("records"), {})
    for ph in ("fcc", "bcc"):
        if (tabn.df.phase == ph).any() and tabn.df[tabn.df.phase == ph]["x"].nunique() > 1:
            tabn = add_configurational_term(tabn, ph, "ideal")      # x = 0 / 1 rows get a zero term
    old = FreeEnergyTable.from_tsv(os.path.join(EX6, "out_full", "05_free_energies.tsv"))
    df = pd.concat([old.df, tabn.df], ignore_index=True); tab = FreeEnergyTable.from_dataframe(df, old.meta)
    rng = {ph: [float(g.x.min()), float(g.x.max()), int(g.x.nunique())] for ph, g in df[df.phase.isin(["fcc", "bcc", "liquid"])].groupby("phase")}
    S = {"cells": {k: {q: v[q] for q in ("phase", "x", "E0_eV_per_atom", "disp_rms_A", "disp_max_A", "n_imag_modes", "imag_weight_fraction") if q in v} for k, v in st.items()},
         "excluded_as_unstable": sorted(bad), "composition_range_after": rng}
    FITS = {"fcc": "poly", "bcc": "poly", "liquid": "rk", "B32": "spline"}; kw = dict(fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4, "fcc": 4, "bcc": 4})
    cf = os.path.join(OUT, "2_curvature.json"); CURV = json.load(open(cf)) if os.path.exists(cf) else {}
    WS = {k: v for k, v in {"Al3Li": ("Al3Li (L1_2)", (3, 1)), "Al2Li3": ("Al2Li3 (R-3m)", (2, 3)), "Al4Li9": ("Al4Li9 (C2/m)", (4, 9))}.items() if v[0] in CURV}
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2)); S["spinodal"] = {}
    for ax, T in zip(axes[:2], (500.0, 800.0)):
        Ts = np.array([T]); ti = interpolate_T(tab, Ts); ph = builder_from_table(ti, **kw)(T)
        gA = float(ti.df[(ti.df.phase == "fcc") & (ti.df.x < 1e-6)]["G"].iloc[0]); gB = float(ti.df[(ti.df.phase == "bcc") & (ti.df.x > 1 - 1e-6)]["G"].iloc[0]); ref = lambda x: (1 - x) * gA + x * gB
        # compounds in the two treatments of Fig. 18 at this temperature:
        #   thick solid = point defects: Wagner-Schottky with the defect free energies eps_d(T) of the largest cell + the interaction term
        #                 from the multi-defect cells (ftphase.compounds.CompoundModel), drawn over the composition range that was sampled
        #   dashed + open circles = small cells with one anti-site on each side treated as a phase with a range (spline through 3 cells)
        from ftphase.compounds import CompoundModel, interaction_polynomial
        from ftphase.aiida.functions import _site_model
        MAPD = {"A_on_B": "Al_on_Li", "B_on_A": "Li_on_Al", "Va_on_B": "Va_Li", "Va_on_A": "Va_Al"}; SCN = {"Al3Li": (3, 1), "B32": (1, 1), "Al2Li3": (2, 3), "Al4Li9": (4, 9)}

        def model(name):
            d = json.load(open(os.path.join(OUT, f"7_defectF_{name}.json")))["sizes"]; N = max(int(q) for q in d); big = d[str(N)]; Tg = np.array(big["T"])
            eps = {a: np.array(big["defects"][b]["eps_T_eV"]) for a, b in MAPD.items()}; w = {}; w3 = {}; lo = hi = 0.03; r9 = json.load(open(os.path.join(OUT, f"9_interaction_{name}.json")))
            for a, b in (("A_on_B", "Al_on_Li"), ("B_on_A", "Li_on_Al")):
                cells = [c for c in r9["cells"].values() if c["side"] == b and "dG_T_eV" in c and c.get("n_imag", 0) == 0]
                if len(cells) >= 6:
                    kk = np.array([c["k"] for c in cells]); dG = np.array([c["dG_T_eV"] for c in cells]); ww = np.array([interaction_polynomial(dG[:, i], kk, eps[a][i], N) for i in range(len(Tg))]); w[a] = ww[:, 0]; w3[a] = ww[:, 1]
                    ext = max(abs(c["x"] - SCN[name][1] / sum(SCN[name])) for c in cells)
                    lo, hi = (max(lo, ext), hi) if a == "A_on_B" else (lo, max(hi, ext))
            return CompoundModel(name, SCN[name][1] / sum(SCN[name]), SCN[name], Tg, eps, w, w3=w3), min(lo, 0.08), min(hi, 0.08)

        def small_cells(name, x0):
            if name == "B32":
                return None
            tr_ = FreeEnergyTable.from_rows(pd.read_csv(os.path.join(OUT, f"6_range_{name}.tsv"), sep="\t").to_dict("records"), {})
            tr_ = add_configurational_term(tr_, name, "sublattice", site_model=_site_model("b32_antisite", x0)); tq = interpolate_T(tr_, Ts)
            return [q for q in builder_from_table(tq, fit="spline", fits={name: "spline"})(T) if q.name == name][0], tq.df[tq.df.phase == name].sort_values("x")

        S.setdefault("compound_lines", {})[int(T)] = {}
        for p in ph:
            if hasattr(p, "x0") or p.name == "B32":
                x0 = p.x0 if hasattr(p, "x0") else 0.5; g0 = p.g0 if hasattr(p, "x0") else float(ti.df[(ti.df.phase == "B32") & np.isclose(ti.df.x, 0.5)]["G"].iloc[0])
                (pt,) = ax.plot([x0], [(g0 - ref(x0)) * 1000], "o", ms=5, label=p.name); col = pt.get_color()
                m, lo, hi = model(p.name); xw = np.linspace(x0 - lo, x0 + hi, 161); gw = m.values(xw, T, g0)
                ax.plot(xw, (gw - ref(xw)) * 1000, "-", color=col, lw=2.2)
                if p.name == "B32":            # the range-phase treatment of B32 is the curve of the table (16-atom cells, example 6)
                    xs, g = p.sample(); ax.plot(xs, (g - ref(xs)) * 1000, "--", color=col, lw=1.3); pts = ti.df[ti.df.phase == "B32"]; ax.plot(pts.x, (pts.G - ref(pts.x)) * 1000, "o", color=col, ms=4.5, mfc="none")
                    sm = (xs, g)
                else:
                    q, pts = small_cells(p.name, x0); xs = np.linspace(q.x_min, q.x_max, 121); g = q.g(xs) + (g0 - float(q.g(np.array([x0]))[0]))     # aligned at stoichiometry (the small stoichiometric cell and the table cell differ by < 1 meV)
                    ax.plot(xs, (g - ref(xs)) * 1000, "--", color=col, lw=1.3); ax.plot(pts.x, (pts.G + (g0 - float(q.g(np.array([x0]))[0])) - ref(pts.x)) * 1000, "o", color=col, ms=4.5, mfc="none")
                    sm = (xs, g)
                S["compound_lines"][int(T)][p.name] = {"defect_model_range": [round(float(x0 - lo), 3), round(float(x0 + hi), 3)],
                                                        "small_cells_minus_defect_model_meV_at_ends": [round(float((np.interp(xq, sm[0], sm[1]) - np.interp(xq, xw, gw)) * 1000), 1) for xq in (max(sm[0].min(), xw.min()), min(sm[0].max(), xw.max()))]}
                continue
            xs, g = p.sample(); (ln,) = ax.plot(xs, (g - ref(xs)) * 1000, lw=1.7, label=f"{p.name} ({p.x_min:.2f}-{p.x_max:.2f})")
            pts = ti.df[ti.df.phase == p.name]; ax.plot(pts.x, (pts.G - ref(pts.x)) * 1000, ".", color=ln.get_color(), ms=5)
            if p.name in ("fcc", "bcc"):
                h = 0.01; xx = np.linspace(p.x_min + h, p.x_max - h, 400); d2 = (p.g(xx + h) - 2 * p.g(xx) + p.g(xx - h)) / h ** 2; neg = xx[d2 < 0]
                S["spinodal"].setdefault(p.name, {})[int(T)] = [round(float(neg.min()), 3), round(float(neg.max()), 3)] if len(neg) else None
        # equilibrium = lower convex hull of all G(x); not drawn (it made the figure hard to read), only its two-phase segments are recorded
        from ftphase.equilibrium import lower_hull
        pts, labs, idx = lower_hull(ph); hx = pts[idx, 0]; o = np.argsort(hx); hx = hx[o]; hl = [labs[i] for i in np.asarray(idx)[o]]
        segs = [(hl[i], round(float(hx[i]), 3), hl[i + 1], round(float(hx[i + 1]), 3)) for i in range(len(hx) - 1) if hl[i] != hl[i + 1] or hx[i + 1] - hx[i] > 0.02]
        S.setdefault("hull_two_phase_segments", {})[int(T)] = segs
        ax.set(xlabel="x_Li", ylabel="G - [(1-x) G(fcc Al) + x G(bcc Li)]  (meV/atom)", title=f"{T:.0f} K: G(x) of every phase (dots = computed cells)"); ax.title.set_fontsize(9)
        from matplotlib.lines import Line2D
        hd, lb = ax.get_legend_handles_labels(); hd += [Line2D([], [], color="0.3", lw=2.2), Line2D([], [], color="0.3", lw=1.3, ls="--", marker="o", mfc="none", ms=4.5)]; lb += ["compound: point defects ε$_d$(T) + interaction", "compound: small anti-site cells (range phase)"]; ax.legend(hd, lb, fontsize=6.3)
    # metastable diagram of the solutions only (no compounds)
    Th = np.arange(300.0, 1100.1, 10.0); ti = interpolate_T(FreeEnergyTable.from_dataframe(df[df.phase.isin(["fcc", "bcc", "liquid"])], old.meta), Th)
    cov = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"]); okT = set(cov[(cov["min"] < 1e-6) & (cov["max"] > 1 - 1e-6) & (cov["size"] >= 6)].index)
    ti = FreeEnergyTable.from_dataframe(ti.df[(ti.df.phase != "liquid") | ti.df["T"].isin(okT)], ti.meta)
    reg = scan(builder_from_table(ti, **kw), Th, min_width=0.005, gap_tol=2.5); r = reg[reg.phase_a != reg.phase_b]; ax = axes[2]
    cols = {}
    for row in r.itertuples():
        key = "+".join(sorted([row.phase_a, row.phase_b])); c = cols.setdefault(key, f"C{len(cols)}")
        ax.fill_between([min(row.x_a, row.x_b), max(row.x_a, row.x_b)], row.T - 5, row.T + 5, color=c, lw=0, label=key)
    hl = dict(zip(*ax.get_legend_handles_labels()[::-1])); ax.legend(hl.values(), hl.keys(), fontsize=7)
    ax.set(xlim=(0, 1), ylim=(300, 1100), xlabel="x_Li", ylabel="T (K)", title="metastable diagram: solutions only (no compounds)"); ax.title.set_fontsize(8.5)
    S["solutions_only_regions"] = {int(T): "; ".join(f"{q.phase_a}({q.x_a:.3f})+{q.phase_b}({q.x_b:.3f})" for q in r[np.isclose(r["T"], T)].itertuples()) for T in (400.0, 600.0, 800.0)}
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "1_full_range.png"), dpi=150); json.dump(S, open(os.path.join(OUT, "1_full_range.json"), "w"), indent=1, default=str)
    tab.to_tsv(os.path.join(OUT, "1_full_range_table.tsv")); print(json.dumps({k: S[k] for k in ("excluded_as_unstable", "composition_range_after", "spinodal", "solutions_only_regions")}, indent=1, default=str))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1] if len(sys.argv) > 1 else "run"]()
