"""Invariant-reaction lines of every sampled phase diagram (the grey horizontal lines of Zhang et al. 2027 Fig. 4).

From the cached ensembles (out/<set>_raw.pkl): in each temperature row the two-phase regions are listed along x; where the list
changes between two consecutive rows there is an invariant reaction, drawn as a horizontal segment over the compositions of the
regions that appear or disappear.  Writes out/<set>_invariants.npz (T, x_lo, x_hi per segment) and out/fig4_lines.png.
"""
import json, os, pickle
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); T0, DT = 500.0, 25.0


def regions(sets_row, comp_row):
    """{phase pair: (x_lo, x_hi)} of the two-phase cells of one temperature row."""
    out = {}
    for s, comps in zip(sets_row, comp_row):
        if len(s) == 2 and len(comps) == 2:
            xs = sorted(c[0] for c in comps); a = out.get(s)
            out[s] = (min(xs[0], a[0]), max(xs[1], a[1])) if a else (xs[0], xs[1])
    return out


def sample_invariants(sets, pts):
    it = iter(pts); comp = []
    try:
        for row in sets:
            comp.append([[(q[1], q[2]) for q in (next(it) for _ in range(len(s)))] for s in row])
    except StopIteration:
        return [], None
    regs = [regions(r, c) for r, c in zip(sets, comp)]; segs = []
    for i in range(len(regs) - 1):
        changed = set(regs[i]) ^ set(regs[i + 1])
        if changed:
            xs = [x for k in changed for x in (regs[i].get(k) or regs[i + 1].get(k))]
            segs.append((T0 + DT * (i + 0.5), min(xs), max(xs)))
    return segs, regs


def boundary_lines(regs):
    """Polylines of the phase compositions bounding each two-phase region, one per (pair, side)."""
    lines = []
    for pair in {k for r in regs for k in r}:
        for side in (0, 1):
            cur = []
            for i, r in enumerate(regs):
                if pair in r:
                    cur.append((r[pair][side], T0 + DT * i))
                elif cur:
                    lines.append(cur); cur = []
            if cur:
                lines.append(cur)
    return [l for l in lines if len(l) > 1]


def label_regions(ax, name):
    """Names of the phases and phase fields.  Field names are those of the reference diagram of the panel (prior: eSEN point
    estimate; posterior: posterior-mean parameters); in individual samples the fields differ, which is what the figure shows."""
    box = dict(fc="w", ec="none", alpha=0.75, pad=0.6)
    for x, lab in ((1 / 3, "Ru$_2$Si"), (3 / 8, "Ru$_5$Si$_3$"), (3 / 7, "Ru$_4$Si$_3$"), (0.5, "RuSi"), (0.6, "Ru$_2$Si$_3$")):
        ax.text(x, 2560, lab, fontsize=6.5, rotation=90, ha="center", va="top", bbox=box)
        ax.plot([x, x], [2290, 2330], "-", c="0.3", lw=0.5)
    for x, lab in ((1 / 6, "Ru$_5$Si"), (0.2, "Ru$_4$Si"), (0.25, "Ru$_3$Si"), (0.75, "RuSi$_3$")):
        ax.text(x, 2560, lab + " (rare)", fontsize=5.5, rotation=90, ha="center", va="top", color="0.35", bbox=box)
    ax.text(0.995, 1730, "Si", fontsize=7, ha="right", va="bottom", bbox=box)
    ax.annotate("hcp (Ru)", (0.035, 1420), xytext=(0.105, 1485), fontsize=7, va="center", bbox=box, arrowprops=dict(arrowstyle="-", lw=0.5, color="0.3"))
    ax.text(0.80, 2330, "liquid", fontsize=8, ha="center", bbox=box)
    ax.text(0.15, 2130, "hcp + liquid", fontsize=7, ha="center", rotation=-52, bbox=box)
    ax.text(0.80, 1000, "Ru$_2$Si$_3$ + Si", fontsize=7, ha="center", bbox=box)
    ax.text(0.55, 1000, "RuSi + Ru$_2$Si$_3$", fontsize=6.5, ha="center", va="center", rotation=90, bbox=box)
    ax.text(0.465, 1000, "Ru$_4$Si$_3$ + RuSi", fontsize=6, ha="center", va="center", rotation=90, bbox=box)
    ax.text(0.70, 1790, "liquid + Ru$_2$Si$_3$", fontsize=6, ha="center", rotation=-38, bbox=box)
    if name == "prior":
        ax.text(0.22, 1050, "hcp + Ru$_4$Si$_3$", fontsize=7, ha="center", bbox=box)
    else:
        ax.text(0.19, 1050, "hcp + Ru$_4$Si$_3$", fontsize=7, ha="center", bbox=box)
        ax.text(0.19, 615, "hcp + RuSi", fontsize=7, ha="center", bbox=box)   # posterior mean: Ru4Si3 is stable only above 725 K
        ax.text(0.19, 1690, "hcp + Ru$_2$Si", fontsize=7, ha="center", bbox=box)


def main():
    D = json.load(open(os.path.join(HERE, "datasets", "zpf_fig4b.json"))); S = json.load(open(os.path.join(OUT, "summary.json")))
    XS = {"RU2SI": 1 / 3, "RU4SI3": 3 / 7, "RUSI": 0.5}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True); stats = {}
    for ax, name, title in zip(axes, ("prior", "posterior"), ("(a) prior: UMLIP (eSEN) uncertainty only", "(b) posterior: + 3 tie-lines (1250, 1550, 1900 K)")):
        res = pickle.load(open(os.path.join(OUT, f"{name}_raw.pkl"), "rb")); inv = []; bl = []; nbad = 0
        for _, sets, pts in res:
            segs, regs = sample_invariants(sets, pts)
            if regs is None:
                nbad += 1; continue
            inv += segs; bl += boundary_lines(regs)
        inv = np.array(inv); np.savez_compressed(os.path.join(OUT, f"{name}_invariants.npz"), inv=inv)
        n = len(res) - nbad; a = min(1.0, 12.0 / n)
        ax.add_collection(LineCollection([[(x0, T), (x1, T)] for T, x0, x1 in inv], colors="0.35", linewidths=0.5, alpha=a, rasterized=True))
        ax.add_collection(LineCollection(bl, colors="#1f4e8c", linewidths=0.6, alpha=min(1.0, 25.0 / n), rasterized=True))
        # invariants below 1800 K that reach the Ru-rich side (x_lo < 0.1): the grey band of the paper's figure
        ru = inv[(inv[:, 1] < 0.1) & (inv[:, 0] < 1800)]
        stats[name] = {"samples": n, "invariants_per_sample": len(inv) / n, "Ru_side_invariants_below_1800K_per_sample": len(ru) / n,
                       "their_T_percentiles_5_25_50_75_95": [float(v) for v in np.percentile(ru[:, 0], [5, 25, 50, 75, 95])] if len(ru) else None}
        if name == "posterior":
            for T, region in zip(D["conditions"]["T"], D["values"]):
                xs = [XS.get(v[0], v[2][0]) for v in region if v[0] != "__HYPERPLANE__"]
                ax.plot(xs, [T, T], "-", c="k", lw=0.8); ax.plot(xs, [T, T], "o", mfc="none", mec="r", ms=6, mew=1.2)
        label_regions(ax, name)
        ax.set(xlim=(0, 1), ylim=(500, 2600), xlabel="x(Si)", title=title); ax.title.set_fontsize(9)
    axes[0].set_ylabel("T (K)")
    fig.suptitle("Ru-Si (eSEN TDB of Zhang et al. 2027), 1000 samples each: phase boundaries (blue) and invariant-reaction lines (grey)", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_lines.png"), dpi=170)
    S["invariant_lines"] = stats; json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1); print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
