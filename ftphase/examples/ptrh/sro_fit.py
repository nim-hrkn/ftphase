"""Fit the short-range-order free energy of the fcc solution (sro_free_energy.py -> out_ce_<mlip>/sro.tsv) to a Redlich-Kister form
that a TDB can carry:      dF_sro(x, T) = x (1 - x) sum_k (1 - 2x)^k (c_k / T + d_k / T^2),  k = 0..3     (eV/atom; x = x_Rh)
(the high-temperature expansion of the configurational free energy starts with -Var(E) / (2 k_B T)).  Only the disordered state is
fitted: for each composition the rows above 1.15 x the temperature of its heat-capacity peak (order-disorder transition of the MC cell)
and with Cv < 0.3 k_B.     env/ftphase/bin/python sro_fit.py --mlip mace-mpa-0   -> out_ce_<mlip>/sro_fit.json, sro_fit.png
"""
import argparse, json, os
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); EV = 96485.33212


def basis(x, T, kmax=3):
    return np.array([x * (1 - x) * (1 - 2 * x) ** k * f for k in range(kmax + 1) for f in (1.0 / T, 1.0 / T ** 2)]).T


def sro(x, T, coef):
    x = np.asarray(x, float); T = np.asarray(T, float) * np.ones_like(x)
    return basis(x, T, len(coef) // 2 - 1) @ np.asarray(coef)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mlip", required=True); ap.add_argument("--T-max", type=float, default=2500.0); a = ap.parse_args()
    out = os.path.join(HERE, f"out_ce_{a.mlip}"); d = pd.read_csv(os.path.join(out, "sro.tsv"), sep="\t"); keep = []; tc = {}
    for x, g in d.groupby("x"):
        g = g.sort_values("T"); pk = g.loc[g.Cv_kB.idxmax()]; t_c = float(pk["T"]) if pk.Cv_kB > 0.3 else 0.0; tc[round(float(x), 3)] = t_c
        keep.append(g[(g["T"] > max(1.15 * t_c, 0)) & (g.Cv_kB < 0.3) & (g["T"] <= a.T_max)])
    f = pd.concat(keep); A = basis(f.x.to_numpy(), f["T"].to_numpy()); w = 1.0 / np.maximum(np.abs(f.dF_sro.to_numpy()), 2e-4)      # relative weight: the low-T rows matter
    coef, *_ = np.linalg.lstsq(A * w[:, None], f.dF_sro.to_numpy() * w, rcond=None); res = A @ coef - f.dF_sro.to_numpy()
    info = {"mlip": a.mlip, "form": "dF_sro = x(1-x) sum_k (1-2x)^k (c_k/T + d_k/T^2), eV/atom, x = x_Rh", "coef_eV": [float(c) for c in coef],
            "RK_J_per_mol": [{"k": k, "c_J_K": float(coef[2 * k] * EV * (-1) ** k), "d_J_K2": float(coef[2 * k + 1] * EV * (-1) ** k)} for k in range(4)],      # TDB order (PT,RH): (x_Pt - x_Rh)^k = (1 - 2x)^k -> same sign; kept explicit
            "rms_meV": float(np.sqrt(np.mean(res ** 2)) * 1000), "max_abs_meV": float(np.abs(res).max() * 1000), "n_rows": int(len(f)), "T_c_MC_K": tc,
            "T_range_fit_K": [float(f["T"].min()), float(f["T"].max())]}
    for r in info["RK_J_per_mol"]:
        r["c_J_K"] = float(coef[2 * r["k"]] * EV); r["d_J_K2"] = float(coef[2 * r["k"] + 1] * EV)
    json.dump(info, open(os.path.join(out, "sro_fit.json"), "w"), indent=1)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4)); xs = np.linspace(0, 1, 201)
    for T, c in ((1000, "#d62728"), (500, "#ff7f0e"), (300, "#2ca02c"), (200, "#1f77b4")):
        g = d.iloc[[(gg["T"] - T).abs().idxmin() for _, gg in d.groupby("x")]]; ax[0].plot(g.x, g.dF_sro * 1000, "o", color=c, ms=4); ax[0].plot(xs, sro(xs, float(g["T"].iloc[0]), coef) * 1000, "-", color=c, label=f"{g['T'].iloc[0]:.0f} K")
    ax[0].set(xlabel="x_Rh", ylabel="ΔF_SRO = F_conf − (E_random − T S_ideal)  (meV/atom)", title=f"{a.mlip}: SRO lowering of fcc G (dots MC, lines fit)"); ax[0].legend(fontsize=8)
    for x, c in ((0.25, "#2ca02c"), (0.5, "#d62728"), (0.75, "#1f77b4")):
        g = d[np.isclose(d.x, x, atol=0.003)].sort_values("T"); ax[1].plot(g["T"], g.dF_sro * 1000, "o", color=c, ms=3, label=f"x_Rh = {x}"); tt = np.linspace(100, 1000, 200); ax[1].plot(tt, sro(np.full_like(tt, x), tt, coef) * 1000, "-", color=c, lw=1)
        ax[2].plot(g["T"], g.alpha1, "o-", color=c, ms=3, label=f"x_Rh = {x}"); ax[1].axvline(tc.get(x, 0), color=c, lw=0.6, ls=":")
    ax[1].set(xlim=(90, 1000), ylim=(-6, 0.2), xlabel="T (K)", ylabel="ΔF_SRO (meV/atom)", title="dotted: order-disorder T of the MC cell; lines: fit above it"); ax[1].legend(fontsize=8)
    ax[2].set(xlim=(90, 1000), xlabel="T (K)", ylabel="Warren-Cowley α₁ (first shell)", title="short-range order parameter"); ax[2].legend(fontsize=8)
    for q in ax: q.title.set_fontsize(8.5)
    fig.tight_layout(); fig.savefig(os.path.join(out, "sro_fit.png"), dpi=140); print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
