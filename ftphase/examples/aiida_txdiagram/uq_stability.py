"""Stage-07 additions after Zhang et al. 2027, applied to the Al-Li runs (2026-11-12).

    uq_stability.py accuracy                      phase-label accuracy of every Al-Li run against the SGTE assessment AlLi-20Lon
    uq_stability.py uq out/alli_ace_m6 [--n 200]  stability-probability maps with the MLIP-level prior (dH 1.41 kJ/mol, dS 1.73 J/mol/K per phase)

accuracy: the run's phase set on a (T, x) grid is read from 07_two_phase_regions.tsv (+ lowT/ + <run>_liside_solid/ as in
sgte_diagrams.draw_run) by ftphase.diagram.phase_sets, the reference from the ORCHID-Diagrams boundaries; grid 300 K .. top of the
run's liquid window, x 0..1; the region x > 0.5 above the bottom of the liquid window, and every x > 0.5 point where the reference has liquid, is masked (no Li-side liquid was computed).
uq: the diagram is re-assembled from 05_free_energies.tsv with the WorkChain's own spec (fits, entropy models, hull settings) and
ftphase.diagram.sensitivity(sigma_H, sigma_S) draws one dH - T dS offset per phase and sample (rigid shift of each phase's curve:
coarser than Zhang's per-end-member perturbation, which a table of cells without CALPHAD parameters does not offer).
"""
import argparse, json, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
sys.path.insert(0, os.path.join(HERE, "..", "orchid_calphad")); sys.path.insert(0, HERE)
RENAME = {"FCC_A1": "fcc", "FCC_4SL": "fcc", "BCC_4SL": "B32", "LIQUID": "liquid", "AL2LI3": "Al2Li3", "AL4LI9": "Al4Li9", "BCC_A2": "bcc"}


def reference_regions(ref, Ts):
    """ORCHID-Diagrams boundary pairs -> regions table on the temperature grid."""
    rows = []
    for reg in ref.get("regions") or []:
        if len(reg) != 2:
            continue
        a, b = reg; n = min(len(a["T"]), len(b["T"])); Ta = np.array(a["T"][:n]); xa = np.array(a["x"][:n]); xb = np.array(b["x"][:n])
        o = np.argsort(Ta); Ta, xa, xb = Ta[o], xa[o], xb[o]
        for T in Ts:
            if Ta[0] - 1e-6 <= T <= Ta[-1] + 1e-6:
                rows.append({"T": float(T), "phase_a": a["phase"].split("#")[0], "x_a": float(np.interp(T, Ta, xa)), "phase_b": b["phase"].split("#")[0], "x_b": float(np.interp(T, Ta, xb))})
    return pd.DataFrame(rows)


def run_regions(run_dir):
    r = pd.read_csv(os.path.join(run_dir, "07_two_phase_regions.tsv"), sep="\t"); T_liq = float(r["T"].min())
    low = os.path.join(run_dir, "lowT", "07_two_phase_regions.tsv")
    if os.path.exists(low):
        lr = pd.read_csv(low, sep="\t"); r = pd.concat([lr[lr["T"] < T_liq - 1e-6], r], ignore_index=True)
    lis = os.path.join(run_dir.rstrip("/") + "_liside_solid", "07_two_phase_regions.tsv")
    if os.path.exists(lis):
        ls = pd.read_csv(lis, sep="\t"); r = pd.concat([ls[(ls["T"] < T_liq - 1e-6) & (ls[["x_a", "x_b"]].min(axis=1) >= 0.45)], r], ignore_index=True)
    return r, T_liq


def accuracy():
    from ftphase.diagram import phase_sets, phase_label_accuracy
    from sgte_diagrams import SYSTEMS, load_sgte
    S = SYSTEMS["alli"]; ref = next(d for d in load_sgte(S["prefix"]) if d["name"] == S["ref"])
    xs = np.linspace(0.005, 0.995, 100); rows = []
    for label, d in S["runs"]:
        if not os.path.exists(os.path.join(d, "07_two_phase_regions.tsv")) or "example 6" in label:
            continue
        reg, T_liq = run_regions(d); T_top = float(reg["T"].max()); Ts = np.arange(300.0, T_top + 1e-6, 10.0)
        a = phase_sets(reg, Ts, xs); b = phase_sets(reference_regions(ref, Ts), Ts, xs)
        TT, XX = np.meshgrid(Ts, xs, indexing="ij")
        has_li = os.path.exists(d.rstrip("/") + "_liside_solid")
        ref_liq = np.array([["LIQUID" in q for q in row] for row in b])
        mask = ~((XX > 0.5) & (TT >= T_liq - 1e-6)) & (has_li | (XX <= 0.5)) & ~((XX > 0.5) & ref_liq)   # no Li-side liquid in any run: reference-liquid points there are left out
        res = {"run": label, "T_top": T_top, "all": phase_label_accuracy(a, b, rename_b=RENAME, mask=mask),
               "Al side 700 K+": phase_label_accuracy(a, b, rename_b=RENAME, mask=mask & (XX <= 0.5) & (TT >= T_liq)),
               "solids < 700 K": phase_label_accuracy(a, b, rename_b=RENAME, mask=mask & (TT < T_liq)), "n": int(mask.sum())}
        rows.append(res); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}, flush=True)
    df = pd.DataFrame(rows); os.makedirs(os.path.join(OUT, "uq"), exist_ok=True); df.to_csv(os.path.join(OUT, "uq", "label_accuracy_alli.tsv"), sep="\t", index=False)
    L = ["# Al-Li: phase-label accuracy of each run against SGTE AlLi-20Lon (grid 10 K x 100 compositions, 300 K .. top of the run's window)", "",
         "| run | all (masked: x > 0.5 above the liquid window) | Al side, liquid window | solids below the liquid window |", "|---|---|---|---|"]
    L += [f"| {r['run']} | {r['all']:.3f} | {r['Al side 700 K+']:.3f} | {r['solids < 700 K']:.3f} |" for r in rows]
    open(os.path.join(OUT, "uq", "label_accuracy_alli.md"), "w").write("\n".join(L) + "\n")


def builder_of(run):
    """The WorkChain's builder(T, offsets, slopes) rebuilt from the run's table and spec."""
    from aiida import load_profile, orm
    load_profile("ftphase")
    from ftphase.assemble import builder_from_table, interpolate_T
    from ftphase.records import FreeEnergyTable
    from ftphase.aiida.functions import _site_model
    asm = orm.load_node(json.load(open(os.path.abspath(run) + ".pk.json"))["pk"]).inputs.spec.get_dict().get("assemble", {})
    tab = FreeEnergyTable.from_tsv(os.path.join(run, "05_free_energies.tsv")); phases = set(tab.df.phase)
    return tab, asm, phases, builder_from_table, interpolate_T, _site_model


def uq(run, n, dT, sigma_stat):
    import matplotlib; matplotlib.use("Agg")
    from ftphase.diagram import scan, sensitivity, stability_probability, plot_stability, phase_sets, ZHANG_SIGMA_H, ZHANG_SIGMA_S
    from ftphase.records import FreeEnergyTable
    tab, asm, phases, builder_from_table, interpolate_T, _site_model = builder_of(run)
    Ts = np.arange(float(asm.get("T_min", 700.0)), float(asm.get("T_max", 1100.0)) + 1e-6, dT)
    ti = interpolate_T(tab, Ts)
    cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].size(); Ts = np.array(sorted(cover[cover >= 3].index))
    ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(Ts)], ti.meta)

    def _sm(name):
        k, _, st = name.partition("@"); return _site_model(k, float(st) if st else None)
    ent = {ph: (_sm(v[0]), float(v[1])) for ph, v in asm.get("entropy_models", {}).items() if ph in phases}
    hull_kw = asm.get("hull", {"min_width": 0.005, "gap_tol": 2.5})
    builder = builder_from_table(ti, fit=asm.get("fit", "spline"), fits=asm.get("fits", {}), poly_order=int(asm.get("poly_order", 3)), poly_orders=asm.get("poly_orders", {}), entropy_models=ent or None)
    xs = np.linspace(0.005, float(ti.df[ti.df.phase == "liquid"]["x"].max()) - 0.005, 80)
    base = scan(builder, Ts, **hull_kw); ref = phase_sets(base, Ts, xs)
    sens = sensitivity(builder, Ts, {p: sigma_stat for p in phases}, n_samples=n, rng=0, sigma_H=ZHANG_SIGMA_H, sigma_S=ZHANG_SIGMA_S, **hull_kw)
    pr = stability_probability(sens.samples, Ts, xs, reference=ref)
    name = os.path.basename(os.path.normpath(run)); out = os.path.join(OUT, "uq", name); os.makedirs(out, exist_ok=True)
    fig = plot_stability(pr, xlabel=asm.get("xlabel", "x_Li")); fig.suptitle(f"{name}: P(phase present), {n} samples, per-phase dH ~ N(0, 1.41 kJ/mol), dS ~ N(0, 1.73 J/mol/K)", fontsize=9)
    fig.savefig(os.path.join(out, "stability_probability.png"), dpi=130, bbox_inches="tight")
    np.savez_compressed(os.path.join(out, "pmaps.npz"), T=Ts, x=xs, **pr.maps)
    # eutectic-like invariant: lowest T with liquid present, per sample
    T_liq = [float(s[(s.phase_a == "liquid") | (s.phase_b == "liquid")]["T"].min()) if ((s.phase_a == "liquid") | (s.phase_b == "liquid")).any() else float("nan") for s in sens.samples]
    b_liq = base[(base.phase_a == "liquid") | (base.phase_b == "liquid")]["T"].min()
    summ = {"run": name, "n_samples": n, "T_grid": [float(Ts[0]), float(Ts[-1]), float(dT)], "sigma_H_eV": ZHANG_SIGMA_H, "sigma_S_eV_K": ZHANG_SIGMA_S, "sigma_stat_eV": sigma_stat,
            "P_anywhere": pr.anywhere, "accuracy_vs_unperturbed_mean": float(np.mean(pr.agreement)), "accuracy_p05_p95": [float(np.percentile(pr.agreement, 5)), float(np.percentile(pr.agreement, 95))],
            "lowest_T_with_liquid_unperturbed": float(b_liq), "lowest_T_with_liquid_mean_std": [float(np.nanmean(T_liq)), float(np.nanstd(T_liq))],
            "lowest_T_with_liquid_p05_p95": [float(np.nanpercentile(T_liq, 5)), float(np.nanpercentile(T_liq, 95))], "fraction_at_grid_floor": float(np.mean(np.isclose(T_liq, Ts[0])))}
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1); print(json.dumps(summ, indent=0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["accuracy", "uq"]); ap.add_argument("runs", nargs="*"); ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--dT", type=float, default=20.0); ap.add_argument("--sigma-stat", type=float, default=0.0); a = ap.parse_args()
    if a.cmd == "accuracy":
        accuracy()
    else:
        for r in a.runs:
            uq(r, a.n, a.dT, a.sigma_stat)
