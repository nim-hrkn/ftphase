"""Step B of the Saengdeejing-type CALPHAD route for Pt-Rh (2026-11-11): write the TDB from params.json and compute the diagram.

    env/pycalphad/bin/python ftphase/examples/ptrh/calphad_tdb.py ptrh/out/calphad_mace_mpa_0 [--liquid ideal|fcc] [--T 100 2400]

TDB: SGTE91 unaries (espei.refdata: GHSERPT, GHSERRH, liquids), FCC_A1 (PT,RH) with the fitted Redlich-Kister L_k = a_k + b_k T,
PTRH_I41AMD = (PT,RH)0.5(PT,RH)0.5 and D022 = (PT,RH)0.75(PT,RH)0.25 two-sublattice CEF phases with Neumann-Kopp end-members
(PT:PT = GHSERPT, RH:RH = GHSERRH, mixed = NK sum + a + b T from params.json; D022 PT:RH = Pt3Rh, RH:PT = PtRh3), LIQUID ideal
(--liquid fcc copies the fcc excess into the liquid, the reading of the paper's Table 6 where the liquid row repeats the fcc values).
The SGTE functions are written with a lower limit of 1 K so that the 100-300 K ordering window can be computed; below 298.15 K
this is the SGTE polynomial extrapolation, which cancels between the solid phases because they share the same GHSER.
Outputs in the same folder: ptrh_<tag>[_liqfcc].tdb, grid.tsv (phase set on a T-x grid), invariants.json, diagram.png.
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def piecewise_to_tdb(expr, name, lo=1.0):
    """espei.refdata Piecewise -> TDB FUNCTION line (symengine/sympy Piecewise with And(T < hi, lo <= T) conditions)."""
    import re
    parts = []
    args = list(expr.args)
    pairs = args if args and isinstance(args[0], (tuple, list)) else list(zip(args[0::2], args[1::2]))   # sympy ExprCondPair vs symengine flat list
    for e, c in pairs:
        s = str(c)
        if s in ("True",):
            continue
        his = re.findall(r"T < ([0-9.e+]+)", s); los = re.findall(r"([0-9.e+]+) <= T", s)
        parts.append((float(los[0]), float(his[0]), str(e)))
    parts.sort()
    body = ""
    for i, (l, h, e) in enumerate(parts):
        e = e.replace("**", "**").replace("log(T)", "LN(T)")
        body += (f"{lo:g} " if i == 0 else "") + f"{e}; {h:g} " + ("Y\n   " if i < len(parts) - 1 else "N !\n")
    return f"FUNCTION {name} " + body


def ordering_params(par, x, phases):
    """Partitioned model: ordered-part end-member values u (a, b) so that G_total(ordered, stoichiometric) = G_fcc(x) + [dG_f(cell) - dG_mix_fcc(x)].
    phases = [(name, x_i, site fraction product p_i)]: ordered state minus disordered state = u_i - p*(u_1 + u_2) with p = x(1-x) summed over the two
    mixed end-members (0.25 for PtRh, 0.1875 for D022)."""
    rk = par["fcc"]["RK"]
    def rk_mix(xx):
        return (xx * (1 - xx) * sum(r["a_J"] * (1 - 2 * xx) ** r["k"] for r in rk), xx * (1 - xx) * sum(r["b_J_per_K"] * (1 - 2 * xx) ** r["k"] for r in rk))
    n = len(phases); A = np.zeros((n, n)); rhs_a = np.zeros(n); rhs_b = np.zeros(n)
    for i, (nm, xi, p) in enumerate(phases):
        A[i, :] -= p; A[i, i] += 1.0
        ma, mb = rk_mix(xi); c = par["ordered"][nm]
        rhs_a[i] = c["a_J"] - ma; rhs_b[i] = c["b_J_per_K"] - mb
    ua = np.linalg.solve(A, rhs_a); ub = np.linalg.solve(A, rhs_b)
    return {nm: (float(ua[i]), float(ub[i]), float(rhs_a[i]), float(rhs_b[i])) for i, (nm, _, _) in enumerate(phases)}


def write_tdb(par, path, liquid="ideal", model="partition"):
    from espei.refdata import SGTE91, SGTE91Stable
    L = [f"$ Pt-Rh CALPHAD description built from the MLIP run {os.path.basename(par['run'])} ({par['model']}) by calphad_tdb.py",
         "$ Saengdeejing-type route: SGTE91 unaries, fcc RK from random cells (E0 + harmonic F_vib), ordered phases 2-sublattice CEF with Neumann-Kopp end-members, liquid " + liquid,
         "ELEMENT /-   ELECTRON_GAS              0.0000E+00  0.0000E+00  0.0000E+00!",
         "ELEMENT VA   VACUUM                    0.0000E+00  0.0000E+00  0.0000E+00!",
         "ELEMENT PT   FCC_A1                    1.9508E+02  5.7230E+03  4.1631E+01!",
         "ELEMENT RH   FCC_A1                    1.0291E+02  4.9200E+03  3.1505E+01!", ""]
    L.append(piecewise_to_tdb(SGTE91Stable["PT"], "GHSERPT")); L.append(piecewise_to_tdb(SGTE91Stable["RH"], "GHSERRH"))
    L.append(piecewise_to_tdb(SGTE91[("PT", "LIQUID")], "GLIQPT")); L.append(piecewise_to_tdb(SGTE91[("RH", "LIQUID")], "GLIQRH"))
    rk = par["fcc"]["RK"]; od = par["ordered"]
    def ab(a, b): return f"{a:+.3f}{b:+.5f}*T"
    L += ["", "TYPE_DEFINITION % SEQ *!", "DEFINE_SYSTEM_DEFAULT ELEMENT 2 !", "DEFAULT_COMMAND DEF_SYS_ELEMENT VA /- !", "",
          "PHASE LIQUID %  1  1.0 !", "CONSTITUENT LIQUID :PT,RH :  !",
          "PARAMETER G(LIQUID,PT;0)  1 +GLIQPT; 6000 N !", "PARAMETER G(LIQUID,RH;0)  1 +GLIQRH; 6000 N !"]
    if liquid == "fcc":
        L += [f"PARAMETER L(LIQUID,PT,RH;{r['k']})  1 {ab(r['a_J'], r['b_J_per_K'])}; 6000 N !" for r in rk]
    L += ["", "PHASE FCC_A1 %  1  1.0 !", "CONSTITUENT FCC_A1 :PT,RH :  !",
          "PARAMETER G(FCC_A1,PT;0)  1 +GHSERPT; 6000 N !", "PARAMETER G(FCC_A1,RH;0)  1 +GHSERRH; 6000 N !"]
    L += [f"PARAMETER L(FCC_A1,PT,RH;{r['k']})  1 {ab(r['a_J'], r['b_J_per_K'])}; 6000 N !" for r in rk]
    if model == "plain":   # 2-sublattice CEF with Neumann-Kopp end-members (its disordered state competes with FCC_A1 at high T)
        if "PtRh" in od:
            c = od["PtRh"]
            L += ["", "PHASE PTRH_I41AMD %  2  0.5  0.5 !", "CONSTITUENT PTRH_I41AMD :PT,RH : PT,RH :  !",
                  "PARAMETER G(PTRH_I41AMD,PT:PT;0)  1 +GHSERPT; 6000 N !", "PARAMETER G(PTRH_I41AMD,RH:RH;0)  1 +GHSERRH; 6000 N !",
                  f"PARAMETER G(PTRH_I41AMD,PT:RH;0)  1 +0.5*GHSERPT+0.5*GHSERRH{ab(c['a_J'], c['b_J_per_K'])}; 6000 N !",
                  f"PARAMETER G(PTRH_I41AMD,RH:PT;0)  1 +0.5*GHSERPT+0.5*GHSERRH{ab(c['a_J'], c['b_J_per_K'])}; 6000 N !"]
        if "Pt3Rh" in od or "PtRh3" in od:
            L += ["", "PHASE D022 %  2  0.75  0.25 !", "CONSTITUENT D022 :PT,RH : PT,RH :  !",
                  "PARAMETER G(D022,PT:PT;0)  1 +GHSERPT; 6000 N !", "PARAMETER G(D022,RH:RH;0)  1 +GHSERRH; 6000 N !"]
            if "Pt3Rh" in od:
                c = od["Pt3Rh"]; L.append(f"PARAMETER G(D022,PT:RH;0)  1 +0.75*GHSERPT+0.25*GHSERRH{ab(c['a_J'], c['b_J_per_K'])}; 6000 N !")
            if "PtRh3" in od:
                c = od["PtRh3"]; L.append(f"PARAMETER G(D022,RH:PT;0)  1 +0.25*GHSERPT+0.75*GHSERRH{ab(c['a_J'], c['b_J_per_K'])}; 6000 N !")
    else:   # order-disorder partition: G = G_FCC_A1(x) + G_ord(y) - G_ord(y = x); only the ordering energy enters the ordered part
        L += ["", "TYPE_DEFINITION ' GES A_P_D PTRH_I41AMD DIS_PART FCC_A1,,,!", "TYPE_DEFINITION \" GES A_P_D D022 DIS_PART FCC_A1,,,!"]
        info = {}
        if "PtRh" in od:
            u = ordering_params(par, 0.5, [("PtRh", 0.5, 0.5)])["PtRh"]; info["PtRh"] = u   # PT:RH and RH:PT share u: disordered state = 2 * 0.25 * u
            L += ["", "PHASE PTRH_I41AMD %'  2  0.5  0.5 !", "CONSTITUENT PTRH_I41AMD :PT,RH : PT,RH :  !",
                  "PARAMETER G(PTRH_I41AMD,PT:PT;0)  1 0; 6000 N !", "PARAMETER G(PTRH_I41AMD,RH:RH;0)  1 0; 6000 N !",
                  f"PARAMETER G(PTRH_I41AMD,PT:RH;0)  1 {ab(u[0], u[1])}; 6000 N !", f"PARAMETER G(PTRH_I41AMD,RH:PT;0)  1 {ab(u[0], u[1])}; 6000 N !"]
        d = [(nm, x, 0.1875) for nm, x in (("Pt3Rh", 0.25), ("PtRh3", 0.75)) if nm in od]
        if d:
            u = ordering_params(par, None, d); info.update(u)
            L += ["", "PHASE D022 %\"  2  0.75  0.25 !", "CONSTITUENT D022 :PT,RH : PT,RH :  !",
                  "PARAMETER G(D022,PT:PT;0)  1 0; 6000 N !", "PARAMETER G(D022,RH:RH;0)  1 0; 6000 N !"]
            if "Pt3Rh" in u:
                L.append(f"PARAMETER G(D022,PT:RH;0)  1 {ab(u['Pt3Rh'][0], u['Pt3Rh'][1])}; 6000 N !")
            if "PtRh3" in u:
                L.append(f"PARAMETER G(D022,RH:PT;0)  1 {ab(u['PtRh3'][0], u['PtRh3'][1])}; 6000 N !")
        L.insert(2, "$ ordering energies dG_f(cell) - dG_mix_fcc(x) (J/mol, J/mol/K): " + ", ".join(f"{k} {v[2]:+.0f} {v[3]:+.2f}T" for k, v in info.items()))
    open(path, "w").write("\n".join(L) + "\n")


ETA_MIN = 0.05   # |y_Rh(sublattice 1) - y_Rh(sublattice 2)| below which a partitioned ordered phase is counted as disordered fcc


def grid_scan(dbf, Ts, xs):
    """Phase set on the (T, x) grid. For partitioned ordered phases (DIS_PART FCC_A1) pycalphad drops FCC_A1 and the ordered phase
    covers the disordered state too, so a vertex with site fractions equal on both sublattices is relabelled FCC_A1."""
    from pycalphad import equilibrium, variables as v
    comps = ["PT", "RH", "VA"]; phases = sorted(dbf.phases)
    part = {p for p in phases if len(dbf.phases[p].constituents) == 2}   # 2-sublattice ordered phases (partitioned or plain): disordered state -> FCC_A1
    rows = []
    for T in Ts:
        eq = equilibrium(dbf, comps, phases, {v.N: 1, v.P: 101325, v.T: float(T), v.X("RH"): xs}, calc_opts={"pdens": 2000})
        for i, x in enumerate(eq.coords["X_RH"].values):
            ph, xph, eta = [], [], []
            for j, p in enumerate(eq.Phase.values[0, 0, 0, i]):
                if not p:
                    continue
                e = 0.0
                if p in part:
                    y = eq.Y.values[0, 0, 0, i, j, :4]; e = float(abs(y[1] - y[3]))
                    if e < ETA_MIN:
                        p = "FCC_A1"
                ph.append(p); xph.append(float(eq.X.values[0, 0, 0, i, j, 1])); eta.append(e)
            rows.append((float(T), float(x), tuple(sorted(set(ph))), {p: (q, e) for p, q, e in zip(ph, xph, eta)}))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("folder"); ap.add_argument("--liquid", default="ideal", choices=["ideal", "fcc"])
    ap.add_argument("--T", nargs=2, type=float, default=[100, 2400]); ap.add_argument("--dT", type=float, default=10); ap.add_argument("--dx", type=float, default=0.005)
    ap.add_argument("--model", default="partition", choices=["partition", "plain"]); ap.add_argument("--suffix", default="")
    a = ap.parse_args()
    folder = a.folder if os.path.isabs(a.folder) else os.path.join(HERE, a.folder) if not os.path.exists(a.folder) else a.folder
    par = json.load(open(os.path.join(folder, "params.json"))); tag = os.path.basename(os.path.normpath(folder)).replace("calphad_", "")
    suf = ("" if a.liquid == "ideal" else "_liqfcc") + ("" if a.model == "partition" else "_plain") + a.suffix + ("_lowT" if a.T[1] <= 600 else "")
    tdb = os.path.join(folder, f"ptrh_{tag}{suf.replace('_lowT', '')}.tdb"); write_tdb(par, tdb, a.liquid, a.model); print("wrote", tdb)
    from pycalphad import Database
    dbf = Database(tdb)
    Ts = np.arange(a.T[0], a.T[1] + 1e-6, a.dT); xs = np.arange(0, 1 + 1e-9, a.dx)
    rows = grid_scan(dbf, Ts, xs)
    with open(os.path.join(folder, f"grid{suf}.tsv"), "w") as f:
        f.write("T_K\tx_Rh\tphases\tx_phases[x, eta]\n")
        for T, x, ph, xph in rows:
            f.write(f"{T:g}\t{x:.4f}\t{'+'.join(ph)}\t{json.dumps({p: [round(q, 4), round(e, 3)] for p, (q, e) in xph.items()})}\n")
    # landmarks from the grid
    inv = {"liquid": a.liquid, "T_grid": [a.T[0], a.T[1], a.dT]}
    for ph in sorted(dbf.phases):
        if ph in ("FCC_A1", "LIQUID"):
            continue
        pts = [(T, x) for T, x, p, _ in rows if ph in p]
        if pts:
            Tm = max(t for t, _ in pts); xm = [x for t, x in pts if t == Tm]
            inv[f"{ph}_Tmax_K"] = Tm; inv[f"{ph}_x_at_Tmax"] = [min(xm), max(xm)]
            lo = [(T, x) for T, x, p, _ in rows if p == (ph,)]; inv[f"{ph}_single_phase_Tmax_K"] = max(t for t, _ in lo) if lo else None
    three = sorted(set((T, p) for T, x, p, _ in rows if len(p) >= 3)); inv["three_phase_grid"] = [(t, "+".join(p)) for t, p in three]
    # melting: lowest T where liquid is present at x=0 and x=1, and solidus/liquidus from the two-phase band
    for xe, nm in ((0.0, "Pt"), (1.0, "Rh")):
        tl = [T for T, x, p, _ in rows if abs(x - xe) < 1e-9 and "LIQUID" in p]; inv[f"T_m_{nm}_grid_K"] = min(tl) if tl else None
    band = [(T, x) for T, x, p, _ in rows if p == ("FCC_A1", "LIQUID")]
    inv["fcc+liquid_width_max_x"] = None
    if band:
        w = {}
        for T, x in band:
            w.setdefault(T, []).append(x)
        Tw = max(w, key=lambda t: max(w[t]) - min(w[t]) + a.dx); inv["fcc+liquid_width_max_x"] = [round(max(w[Tw]) - min(w[Tw]) + a.dx, 3), Tw]
    # mapping invariants (pycalphad BinaryStrategy), if it works
    try:
        from pycalphad import variables as v
        from pycalphad.mapping import BinaryStrategy
        conds = {v.N: 1, v.P: 101325, v.T: (max(a.T[0], 100), a.T[1], a.dT), v.X("RH"): (0, 1, 0.01)}
        strat = BinaryStrategy(dbf, ["PT", "RH", "VA"], sorted(dbf.phases), conds); strat.do_map()
        mi = []
        for region in strat.get_invariant_data(v.X("RH"), v.T):
            try:
                d = [(str(q.phase), float(np.atleast_1d(q.x)[0]), float(np.atleast_1d(q.y)[0])) for q in region.data]
                mi.append({"T": d[0][2], "phases": [q[0] for q in d], "x": [round(q[1], 4) for q in d]})
            except Exception as e:
                mi.append({"raw": str(region)[:200]})
        inv["mapping_invariants"] = mi
    except Exception as e:
        inv["mapping_error"] = str(e)[:300]
    json.dump(inv, open(os.path.join(folder, f"invariants{suf}.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in inv.items() if k != "mapping_invariants"}, default=str)[:1500])
    print("mapping:", inv.get("mapping_invariants", inv.get("mapping_error")))
    draw(rows, folder, suf, par, a)


def draw(rows, folder, suf, par, a):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    cols = {("FCC_A1",): "#f2f2f2", ("LIQUID",): "#fde9c9", ("FCC_A1", "LIQUID"): "#e8a33c", ("PTRH_I41AMD",): "#6a9bd1", ("D022",): "#8fc37e",
            ("FCC_A1", "PTRH_I41AMD"): "#b9d0ea", ("FCC_A1", "D022"): "#cde7c3", ("D022", "PTRH_I41AMD"): "#d9c6ea", ("D022", "D022"): "#a6d68f"}
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1]})
    for ax, (T0, T1) in zip(axs, ((a.T[0], a.T[1]), (a.T[0], 400))):
        seen = {}
        for T, x, ph, _ in rows:
            if not (T0 <= T <= T1):
                continue
            c = cols.get(ph, "#999999"); seen[ph] = c
            ax.scatter(x, T, s=4 if ax is axs[0] else 9, c=c, marker="s", linewidths=0)
        ax.set_xlim(0, 1); ax.set_ylim(T0, T1); ax.set_xlabel("x_Rh"); ax.set_ylabel("T (K)")
        for ph, c in sorted(seen.items()):
            ax.scatter([], [], c=c, marker="s", s=30, label="+".join(p.replace("PTRH_I41AMD", "PtRh").replace("D022", "D0$_{22}$").replace("FCC_A1", "fcc").replace("LIQUID", "L") for p in ph))
        ax.legend(fontsize=7, loc="upper right" if ax is axs[0] else "lower right", ncol=2)
    for T, lab in ((258.0, "PFP"), (210.6, "DFT")):
        axs[1].axhline(T, color="k", ls=":" if lab == "DFT" else "--", lw=0.8); axs[1].text(0.01, T + 3, f"paper {lab} fcc→PtRh {T:.0f} K", fontsize=7)
    axs[1].axhline(2041.5 if False else 2041.5, visible=False)
    axs[0].axhline(2041.5, color="k", lw=0.5, ls=":"); axs[0].axhline(2237.0, color="k", lw=0.5, ls=":")
    axs[0].set_title(f"Pt-Rh CALPHAD from {par['model'].split(' (')[0]} (liquid {'fcc RK' if 'liqfcc' in suf else 'ideal'}, {'plain CEF' if 'plain' in suf else 'partitioned'})", fontsize=9); axs[1].set_title("ordering window 100-400 K", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(folder, f"diagram{suf}.png"), dpi=150); print("->", os.path.join(folder, f"diagram{suf}.png"))


if __name__ == "__main__":
    main()
