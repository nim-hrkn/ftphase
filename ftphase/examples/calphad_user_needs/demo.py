"""What a CALPHAD / phase-field user needs beyond the stable diagram, tried on ACE Al-Li (example 6 table):

  1. metastable   G(x) of every phase (also where it is metastable) and metastable diagrams with phases suppressed
                  (fcc + Al3Li = the delta' solvus without B32; fcc + liquid without compounds)
  2. curvature    d2G/dx2 and the chemical-potential difference at a line compound: B32 from its defect cells, and Al3Li
                  (a point phase so far) from four static defect cells + the Wagner-Schottky model
  3. sgte         pure-element references replaced by SGTE (Dinsdale 1991): per phase G += (1-x) dA + x dB with
                  d_i = G_i^SGTE(phase) - G_i^MLIP(phase), so the pure melting points are exact; the MLIP supplies only mixing
                  and formation quantities.  sgte_unary.json comes from sgte_unary.py (env/pycalphad).

    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/demo.py [metastable] [curvature] [sgte]     -> out/
"""
import json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram")
sys.path.insert(0, EX6)
KB = 8.617333262e-5; EV2J = 96485.33212
FITS = {"fcc": "poly", "bcc": "poly", "liquid": "rk", "B32": "spline"}; HULL = {"min_width": 0.005, "gap_tol": 2.5}


def table():
    from ftphase.records import FreeEnergyTable
    return FreeEnergyTable.from_tsv(os.path.join(EX6, "out_full", "05_free_energies.tsv"))


def grid_table(tab, Ts, liquid=True):
    """Table interpolated on Ts; with liquid=True only temperatures where the liquid covers both pure ends (as in example 6)."""
    from ftphase.assemble import interpolate_T
    from ftphase.records import FreeEnergyTable
    df = tab.df if liquid else tab.df[tab.df.phase != "liquid"]
    ti = interpolate_T(FreeEnergyTable.from_dataframe(df, tab.meta), Ts)
    if liquid:
        cov = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"]); ok = cov[(cov["min"] < 1e-6) & (cov["max"] > 1 - 1e-6) & (cov["size"] >= 6)].index
        ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(ok)], ti.meta)
    return ti


def make_builder(ti, keep=None):
    from ftphase.assemble import builder_from_table
    b = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4})
    if keep is None:
        return b
    return lambda T, offsets=None, slopes=None: [p for p in b(T, offsets, slopes) if p.name in keep]


def fmt(reg, T):
    r = reg[np.isclose(reg["T"], T)]
    return "; ".join(f"{p.phase_a}({p.x_a:.3f})+{p.phase_b}({p.x_b:.3f})" for p in r.itertuples() if p.phase_a != p.phase_b)


def metastable(S):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.diagram import scan, invariants
    from ftphase.equilibrium import PointPhase
    tab = table(); Tl = np.arange(300.0, 700.1, 10.0); ts = grid_table(tab, Tl, liquid=False); res = {}
    # (a) delta' (Al3Li) solvus: fcc + Al3Li with B32 suppressed, against the stable fcc + B32 solvus
    for name, keep in (("stable (all solids)", None), ("B32 suppressed: fcc + Al3Li", {"fcc", "Al3Li"})):
        reg = scan(make_builder(ts, keep), Tl, **HULL); rows = []
        for T in Tl:
            r = reg[np.isclose(reg["T"], T) & (reg.phase_a == "fcc") & (reg.phase_b != "fcc")]
            if len(r):
                rows.append((float(T), float(r.x_a.min()), str(r.phase_b.iloc[0])))
        res[name] = rows
    S["fcc_solvus"] = {k: [(T, round(x, 4), ph) for T, x, ph in v if T in (300, 400, 500, 600, 700)] for k, v in res.items()}
    # (b) fcc + liquid without any compound (the liquidus/solidus a rapidly solidified alloy would see), with the liquid window
    Th = np.arange(650.0, 1100.1, 10.0); th = grid_table(tab, Th); reg_fl = scan(make_builder(th, {"fcc", "liquid", "bcc"}), np.array(sorted(th.df["T"].unique())), **HULL)
    S["no_compounds"] = {int(T): fmt(reg_fl, T) for T in (650, 700, 760, 800, 850)}
    # (c) G(x) of every phase relative to fcc Al and bcc Li at two temperatures
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3))
    for ax, T, liq in zip(axes[:2], (500.0, 800.0), (False, True)):
        ti = grid_table(tab, np.array([T]), liquid=liq) if liq else grid_table(tab, np.array([T]), liquid=False)
        if liq and ti.df.empty:
            ti = grid_table(tab, np.array([T]), liquid=False)
        ph = make_builder(ti)(T); gA = float(ti.df[(ti.df.phase == "fcc") & (ti.df.x < 1e-6)]["G"].iloc[0]); gB = float(ti.df[(ti.df.phase == "bcc") & (ti.df.x > 1 - 1e-6)]["G"].iloc[0])
        ref = lambda x: (1 - x) * gA + x * gB
        for p in ph:
            if isinstance(p, PointPhase):
                ax.plot([p.x0], [(p.g0 - ref(p.x0)) * 1000], "o", ms=6, label=p.name)
            else:
                xs, g = p.sample(); ax.plot(xs, (g - ref(xs)) * 1000, lw=1.6, label=f"{p.name} ({p.x_min:.2f}-{p.x_max:.2f})")
        ax.set(xlabel="x_Li", ylabel="G - [(1-x) G(fcc Al) + x G(bcc Li)]  (meV/atom)", title=f"{T:.0f} K: G(x) of every phase, also where metastable"); ax.legend(fontsize=7); ax.title.set_fontsize(9)
    ax = axes[2]
    for (name, rows), c in zip(res.items(), ("k", "#c0392b")):
        ax.plot([x for _, x, _ in rows], [T for T, _, _ in rows], "-", color=c, lw=1.8, label="fcc side of " + name)
    ax.set(xlabel="x_Li in fcc", ylabel="T (K)", xlim=(0, 0.2), title="fcc solvus: stable (vs B32) and metastable (vs Al3Li, delta')"); ax.legend(fontsize=7); ax.title.set_fontsize(9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "1_metastable.png"), dpi=150)


def curvature(S):
    from ase.build import make_supercell
    from ftphase.validate import relax
    from ftphase.configurational import wagner_schottky_curve, defect_energies_from_cells
    from pipeline import ace, l12_al3li
    tab = table(); res = {}
    # B32 (limited phase, anti-site cells): curvature of the fitted G(x) at x = 0.5
    for T in (300.0, 500.0, 700.0):
        ti = grid_table(tab, np.array([T]), liquid=False); p = next(q for q in make_builder(ti)(T) if q.name == "B32"); h = 0.01
        k = float((p.g(np.array([0.5 + h])) - 2 * p.g(np.array([0.5])) + p.g(np.array([0.5 - h])))[0] / h ** 2); mu = float(p.dg(np.array([0.5]))[0])
        res.setdefault("B32 (anti-site cells + sublattice entropy, example 6)", {})[int(T)] = {"d2G_dx2_eV": round(k, 3), "d2G_dx2_kJ_mol": round(k * EV2J / 1000, 1), "dG_dx_eV": round(mu, 4), "range": [round(p.x_min, 3), round(p.x_max, 3)]}
    # Al3Li (L1_2): four static defect cells of a 108-site supercell with ACE -> Wagner-Schottky G(x)
    calc = ace(); prim = l12_al3li(); base = relax(prim, calc, fmax=1e-3, cell=True).atoms; base.calc = None; sc = base.repeat((3, 3, 3)); sym = sc.get_chemical_symbols()
    iAl, iLi = sym.index("Al"), sym.index("Li"); cells = {"perfect": sc.copy()}
    a = sc.copy(); a[iAl].symbol = "Li"; cells["Li on Al site"] = a
    a = sc.copy(); a[iLi].symbol = "Al"; cells["Al on Li site"] = a
    a = sc.copy(); del a[iAl]; cells["Al vacancy"] = a
    a = sc.copy(); del a[iLi]; cells["Li vacancy"] = a
    rows = []
    for name, at in cells.items():
        r = relax(at, calc, fmax=2e-3, cell=False); x = at.get_chemical_symbols().count("Li") / len(at); rows.append((name, x, r.energy_per_atom, len(at)))
    de, g0, n_sites, tb = defect_energies_from_cells([r[1] for r in rows], [r[2] for r in rows], [r[3] for r in rows], (3, 1))
    out = {"defect_energies_raw_eV": {k: round(float(v), 4) for k, v in de.items()}, "cells": [(n, round(x, 5), round(e, 6), k) for n, x, e, k in rows], "T": {}}
    for T in (300.0, 500.0, 700.0):
        xs = np.linspace(0.25 - 0.012, 0.25 + 0.012, 25); g = np.array(wagner_schottky_curve(xs, T, (3, 1), de, g0_atom=0.0)); c = np.polyfit(xs - 0.25, g, 2)
        fit = np.polyval(c, xs - 0.25); out["T"][int(T)] = {"d2G_dx2_eV": round(2 * c[0], 2), "d2G_dx2_kJ_mol": round(2 * c[0] * EV2J / 1000, 0), "dG_dx_at_stoich_eV": round(c[1], 4),
                                                              "parabola_rms_meV_within_0.012": round(float(np.sqrt(np.mean((fit - g) ** 2))) * 1000, 3)}
    res["Al3Li (L1_2), Wagner-Schottky from 4 static ACE defect cells (108 sites)"] = out; S["curvature"] = res
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.6, 4.2)); xs = np.linspace(0.22, 0.28, 121)
    for T in (300.0, 500.0, 700.0):
        g = np.array(wagner_schottky_curve(xs, T, (3, 1), de, g0_atom=0.0)); ax.plot(xs, g * 1000, label=f"{T:.0f} K, d2G/dx2 = {out['T'][int(T)]['d2G_dx2_eV']:.1f} eV")
    ax.set(xlabel="x_Li", ylabel="G - G(perfect Al3Li)  (meV/atom)", title="Al3Li (L1_2): G(x) near stoichiometry from point defects"); ax.title.set_fontsize(9); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "2_curvature_al3li.png"), dpi=150)


def sgte(S):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.diagram import scan, invariants, plot_tx, write_records
    from ftphase.records import FreeEnergyTable
    U = json.load(open(os.path.join(HERE, "sgte_unary.json"))); TU = np.array(U["T"]); sg = lambda el, ph, T: np.interp(T, TU, U[el][ph])
    tab = table(); Ts = np.arange(650.0, 1100.1, 10.0); ti = grid_table(tab, Ts); df = ti.df.copy(); Ts = np.array(sorted(df["T"].unique()))
    pure = lambda ph, x0: df[(df.phase == ph) & (abs(df.x - x0) < 1e-6)].set_index("T")["G"].reindex(Ts)
    m = {("Al", "fcc"): pure("fcc", 0.0), ("Li", "bcc"): pure("bcc", 1.0), ("Al", "liquid"): pure("liquid", 0.0), ("Li", "liquid"): pure("liquid", 1.0)}
    d = {k: pd.Series(sg(k[0], k[1], Ts), index=Ts) - v for k, v in m.items()}          # SGTE - MLIP for each available pure-element phase
    ser = {"Al": "fcc", "Li": "bcc"}
    def delta(el, ph):
        return d[(el, ph)] if (el, ph) in d else d[(el, ser[el])]                        # no MLIP end member of that phase -> stable-element reference
    for ph in df.phase.unique():
        msk = df.phase == ph; T = df.loc[msk, "T"].to_numpy(); x = df.loc[msk, "x"].to_numpy()
        df.loc[msk, "G"] = df.loc[msk, "G"].to_numpy() + (1 - x) * delta("Al", ph).reindex(T).to_numpy() + x * delta("Li", ph).reindex(T).to_numpy()
    out = {}
    for name, t in (("MLIP references (example 6)", ti), ("SGTE pure-element references", FreeEnergyTable.from_dataframe(df, ti.meta))):
        reg = scan(make_builder(t), Ts, **HULL); inv = invariants(reg); r = reg[reg.phase_a != reg.phase_b]
        fl = r[(r.phase_a == "fcc") & (r.phase_b == "liquid") & (r.x_a < 0.02)]; liq = r[(r.phase_a == "liquid") | (r.phase_b == "liquid")]
        b32l = r[((r.phase_a == "B32") & (r.phase_b == "liquid")) | ((r.phase_a == "liquid") & (r.phase_b == "B32"))]
        eut = r[(r.phase_a == "fcc") & (r.phase_b == "B32")]
        out[name] = {"fcc+liquid_highest_T_K": float(fl["T"].max()) if len(fl) else None, "fcc+B32_highest_T_K (eutectic below +10)": float(eut["T"].max()) if len(eut) else None,
                     "B32+liquid_highest_T_K": float(b32l["T"].max()) if len(b32l) else None, "regions_800K": fmt(reg, 800.0), "regions_700K": fmt(reg, 700.0),
                     "invariants": [(float(a.T_low), float(a.T_high)) for a in inv.itertuples()]}
        if name.startswith("SGTE"):
            write_records(os.path.join(OUT, "3_sgte_two_phase_regions.tsv"), reg, {"note": "example 6 table with SGTE pure-element references per phase"})
            ax = plot_tx(r, xlabel="x_Li", dT=10.0); ax.set_xlim(0, 1); ax.set_title("ACE Al-Li, example 6 with SGTE pure-element references (Al 933.5 K, Li 453.6 K exact)", fontsize=8.5)
            ax.figure.savefig(os.path.join(OUT, "3_sgte_phase_diagram.png"), dpi=150, bbox_inches="tight")
    out["shift_SGTE_minus_MLIP_meV"] = {f"{k[0]} {k[1]}": {int(T): round(float(v.loc[T] - d[(k[0], ser[k[0]])].loc[T]) * 1000, 2) for T in (700.0, 900.0, 1100.0) if T in v.index} for k, v in d.items() if k[1] == "liquid"}
    out["experiment"] = {"Al melting": 933.5, "eutectic": 875, "B32 congruent": "about 970-990 (assessment 975)"}
    S["sgte"] = out


def main():
    os.makedirs(OUT, exist_ok=True); what = sys.argv[1:] or ["metastable", "curvature", "sgte"]; sf = os.path.join(OUT, "summary.json")
    S = json.load(open(sf)) if os.path.exists(sf) else {}
    for w in what:
        {"metastable": metastable, "curvature": curvature, "sgte": sgte}[w](S); json.dump(S, open(sf, "w"), indent=1, default=str); print("done", w, flush=True)
    print(json.dumps(S, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
