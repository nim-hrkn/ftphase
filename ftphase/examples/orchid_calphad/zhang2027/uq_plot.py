"""Fig. 4a-style plot from a uq.py output folder (pmaps.npz + summary.json): solution phases as P(present) >= 0.5 regions with the 0.1 /
0.9 probability contours, stoichiometric compounds as vertical bars coloured by P(present at T); labels = P(stable anywhere).
    python uq_plot.py <uq folder> [--out <png>]
"""
import argparse, json, os, re
import numpy as np


def compound_x(tdb_text, xel):
    """x(xel) of every stoichiometric phase from its PHASE site counts and CONSTITUENT species."""
    sites = {m.group(1).upper(): [float(v) for v in m.group(3).split()] for m in re.finditer(r"^\s*PHASE\s+(\w+)\s+%\s+(\d+)\s+([\d.\s]+)!", tdb_text, re.M)}
    out = {}
    for m in re.finditer(r"^\s*CONSTITUENT\s+(\w+)\s*:(.*?):\s*!", tdb_text, re.M):
        ph = m.group(1).upper(); subs = [t.strip() for t in m.group(2).split(":")]
        if ph not in sites or any("," in t for t in subs):
            continue
        n = sum(sites[ph]); out[ph] = sum(c for c, t in zip(sites[ph], subs) if t.strip().upper() == xel) / n
    return out
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("folder"); ap.add_argument("--out", default=None); a = ap.parse_args()
    z = np.load(os.path.join(a.folder, "pmaps.npz")); summ = json.load(open(os.path.join(a.folder, "summary.json")))
    T, x = z["T"], z["x"]; phases = [k for k in z.files if k not in ("T", "x")]; P = summ["P_stable_anywhere"]
    nT, nx = z[phases[0]].shape; T = T[:nT]; x = x[:nx]; xel = summ["grid"][0].upper()
    xcomp = compound_x(open(summ["tdb"]).read(), xel) if os.path.exists(summ["tdb"]) else {}
    fig, ax = plt.subplots(figsize=(6.6, 4.8)); X, Y = np.meshgrid(x, T)
    sol = {"LIQUID": ("#fde0b0", "liquid"), "HCP": ("#cfe3f3", "hcp (Ru)"), "FCC": ("#d9f0d3", "fcc"), "BCC": ("#e6d8f0", "bcc"), "SI": ("#e0e0e0", "Si (diamond)")}
    for p in phases:
        if p not in sol:
            continue
        m = z[p]; c, lab = sol[p]
        ax.contourf(X, Y, m, levels=[0.5, 1.01], colors=[c]); ax.contour(X, Y, m, levels=[0.1, 0.9], colors=["0.55"], linewidths=[0.6, 0.6], linestyles=["--", "-"])
        if m.max() >= 0.5:
            i, j = np.unravel_index(np.argmax(m * (m >= 0.5) + 1e-3 * np.random.default_rng(0).random(m.shape)), m.shape); ax.text(x[j], T[i], lab, fontsize=7, ha="center", color="0.3")
    cmap = plt.get_cmap("Blues"); k = 0
    comps = [p for p in phases if p not in sol]
    for p in sorted(comps, key=lambda q: xcomp.get(q, float(np.argmax(z[q].max(axis=0))) * x[1])):
        m = z[p]; xc = xcomp.get(p, x[int(np.argmax(m.max(axis=0)))]); prob = m.max(axis=1)
        if m.max() <= 0 and p not in xcomp:
            continue   # P(phase present somewhere at T) = P(stable at T) for a point compound
        segs = [[(xc, T[i]), (xc, T[i + 1])] for i in range(nT - 1)]
        lc = LineCollection(segs, colors=cmap(0.15 + 0.85 * prob[:-1]), linewidths=4); ax.add_collection(lc)
        ax.text(xc, T[-1] - (0.04 + 0.055 * (k % 5)) * (T[-1] - T[0]), f"{p}\n{P.get(p, 0):.2f}", fontsize=6.5, ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="0.7", lw=0.5)); k += 1
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1)); cb = fig.colorbar(sm, ax=ax, pad=0.02); cb.set_label("P(compound present at T)", fontsize=8); cb.ax.tick_params(labelsize=7)
    ax.set(xlim=(0, 1), ylim=(T[0], T[-1]), xlabel=f"x_{xel.capitalize()}", ylabel="T (K)")
    ax.set_title(f"{os.path.basename(a.folder)}: {summ['n_samples']} samples, dH ~ N(0, {summ['sigma_H_J'] / 1000:.2f} kJ/mol), dS ~ N(0, {summ['sigma_S_J_K']} J/mol/K)\n"
                 "solutions: filled P >= 0.5, contours 0.1 (dashed) / 0.9; compounds: bars = P(stable at T), label = P(stable anywhere)", fontsize=7.5)
    fig.tight_layout(); out = a.out or os.path.join(a.folder, "uq_fig4a.png"); fig.savefig(out, dpi=150); print("wrote", out)


if __name__ == "__main__":
    main()
