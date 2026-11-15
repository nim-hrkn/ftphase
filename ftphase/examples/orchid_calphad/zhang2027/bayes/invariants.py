"""Invariant-reaction lines of every sampled phase diagram (the grey horizontal lines of Zhang et al. 2027 Fig. 4).

From the cached ensembles (out/<set>_raw.pkl): in each temperature row the two-phase regions are listed along x; where the list
changes between two consecutive rows there is an invariant reaction, drawn as a horizontal segment over the compositions of the
regions that appear or disappear.  Writes out/<set>_invariants.npz (T, x_lo, x_hi per segment) and out/fig4_lines.png.
"""
import json, os, pickle
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

SRC = os.path.dirname(os.path.abspath(__file__)); HERE = os.environ.get("BAYES_DIR") or SRC; LABEL = os.environ.get("BAYES_LABEL", "eSEN TDB of Zhang et al. 2027"); OUT = os.path.join(HERE, "out"); T0, DT = 500.0, 25.0


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


PRETTY = {"RU2SI": "Ru$_2$Si", "SI3RU5": "Ru$_5$Si$_3$", "RU4SI3": "Ru$_4$Si$_3$", "RUSI": "RuSi", "RU2SI3": "Ru$_2$Si$_3$", "SIRU5": "Ru$_5$Si", "SIRU4": "Ru$_4$Si",
          "SIRU3": "Ru$_3$Si", "SI3RU": "RuSi$_3$", "HCP": "hcp", "LIQUID": "liquid", "SI": "Si"}
XCOMP = {"RU2SI": 1 / 3, "SI3RU5": 3 / 8, "RU4SI3": 3 / 7, "RUSI": 0.5, "RU2SI3": 0.6, "SIRU5": 1 / 6, "SIRU4": 0.2, "SIRU3": 0.25, "SI3RU": 0.75, "SI": 1.0}


def reference_sets(name):
    """Phase sets on the (T, x) grid of the panel's reference diagram: point estimate (prior) or posterior-mean parameters."""
    import posterior as P
    P.TEXT = open(os.path.join(HERE, "rusi-start.tdb")).read(); pr = json.load(open(os.path.join(HERE, "prior.json"))); P.SYMS = pr["symbols"]
    S = json.load(open(os.path.join(OUT, "summary.json")))
    theta = np.zeros(len(P.SYMS)) if name == "prior" else np.array([v for p in S["parameters"] for v in (p["dH_post_mean_std_J"][0], p["dS_post_mean_std_J_K"][0])])
    return P.run_one((0, theta))[1]


def label_regions(ax, name, p_any):
    """Names of the phases and phase fields.  Compound names at the top (grey = stable somewhere in < 5 % of the samples); field names
    are those of the reference diagram of the panel (prior: point estimate; posterior: posterior-mean parameters), placed at the
    centre of each field; in individual samples the fields differ, which is what the figure shows."""
    box = dict(fc="w", ec="none", alpha=0.75, pad=0.6); sets = reference_sets(name); nT, nx = len(sets), len(sets[0])
    for ph, x in XCOMP.items():
        if ph == "SI" or ph not in p_any:
            continue
        rare = p_any[ph] < 0.05
        ax.text(x, 2575, PRETTY[ph] + (" (rare)" if rare else ""), fontsize=5.5 if rare else 6.5, rotation=90, ha="center", va="top", color="0.35" if rare else "k", bbox=box)
    ax.text(0.995, 1730, "Si", fontsize=7, ha="right", va="bottom", bbox=box)
    cells = {}
    for i in range(nT):
        for j in range(nx):
            cells.setdefault(sets[i][j], []).append((T0 + DT * i, 0.01 * j))
    stable = sorted({p for s_ in cells for p in s_})
    for s_, c in cells.items():
        c = np.array(c); T, x = c[:, 0], c[:, 1]
        if len(s_) == 1:
            (p,) = s_
            if p == "LIQUID":
                m = x > 0.6; ax.text(0.80, np.percentile(T[m], 80) if m.any() else 2350, "liquid", fontsize=8, ha="center", bbox=box)
            elif p == "HCP":
                k = int(np.argmin(abs(T - 1450))); ax.annotate("hcp (Ru)", (x[T == T[k]].mean(), T[k]), xytext=(0.105, 1485), fontsize=7, va="center", bbox=box, arrowprops=dict(arrowstyle="-", lw=0.5, color="0.3"))
            continue
        if len(s_) != 2 or len(c) < 60:
            continue
        a, b = sorted(s_, key=lambda p: {"HCP": 0.0, "LIQUID": 0.5}.get(p, XCOMP.get(p, 0.5))); lab = f"{PRETTY.get(a, a)} + {PRETTY.get(b, b)}"
        Tm = np.median(T); xs = x[abs(T - T[np.argmin(abs(T - Tm))]) < 1]; xm = xs.mean(); w = xs.max() - xs.min()
        ax.text(xm, Tm, lab, fontsize=6.5 if w > 0.14 else 5.8, ha="center", va="center", rotation=0 if w > 0.14 else 90, bbox=box)
    return stable


def main():
    D = json.load(open(os.path.join(HERE, "datasets", "zpf_fig4b.json"))); S = json.load(open(os.path.join(OUT, "summary.json")))
    XS = {"RU2SI": 1 / 3, "RU4SI3": 3 / 7, "RUSI": 0.5}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True); stats = {}
    for ax, name, title in zip(axes, ("prior", "posterior"), ("(a) prior: UMLIP uncertainty only", "(b) posterior: + 3 tie-lines (1250, 1550, 1900 K)")):
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
        stats[name]["reference_diagram_phases"] = label_regions(ax, name, S[name]["P_stable_anywhere"])
        ax.set(xlim=(0, 1), ylim=(500, 2600), xlabel="x(Si)", title=title); ax.title.set_fontsize(9)
    axes[0].set_ylabel("T (K)")
    fig.suptitle(f"Ru-Si ({LABEL}), 1000 samples each: phase boundaries (blue) and invariant-reaction lines (grey)", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_lines.png"), dpi=170)
    S["invariant_lines"] = stats; json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1); print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
