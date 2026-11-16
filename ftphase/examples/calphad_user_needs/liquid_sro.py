"""Is there chemical short-range order in the liquid?  Thermodynamic test on the ACE Al-Li liquid of example 6.

Bhatia-Thornton: the long-wavelength limit of the concentration-concentration structure factor is
    S_cc(0) = k_B T / (d2G/dx2)          (G per atom),
and an ideal (random) mixture has S_cc(0) = x (1 - x).  S_cc(0) / [x(1-x)] < 1 means the liquid prefers unlike neighbours
(compound-forming, associates); > 1 means clustering (tendency to demix).  d2G/dx2 is taken from the fitted liquid G(x, T)
(calphy thermodynamic integration at 11 compositions, ideal mixing + 4-term Redlich-Kister fit).
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/liquid_sro.py   -> out/4_liquid_scc.png, out/4_liquid_scc.json
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
KB = 8.617333262e-5


def main():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from demo import table, grid_table, make_builder, OUT
    tab = table(); res = {}; fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0)); xs = np.linspace(0.05, 0.95, 181); h = 0.01
    for T, c in ((700.0, "#1f77b4"), (900.0, "#ff7f0e"), (1100.0, "#2ca02c")):
        ti = grid_table(tab, np.array([T])); p = next(q for q in make_builder(ti)(T) if q.name == "liquid")
        d2 = (p.g(xs + h) - 2 * p.g(xs) + p.g(xs - h)) / h ** 2; scc = KB * T / d2; ratio = scc / (xs * (1 - xs))
        gx = (p.g(xs) - ((1 - xs) * p.g(np.array([0.0]))[0] + xs * p.g(np.array([1.0]))[0]) + KB * T * -(xs * np.log(xs) + (1 - xs) * np.log(1 - xs))) * 1000   # excess over ideal mixing, meV
        i = int(np.argmin(ratio)); res[int(T)] = {"min_Scc_ratio": round(float(ratio[i]), 3), "x_at_min": round(float(xs[i]), 3), "ratio_at_x": {f"{x:.1f}": round(float(np.interp(x, xs, ratio)), 3) for x in (0.1, 0.25, 0.5, 0.6, 0.75, 0.9)},
                       "excess_G_min_meV": round(float(gx.min()), 1), "x_at_excess_min": round(float(xs[int(np.argmin(gx))]), 3)}
        axes[0].plot(xs, ratio, color=c, lw=1.8, label=f"{T:.0f} K"); axes[1].plot(xs, gx, color=c, lw=1.8, label=f"{T:.0f} K")
    axes[0].axhline(1.0, color="k", lw=0.8, ls="--"); axes[0].text(0.06, 1.03, "ideal (random) mixture", fontsize=8)
    axes[0].set(xlabel="x_Li", ylabel="S_cc(0) / [x (1 - x)]", ylim=(0, 1.3), title="ACE Al-Li liquid: < 1 = unlike neighbours preferred (ordering)"); axes[0].legend(fontsize=8); axes[0].title.set_fontsize(9)
    axes[1].axhline(0, color="k", lw=0.6); axes[1].set(xlabel="x_Li", ylabel="excess G of mixing (meV/atom)", title="excess over ideal mixing (from the same fit)"); axes[1].legend(fontsize=8); axes[1].title.set_fontsize(9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "4_liquid_scc.png"), dpi=150); json.dump(res, open(os.path.join(OUT, "4_liquid_scc.json"), "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
