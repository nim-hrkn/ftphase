"""T-x diagram with every compound treated by the uniform procedure (ftphase.compounds): defect free energies of run_defects.py
+ the solutions / liquid and the stoichiometric compound rows of an existing free-energy table.
    python assemble.py nial_eam   -> out/<system>/uniform_{two_phase_regions.tsv, widths.tsv, diagram.png, REPORT.md}
"""
import glob, json, os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); EXA = os.path.join(HERE, "..")
CFG = {"nial_eam": {"table": os.path.join(EXA, "nial_eam", "out_mygardenx1_stage5", "05_free_energies.tsv"), "reference": os.path.join(EXA, "nial_eam", "out_mygardenx1_stage5", "ws", "07_two_phase_regions.tsv"),
                    "reference_label": "stage 5: B2 / L1$_2$ from sampled defect cells (triple-defect / anti-site models chosen by hand), Ni$_2$Al$_3$, NiAl$_3$ as points",
                    "compounds": ["NiAl3", "Ni2Al3", "B2", "L12"], "T": np.arange(960.0, 2000.1, 20.0), "xlabel": "x_Ni",
                    "kw": dict(fit="spline", fits={"fccAl": "poly", "fccNi": "poly", "liquid": "rk"}, poly_order=3, poly_orders={"liquid": 4, "fccAl": 2})}}


_G1 = os.path.join(EXA, "aiida_txdiagram", "out", "nial_grace_1l_b2l12ext_merged")
CFG["nial_grace_1l"] = {"table": os.path.join(_G1, "05_free_energies.tsv"), "reference": os.path.join(_G1, "ws", "07_two_phase_regions.tsv"),
                        "reference_label": "GRACE-1L: B2 / L1$_2$ from sampled defect cells (solid TI, Wagner-Schottky), Ni$_2$Al$_3$, NiAl$_3$ as points",
                        "compounds": ["NiAl3", "Ni2Al3", "B2", "L12"], "T": np.arange(960.0, 2000.1, 20.0), "xlabel": "x_Ni", "kw": CFG["nial_eam"]["kw"]}


def _alli(run, label):
    """Al-Li, solids only (300-700 K): the Li-side solid run of the MLIP (fcc, bcc, B32 and the three compounds; no liquid on the Li side)."""
    d = os.path.join(EXA, "aiida_txdiagram", "out", run)
    return {"table": os.path.join(d, "05_free_energies.tsv"), "reference": os.path.join(d, "07_two_phase_regions.tsv"),
            "reference_label": f"{label}: Al$_3$Li, Al$_2$Li$_3$, Al$_4$Li$_9$ as points, B32 as a range phase (declared in the input); solids only",
            "compounds": ["Al3Li", "B32", "Al2Li3", "Al4Li9"], "T": np.arange(300.0, 700.1, 20.0), "xlabel": "x_Li", "T_report": (300.0, 400.0, 500.0, 600.0, 700.0),
            "kw": dict(fit="spline", fits={"fcc": "poly", "bcc": "poly"}, poly_order=3)}


CFG["alli_grace_fs"] = _alli("alli_grace_fs_liside_solid", "GRACE-FS-OAM")
CFG["alli_ace"] = _alli("alli_ace_liside_solid", "ACE")


def main(system, kmax=None, quiet=False, use_lattice=None):
    """Assemble; ``kmax``: use only multi-defect cells with at most that many defects (to replay the extension loop of auto.py).
    Returns {compound: [sides whose range touches the edge of the sampled window]} (also written to extend.json)."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import interpolate_T, builder_from_table
    from ftphase.compounds import CompoundModel, with_compound_models, widths_from_regions, classify, interaction_polynomial, size_convergence
    from ftphase.diagram import scan, plot_tx, write_records, invariants
    c = CFG[system]; out = os.path.join(HERE, "out", system); tab = FreeEnergyTable.from_tsv(c["table"]); df = tab.df; models, info = {}, {}
    keep = []; keep_T = {}
    for name in c["compounds"]:
        r = json.load(open(os.path.join(out, f"defects_{name}.json"))); x0 = r["x0"]; sizes = sorted(int(k) for k, v in r["sizes"].items() if v.get("done")); N = sizes[-1]; big = r["sizes"][str(N)]; T = np.array(big["T"])
        eps = {k: np.array(v["eps_T_eV"]) for k, v in big["defects"].items() if "eps_T_eV" in v}; w = {}; w3 = {}; ext = {}; inf = {"n_sites": N, "sizes": sizes, "defects_ok": sorted(eps), "defects_failed": sorted(k for k in big["defects"] if k not in eps)}
        iT = int(np.argmin(abs(T - c.get("T_conv", 1200.0 if T.max() > 1500 else 500.0))))
        if "A_on_B" in eps and "B_on_A" in eps:      # convergence with cell size: anti-site pair free energy at 1200 K
            pair = {n: r["sizes"][str(n)]["defects"]["A_on_B"]["eps_T_eV"][iT] + r["sizes"][str(n)]["defects"]["B_on_A"]["eps_T_eV"][iT] for n in sizes if all("eps_T_eV" in r["sizes"][str(n)]["defects"].get(q, {}) for q in ("A_on_B", "B_on_A"))}
            inf["antisite_pair_by_size_eV"] = {int(k): round(float(v), 3) for k, v in pair.items()}; inf["size_converged_0.02eV"] = size_convergence(pair, 0.02)[0] if len(pair) > 1 else None
        mu = r.get("multi", {}); half = 0.03; sd = mu.get("constitutional_defects")
        if sd:
            inf["constitutional_defects"] = sd; xs = []
            for side, dk in sd.items():
                cells = [v for v in mu["cells"].values() if v["side"] == side and "dG_T_eV" in v and v.get("n_imag", 0) == 0 and (kmax is None or v["k"] <= kmax)]
                inf[f"cells_{side}"] = f"{len(cells)}/{sum(1 for v in mu['cells'].values() if v['side'] == side)}"
                if len(cells) >= 6 and dk in eps:
                    kk = np.array([v["k"] for v in cells]); dG = np.array([v["dG_T_eV"] for v in cells]); ww = np.array([interaction_polynomial(dG[:, i], kk, eps[dk][i], N) for i in range(len(T))]); w[dk] = ww[:, 0]; w3[dk] = ww[:, 1]
                    ext[side] = min(max(abs(v["x"] - x0) for v in cells), 0.15); inf[f"k_max_{side}"] = int(kk.max())
                    inf[f"w_{dk}_at_T_eV"] = {int(t): round(float(np.interp(t, T, w[dk])), 2) for t in (c.get("T_report", (1000.0, 1400.0, 1800.0))[0], c.get("T_report", (1000.0, 1400.0, 1800.0))[-1])}; xs += [abs(v["x"] - x0) for v in cells]
        half = (ext.get("A_rich", 0.03), ext.get("B_rich", 0.03))            # window = the compositions sampled on each side
        models[name] = CompoundModel(name, x0, tuple(r["site_counts"]), T, eps, w, half_width=half, side_defects=sd, w3=w3); inf["window"] = [round(x0 - half[0], 3), round(x0 + half[1], 3)]; info[name] = inf
        keep.append(df[(df.phase == name) & np.isclose(df.x, x0, atol=2e-4)]); keep_T[name] = keep[-1].sort_values("T")
    d2 = pd.concat([df[~df.phase.isin(c["compounds"])]] + keep, ignore_index=True); ti = interpolate_T(FreeEnergyTable.from_dataframe(d2, tab.meta), c["T"])
    if (ti.df.phase == "liquid").any():
        cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["size"]); okT = cover[cover["size"] >= 3].index; ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(okT)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique())); full = with_compound_models(builder_from_table(ti, **c["kw"]), models); cache = {}

    # Compounds whose ordered state does not survive in the defect Monte Carlo (defect_ce_mc.py: `mc` gives no branch) are replaced by the
    # phase on their lattice in whatever state of order it takes (`lattice` step: G(x) at 3 temperatures, interpolated quadratically in T).
    lat = {}; alias = {}          # lattice=Al3Li:fcc -> the Al3Li lattice IS the fcc lattice: its curve is called fcc and competes with (replaces, where lower) the fcc solution of the table
    for name in (use_lattice or []):
        name, alias[name.split(":")[0]] = name.split(":")[0], name.split(":")[-1]
        d_ = os.path.join(out, f"ce_{name}"); fs = sorted(glob.glob(os.path.join(d_, "lattice_*.tsv")))
        if not fs:
            continue
        tb = [pd.read_csv(f_, sep="\t") for f_ in fs]; Tl = np.array([t_["T"].iloc[0] for t_ in tb]); o = np.argsort(Tl); tb = [tb[k_] for k_ in o]; Tl = Tl[o]
        dG = np.array([(t_.G - t_.G_perfect_compound).to_numpy() for t_ in tb]); lat[name] = (tb[0].x.to_numpy(), Tl, dG); info[name]["lattice_phase_T"] = [float(v) for v in Tl]; info[name]["lattice_phase_name"] = alias[name]; info[name]["lattice_x_range"] = [round(float(tb[0].x.min()), 3), round(float(tb[0].x.max()), 3)]
        info[name]["lattice_minus_perfect_at_x0_meV"] = [round(float(1000 * np.interp(models[name].x0, tb[0].x, r_)), 1) for r_ in dG]

    def builder(T):
        if T not in cache:
            ph = full(T)
            for name, (xl, Tl, dG) in lat.items():
                if Tl.min() - 1 <= T <= Tl.max() + 1:
                    from ftphase.equilibrium import PhaseCurve
                    g0 = float(np.interp(T, *[v_.to_numpy() for v_ in (keep_T[name]["T"], keep_T[name]["G"])])); dg = np.array([np.polyval(np.polyfit(Tl, dG[:, j_], min(2, len(Tl) - 1)), T) for j_ in range(len(xl))])
                    ph = [p_ for p_ in ph if p_.name != name] + [PhaseCurve.from_points(alias[name], xl, g0 + dg, fit="spline", limited=True, n_sample=401)]
            cache[T] = ph
        return cache[T]

    reg = scan(builder, Ts, min_width=0.002, gap_tol=2.5); reg = reg[reg.phase_a != reg.phase_b]
    write_records(os.path.join(out, "uniform_two_phase_regions.tsv"), reg, {"example": f"{system}: every compound by defect free energies (assemble.py)"})
    w = widths_from_regions(reg, models); w.to_csv(os.path.join(out, "uniform_widths.tsv"), sep="\t", index=False, float_format="%.4f"); cls = classify(w); invariants(reg).to_csv(os.path.join(out, "uniform_invariants.tsv"), sep="\t", index=False)
    ref = pd.read_csv(c["reference"], sep="\t", comment="#"); ref = ref[(ref.phase_a != ref.phase_b) & (ref["T"] >= Ts.min() - 1) & (ref["T"] <= Ts.max() + 1)]
    keys = sorted(set("+".join(sorted((a_, b_))) for d_ in (ref, reg) for a_, b_ in zip(d_.phase_a, d_.phase_b)))
    pal = ["#b0b0b0", "#f4a259", "#5b9bd5", "#a05195", "#70ad47", "#d45087", "#8dd3c7", "#ffa600", "#bc80bd", "#fb8072", "#665191", "#b3de69", "#80b1d3", "#fdb462", "#bebada", "#ccebc5"]; COL = {}
    for n_, k_ in enumerate(keys):
        a_, b_ = k_.split("+"); COL[f"{a_}+{b_}"] = COL[f"{b_}+{a_}"] = pal[n_ % len(pal)]
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6), sharey=True)
    plot_tx(ref, xlabel=c["xlabel"], dT=10, ax=axes[0], colors=COL); axes[0].set_title(c["reference_label"], fontsize=8.5)
    plot_tx(reg, xlabel=c["xlabel"], dT=float(np.diff(Ts).min()), ax=axes[1], colors=COL); axes[1].set_title("same solutions and liquid; every compound by defect free energies ε$_d$(T) + interaction, kind read from the hull", fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(out, "uniform_diagram.png"), dpi=140)
    L = [f"# {system}: uniform compound procedure", "", f"Classification read from the hull: {cls}", "", "## Width of each compound (x of the second element; '*' = at the edge of the window)", "",
         "| T (K) | " + " | ".join(c["compounds"]) + " |", "|---|" + "---|" * len(c["compounds"])]
    for T in sorted(w["T"].unique())[::5]:
        g = w[np.isclose(w["T"], T)].set_index("phase"); L.append(f"| {T:.0f} | " + " | ".join("—" if not g.loc[k, "stable"] else f"{g.loc[k, 'x_min']:.3f}–{g.loc[k, 'x_max']:.3f}" + ("*" if g.loc[k, "at_window_edge"] else "") for k in c["compounds"]) + " |")
    top = {k: (float(w[(w.phase == k) & w.stable]["T"].max()) if w[w.phase == k].stable.any() else None) for k in c["compounds"]}
    L += ["", f"Highest temperature on the hull: {top}", "", "## Inputs per compound", ""] + [f"* {k}: {json.dumps(v)}" for k, v in info.items()]
    from ftphase.compounds import window_extensions
    need = window_extensions(w, models); L += ["", f"Sides at the edge of the sampled window (to be extended with more defects per cell): {need}"]
    json.dump({"extend": need, "k_max": {k: {sd_: v.get(f"k_max_{sd_}") for sd_ in ("A_rich", "B_rich")} for k, v in info.items()}}, open(os.path.join(out, "extend.json"), "w"), indent=1)
    open(os.path.join(out, "REPORT.md"), "w").write("\n".join(L) + "\n")
    if not quiet:
        print("\n".join(L))
    return need


if __name__ == "__main__":
    main(sys.argv[1], use_lattice=next((v.split("=")[1].split(",") for v in sys.argv[2:] if v.startswith("lattice=")), None))   # lattice=Al3Li,Al2Li3: see `lat` in main
