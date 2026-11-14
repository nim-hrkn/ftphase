"""Figure for the Ru-Si Bayesian update: prior ensemble (Fig. 4a) | posterior ensemble (Fig. 4b)."""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
S = json.load(open(os.path.join(OUT, "summary.json"))); P = np.load(os.path.join(OUT, "points.npz"))
D = json.load(open(os.path.join(HERE, "datasets", "zpf_fig4b.json")))
LAB = {"RU2SI": "Ru$_2$Si", "SI3RU5": "Ru$_5$Si$_3$", "RU4SI3": "Ru$_4$Si$_3$", "RUSI": "RuSi", "RU2SI3": "Ru$_2$Si$_3$", "SIRU5": "Ru$_5$Si", "SIRU3": "Ru$_3$Si", "SIRU4": "Ru$_4$Si", "SI3RU": "RuSi$_3$"}
XS = {"RU2SI": 1 / 3, "SI3RU5": 3 / 8, "RU4SI3": 3 / 7, "RUSI": 0.5, "RU2SI3": 0.6, "SIRU5": 1 / 6, "SIRU3": 0.25, "SIRU4": 0.2, "SI3RU": 0.75}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, name, title in zip(axes, ("prior", "posterior"), ("(a) prior: UMLIP (eSEN) uncertainty only", "(b) posterior: + 3 tie-lines (1250, 1550, 1900 K)")):
    pts = np.load(os.path.join(OUT, f"{name}.npz"))["pts"]; n = S[name]["n"]
    ax.scatter(pts[:, 1], pts[:, 0], s=1.0, c="#1f4e8c", alpha=min(1.0, 40.0 / n), linewidths=0, rasterized=True)
    ref = P["point_mlip" if name == "prior" else "point_posterior_mean"]
    ax.scatter(ref[:, 1], ref[:, 0], s=2.5, c="#e8c100", linewidths=0, rasterized=True, label="eSEN point estimate" if name == "prior" else "posterior-mean parameters")
    pr = S[name]["P_stable_anywhere"]
    txt = "\n".join(f"{LAB[p]}: {pr.get(p, 0):.2f}" for p in ("RU2SI", "SI3RU5", "RU4SI3", "RUSI", "SIRU5", "SIRU3", "SIRU4", "SI3RU"))
    ax.text(0.985, 0.03, "P(stable somewhere)\n" + txt, transform=ax.transAxes, fontsize=7, ha="right", va="bottom", bbox=dict(fc="w", ec="0.7", lw=0.5))
    if name == "posterior":
        for T, region in zip(D["conditions"]["T"], D["values"]):
            xs = [XS.get(v[0], v[2][0]) for v in region if v[0] != "__HYPERPLANE__"]
            ax.plot(xs, [T, T], "-", c="k", lw=0.8); ax.plot(xs, [T, T], "o", mfc="none", mec="r", ms=6, mew=1.2)
    ax.set(xlim=(0, 1), ylim=(500, 2600), xlabel="x(Si)", title=title); ax.title.set_fontsize(9); ax.legend(fontsize=7, loc="upper right")
axes[0].set_ylabel("T (K)")
fig.suptitle("Ru-Si, eSEN TDB of Zhang et al. 2027: 1000 parameter samples each; dH ~ N(0, 1.41 kJ/mol), dS ~ N(0, 1.73 J/mol/K) per mole of atoms; ESPEI MCMC", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4.png"), dpi=170); print("->", os.path.join(OUT, "fig4.png"))
