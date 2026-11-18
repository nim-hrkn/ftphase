"""Pt-Rh order-disorder temperature against composition from CE + canonical MC (data: out_ce_<mlip>/sro.tsv of sro_free_energy.py,
2048 sites, 19 compositions, cooling from 4800 K on a grid uniform in 1/T).  Background: heat capacity C_v(x, T); points: its peak
(order-disorder transition of the cell) where it exceeds 0.3 k_B; markers: [Saengdeejing2026] Table 7 (PFP filled, DFT open).
    env/ftphase/bin/python ce_dome_figure.py   -> out/ce_dome.png, out/ce_dome.json"""
import json, os
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = [(0.25, 146, None, "Pt$_3$Rh"), (0.50, 258, 211, "PtRh"), (0.75, 235, 156, "PtRh$_3$")]
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True); out = {}
for ax, (mlip, label) in zip(axes, (("mace-mpa-0", "MACE-MPA-0"), ("sevenn-mf-ompa", "SevenNet-MF-ompa"))):
    d = pd.read_csv(os.path.join(HERE, f"out_ce_{mlip}", "sro.tsv"), sep="\t"); d = d[d["T"] <= 330]
    xs = np.array(sorted(d.x.unique())); Ts = np.array(sorted(d["T"].unique())); C = np.array([[float(d[(np.isclose(d.x, x)) & (np.isclose(d["T"], T))].Cv_kB.iloc[0]) for x in xs] for T in Ts])
    pm = ax.pcolormesh(xs, Ts, np.clip(C, 0, 2.0), shading="nearest", cmap="Greys", vmin=0, vmax=2.0); tc = []
    for x in xs:
        g = d[np.isclose(d.x, x)]; pk = g.loc[g.Cv_kB.idxmax()]
        tc.append((float(x), float(pk["T"]) if pk.Cv_kB > 0.3 else None, float(pk.Cv_kB)))
    xt = [a for a, b, _ in tc if b]; tt = [b for a, b, _ in tc if b]; ax.plot(xt, tt, "o-", color="#b00020", ms=6, lw=1.5, label="C$_v$ peak (CE + canonical MC, this work)")
    for a, b, _ in tc:
        if b is None:
            ax.annotate("", (a, 100), (a, 114), arrowprops=dict(arrowstyle="->", color="#b00020", lw=1.0))
    for k, (x, tp, td, nm) in enumerate(PAPER):
        ax.plot([x], [tp], "s", color="k", ms=8, label="[Saengdeejing2026] PFP" if k == 0 else None); ax.text(x + 0.015, tp, nm, fontsize=8, va="center")
        if td:
            ax.plot([x], [td], "s", mfc="none", color="k", ms=8, label="[Saengdeejing2026] DFT" if k == 1 else None)
    box = dict(fc="w", ec="none", alpha=0.8, pad=1.0)
    ax.text(0.5, 300, "fcc: disordered, with short-range order", ha="center", fontsize=9.5, bbox=box)
    ax.text(0.5, 118, "long-range order\n(below the C$_v$ peak)", ha="center", fontsize=9, bbox=box)
    ax.text(0.02, 124, "arrows: no peak\nabove 100 K", fontsize=7.5, color="#b00020", bbox=box)
    ax.set(xlim=(0, 1), ylim=(100, 330), xlabel="x_Rh", title=f"{label}: order-disorder temperature from the cluster expansion"); ax.title.set_fontsize(10); ax.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.0, 0.86))
    out[mlip] = {"T_c_K": {f"{a:.2f}": b for a, b, _ in tc}, "Cv_max_kB": {f"{a:.2f}": round(c, 2) for a, _, c in tc}, "T_c_max_K": max(tt), "x_at_max": xt[int(np.argmax(tt))]}
axes[0].set_ylabel("T (K)"); cb = fig.colorbar(pm, ax=axes, fraction=0.025, pad=0.02); cb.set_label("C$_v$ (k$_B$/atom, clipped at 2)")
fig.savefig(os.path.join(HERE, "out", "ce_dome.png"), dpi=140, bbox_inches="tight"); json.dump(out, open(os.path.join(HERE, "out", "ce_dome.json"), "w"), indent=1); print(json.dumps({k: (v["T_c_max_K"], v["x_at_max"]) for k, v in out.items()}))
